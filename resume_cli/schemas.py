import json
import re
from typing import Any

from .errors import AppError


def _object(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AppError("AI_INVALID_JSON", f"{context}必须是 JSON 对象。")
    return value


def _string(value: Any, field: str) -> str:
    if not isinstance(value, str):
        raise AppError("AI_INVALID_JSON", f"AI 返回的 {field} 必须是字符串。")
    return value.strip()


def _string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise AppError("AI_INVALID_JSON", f"AI 返回的 {field} 必须是字符串数组。")
    return [item.strip() for item in value if item.strip()]


def _score(value: Any, field: str) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not 0 <= value <= 100
    ):
        raise AppError("AI_INVALID_JSON", f"AI 返回的 {field} 必须是 0-100 的数字。")
    return round(value)


def parse_model_json(raw: str) -> Any:
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip(), count=1, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as cause:
        raise AppError(
            "AI_INVALID_JSON", "AI 未返回有效 JSON，请重试或使用 --mock。", cause=cause
        ) from cause


def validate_resume_profile(value: Any) -> dict[str, Any]:
    data = _object(value, "AI 返回结果")
    education_source = data.get("education")
    if not isinstance(education_source, list):
        raise AppError("AI_INVALID_JSON", "AI 返回的 education 必须是数组。")

    education: list[dict[str, str]] = []
    for index, item in enumerate(education_source):
        item_data = _object(item, f"education[{index}]")
        education.append(
            {
                "school": _string(
                    item_data.get("school"), f"education[{index}].school"
                ),
                "major": _string(item_data.get("major"), f"education[{index}].major"),
                "degree": _string(
                    item_data.get("degree"), f"education[{index}].degree"
                ),
                "graduation_time": _string(
                    item_data.get("graduation_time"),
                    f"education[{index}].graduation_time",
                ),
            }
        )

    return {
        "name": _string(data.get("name"), "name"),
        "phone": _string(data.get("phone"), "phone"),
        "email": _string(data.get("email"), "email"),
        "city": _string(data.get("city"), "city"),
        "education": education,
        "skills": _string_list(data.get("skills"), "skills"),
    }


def validate_score_result(value: Any) -> dict[str, Any]:
    data = _object(value, "AI 返回结果")
    return {
        "overall_score": _score(data.get("overall_score"), "overall_score"),
        "skill_score": _score(data.get("skill_score"), "skill_score"),
        "experience_score": _score(data.get("experience_score"), "experience_score"),
        "education_score": _score(data.get("education_score"), "education_score"),
        "comment": _string(data.get("comment"), "comment"),
        "interview_questions": _string_list(
            data.get("interview_questions"), "interview_questions"
        ),
    }
