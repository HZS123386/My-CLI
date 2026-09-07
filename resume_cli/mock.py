import re
from typing import Any


KNOWN_SKILLS = [
    "TypeScript",
    "JavaScript",
    "React",
    "Node.js",
    "Next.js",
    "Python",
    "Go",
    "Java",
    "SQL",
    "PostgreSQL",
    "MySQL",
    "Redis",
    "Docker",
    "Kubernetes",
    "AWS",
    "Git",
    "REST API",
    "GraphQL",
]


def _capture(text: str, expression: str, flags: int = re.IGNORECASE) -> str:
    match = re.search(expression, text, flags)
    return match.group(1).strip() if match else ""


def _contains(text: str, word: str) -> bool:
    if word == "Go":
        return (
            re.search(r"\bGo\b", text) is not None
            or re.search(r"\bGolang\b", text, re.IGNORECASE) is not None
        )
    return re.search(rf"\b{re.escape(word)}\b", text, re.IGNORECASE) is not None


def _find_skills(text: str) -> list[str]:
    return [skill for skill in KNOWN_SKILLS if _contains(text, skill)]


def _find_education(text: str) -> list[dict[str, str]]:
    line = next(
        (
            item
            for item in text.splitlines()
            if re.search(r"university|college|大学|学院", item, re.IGNORECASE)
        ),
        "",
    )
    if not line:
        return []
    school = (
        _capture(line, r"([A-Za-z\s]+(?:University|College)|[^,，|]+(?:大学|学院))")
        or line.strip()
    )
    degree = _capture(
        line,
        r"(Ph\.?D\.?|M\.?S\.?|M\.Eng\.?|B\.?S\.?|B\.Eng\.?|Master(?:'s)?|Bachelor(?:'s)?|硕士|学士)",
    )
    major = _capture(
        line,
        r"(?:B\.?S\.?|B\.Eng\.?|M\.?S\.?|M\.Eng\.?|Master(?:'s)?|Bachelor(?:'s)?|硕士|学士)[,.\s|-]+([^,|\n]+?)(?:\s*[,|]\s*|$)",
    )
    graduation_time = _capture(line, r"((?:19|20)\d{2}(?:\s*[-–]\s*(?:19|20)\d{2})?)")
    return [
        {
            "school": school,
            "major": major,
            "degree": degree,
            "graduation_time": graduation_time,
        }
    ]


def extract_with_mock(resume_text: str) -> dict[str, Any]:
    phone = _capture(
        resume_text, r"(?:phone|mobile|tel|电话|手机)\s*[:：]?\s*([+\d][\d\s()\-]{5,})"
    )
    if not phone:
        for match in re.finditer(r"\+?\d[\d\s()\-]{7,}\d", resume_text):
            candidate = match.group(0).strip()
            if re.fullmatch(r"(?:19|20)\d{2}\s*[-–]\s*(?:19|20)\d{2}", candidate):
                continue
            if len(re.sub(r"\D", "", candidate)) >= 8:
                phone = candidate
                break
    return {
        "name": _capture(resume_text, r"(?:name|姓名)\s*[:：]\s*([^\r\n|,，]+)"),
        "phone": phone,
        "email": _capture(resume_text, r"\b([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})\b"),
        "city": _capture(
            resume_text, r"(?:city|location|所在地|城市)\s*[:：]\s*([^\r\n|,，]+)"
        ),
        "education": _find_education(resume_text),
        "skills": _find_skills(resume_text),
    }


def _experience_score(resume_text: str) -> int:
    match = re.search(
        r"(\d+)\+?\s*(?:years?|年)(?:\s+of)?(?:\s+(?:experience|经验))?",
        resume_text,
        re.IGNORECASE,
    )
    if match:
        return min(100, 45 + int(match.group(1)) * 11)
    return (
        75 if re.search(r"senior|lead|高级|负责人", resume_text, re.IGNORECASE) else 55
    )


def score_with_mock(resume_text: str, jd_text: str) -> dict[str, Any]:
    jd_skills = [skill for skill in KNOWN_SKILLS if _contains(jd_text, skill)]
    matched = [skill for skill in jd_skills if _contains(resume_text, skill)]
    missing = [skill for skill in jd_skills if skill not in matched]
    skill_score = round(len(matched) / len(jd_skills) * 100) if jd_skills else 60
    experience_score = _experience_score(resume_text)
    education_score = (
        78
        if re.search(
            r"Ph\.?D\.?|M\.?S\.?|Master|Bachelor|B\.?S\.?|硕士|学士",
            resume_text,
            re.IGNORECASE,
        )
        else 55
    )
    overall_score = round(
        skill_score * 0.5 + experience_score * 0.3 + education_score * 0.2
    )
    matched_text = "、".join(matched) if matched else "暂无明确技能命中"
    missing_text = (
        f"；待补充：{'、'.join(missing)}" if missing else "；JD 中的已识别技能均有命中"
    )
    questions = [
        f"请介绍您使用 {skill} 解决过的一个具体问题。" for skill in missing[:2]
    ]
    questions.append("请说明您在最近项目中承担的职责和量化成果。")
    return {
        "overall_score": overall_score,
        "skill_score": skill_score,
        "experience_score": experience_score,
        "education_score": education_score,
        "comment": f"Mock 评分：匹配技能为 {matched_text}{missing_text}。此结果仅用于本地演示。",
        "interview_questions": questions,
    }
