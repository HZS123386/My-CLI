import type { ResumeProfile, ScoreResult } from "./types.js";

const KNOWN_SKILLS = [
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
];

function capture(text: string, expression: RegExp): string {
  return expression.exec(text)?.[1]?.trim() ?? "";
}

function contains(text: string, word: string): boolean {
  const escaped = word.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return new RegExp(`\\b${escaped}\\b`, "i").test(text);
}

function findSkills(text: string): string[] {
  return KNOWN_SKILLS.filter((skill) => contains(text, skill));
}

function findEducation(text: string): ResumeProfile["education"] {
  const line = text.split(/\r?\n/).find((item) => /university|college|大学|学院/i.test(item));
  if (!line) return [];

  const school = capture(line, /([A-Za-z\s]+(?:University|College)|[^,，|]+(?:大学|学院))/i) || line.trim();
  const degree = capture(line, /(Ph\.?D\.?|M\.?S\.?|M\.Eng\.?|B\.?S\.?|B\.Eng\.?|Master(?:'s)?|Bachelor(?:'s)?|硕士|学士)/i);
  const major = capture(line, /(?:B\.?S\.?|B\.Eng\.?|M\.?S\.?|M\.Eng\.?|Master(?:'s)?|Bachelor(?:'s)?|硕士|学士)[,.\s|-]+([^,|\n]+?)(?:\s*[,|]\s*|$)/i);
  const graduationTime = capture(line, /((?:19|20)\d{2}(?:\s*[-–]\s*(?:19|20)\d{2})?)/);
  return [{ school, major, degree, graduation_time: graduationTime }];
}

/** A deterministic offline fallback used solely by the --mock demonstration mode. */
export function extractWithMock(resumeText: string): ResumeProfile {
  const name = capture(resumeText, /(?:name|姓名)\s*[:：]\s*([^\r\n|,，]+)/i);
  const phone = capture(resumeText, /(?:phone|mobile|tel|电话|手机)\s*[:：]?\s*([+\d][\d\s()-]{5,})/i)
    || capture(resumeText, /(\+?\d[\d\s()-]{7,}\d)/);
  const email = capture(resumeText, /\b([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})\b/i);
  const city = capture(resumeText, /(?:city|location|所在地|城市)\s*[:：]\s*([^\r\n|,，]+)/i);

  return {
    name,
    phone,
    email,
    city,
    education: findEducation(resumeText),
    skills: findSkills(resumeText),
  };
}

function scoreForExperience(resumeText: string): number {
  const years = Number(capture(resumeText, /(\d+)\+?\s*(?:years?|年)(?:\s+of)?\s+(?:experience|经验)?/i));
  if (Number.isFinite(years) && years > 0) return Math.min(100, 45 + years * 11);
  return /senior|lead|高级|负责人/i.test(resumeText) ? 75 : 55;
}

/**
 * Produces transparent, repeatable scores for local demos; it is intentionally
 * simpler than the AI-backed evaluator and should not be used for hiring decisions.
 */
export function scoreWithMock(resumeText: string, jdText: string): ScoreResult {
  const jdSkills = KNOWN_SKILLS.filter((skill) => contains(jdText, skill));
  const matchedSkills = jdSkills.filter((skill) => contains(resumeText, skill));
  const missingSkills = jdSkills.filter((skill) => !contains(resumeText, skill));
  const skillScore = jdSkills.length === 0 ? 60 : Math.round((matchedSkills.length / jdSkills.length) * 100);
  const experienceScore = scoreForExperience(resumeText);
  const educationScore = /Ph\.?D\.?|M\.?S\.?|Master|Bachelor|B\.?S\.?|硕士|学士/i.test(resumeText) ? 78 : 55;
  const overallScore = Math.round(skillScore * 0.5 + experienceScore * 0.3 + educationScore * 0.2);
  const matched = matchedSkills.length ? matchedSkills.join("、") : "暂无明确技能命中";
  const missing = missingSkills.length ? `；待补充：${missingSkills.join("、")}` : "；JD 中的已识别技能均有命中";

  return {
    overall_score: overallScore,
    skill_score: skillScore,
    experience_score: experienceScore,
    education_score: educationScore,
    comment: `Mock 评分：匹配技能为 ${matched}${missing}。此结果仅用于本地演示。`,
    interview_questions: missingSkills.slice(0, 2).map((skill) => `请介绍您使用 ${skill} 解决过的一个具体问题。`).concat(
      "请说明您在最近项目中承担的职责和量化成果。",
    ),
  };
}
