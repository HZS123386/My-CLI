RESUME_SCHEMA = """{
  "name": "string (unknown use empty string)",
  "phone": "string (unknown use empty string)",
  "email": "string (unknown use empty string)",
  "city": "string (unknown use empty string)",
  "education": [{
    "school": "string",
    "major": "string",
    "degree": "string",
    "graduation_time": "string"
  }],
  "skills": ["string"]
}"""


def extract_prompt(resume_text: str) -> str:
    return f"""你是简历信息抽取助手。仅根据简历原文提取信息；不得臆测。

请只输出能被 JSON 解析的 JSON，不要 Markdown、解释或代码围栏。字段必须严格符合：
{RESUME_SCHEMA}

简历原文：
---
{resume_text}
---"""


def score_prompt(resume_text: str, jd_text: str) -> str:
    return f"""你是一位客观的招聘评估助手。请按岗位描述评估候选人简历，评分均为 0-100 的整数。不得编造简历中不存在的经历。

请只输出能被 JSON 解析的 JSON，不要 Markdown、解释或代码围栏。输出格式：
{{
  "overall_score": 0,
  "skill_score": 0,
  "experience_score": 0,
  "education_score": 0,
  "comment": "简明的匹配理由与缺口",
  "interview_questions": ["建议追问的问题"]
}}

候选人简历：
---
{resume_text}
---

岗位描述：
---
{jd_text}
---"""
