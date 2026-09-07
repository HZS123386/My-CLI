import pytest

from resume_cli.errors import AppError
from resume_cli.schemas import (
    parse_model_json,
    validate_resume_profile,
    validate_score_result,
)


def test_parse_model_json_accepts_code_fence() -> None:
    assert parse_model_json('```json\n{"name": "Alex"}\n```') == {"name": "Alex"}


def test_validate_resume_profile_keeps_required_shape() -> None:
    result = validate_resume_profile(
        {
            "name": "Alex",
            "phone": "",
            "email": "alex@example.com",
            "city": "Hangzhou",
            "education": [],
            "skills": ["TypeScript"],
        }
    )
    assert result["skills"] == ["TypeScript"]


def test_validate_score_result_rejects_out_of_range_score() -> None:
    with pytest.raises(AppError, match="0-100"):
        validate_score_result(
            {
                "overall_score": 101,
                "skill_score": 80,
                "experience_score": 70,
                "education_score": 80,
                "comment": "test",
                "interview_questions": [],
            }
        )
