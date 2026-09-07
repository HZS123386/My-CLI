export const RESUME_SCHEMA = `{
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
}`;

export function extractPrompt(resumeText: string): string {
  return `你是简历信息抽取助手。仅根据简历原文提取信息；不得臆测。\n\n请只输出能被 JSON.parse 解析的 JSON，不要 Markdown、解释或代码围栏。字段必须严格符合：\n${RESUME_SCHEMA}\n\n简历原文：\n---\n${resumeText}\n---`;
}

export function scorePrompt(resumeText: string, jdText: string): string {
  return `你是一位客观的招聘评估助手。请按岗位描述评估候选人简历，评分均为 0-100 的整数。不得编造简历中不存在的经历。\n\n请只输出能被 JSON.parse 解析的 JSON，不要 Markdown、解释或代码围栏。输出格式：\n{
  "overall_score": 0,
  "skill_score": 0,
  "experience_score": 0,
  "education_score": 0,
  "comment": "简明的匹配理由与缺口",
  "interview_questions": ["建议追问的问题"]
}\n\n候选人简历：\n---\n${resumeText}\n---\n\n岗位描述：\n---\n${jdText}\n---`;
}
