import { AppError } from "../core/errors.js";
import type { Education, ResumeProfile, ScoreResult } from "./types.js";

function asObject(value: unknown, context: string): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new AppError("AI_INVALID_JSON", `${context}必须是 JSON 对象。`);
  }
  return value as Record<string, unknown>;
}

function asString(value: unknown, field: string): string {
  if (typeof value !== "string") {
    throw new AppError("AI_INVALID_JSON", `AI 返回的 ${field} 必须是字符串。`);
  }
  return value.trim();
}

function asStringArray(value: unknown, field: string): string[] {
  if (!Array.isArray(value) || value.some((item) => typeof item !== "string")) {
    throw new AppError("AI_INVALID_JSON", `AI 返回的 ${field} 必须是字符串数组。`);
  }
  return value.map((item) => item.trim()).filter(Boolean);
}

function asScore(value: unknown, field: string): number {
  if (typeof value !== "number" || !Number.isFinite(value) || value < 0 || value > 100) {
    throw new AppError("AI_INVALID_JSON", `AI 返回的 ${field} 必须是 0-100 的数字。`);
  }
  return Math.round(value);
}

export function parseModelJson(raw: string): unknown {
  const cleaned = raw.trim().replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/, "").trim();
  try {
    return JSON.parse(cleaned);
  } catch (cause) {
    throw new AppError("AI_INVALID_JSON", "AI 未返回有效 JSON，请重试或使用 --mock。", { cause });
  }
}

export function validateResumeProfile(value: unknown): ResumeProfile {
  const data = asObject(value, "AI 返回结果");
  const educationSource = data.education;
  if (!Array.isArray(educationSource)) {
    throw new AppError("AI_INVALID_JSON", "AI 返回的 education 必须是数组。");
  }

  const education: Education[] = educationSource.map((item, index) => {
    const itemData = asObject(item, `education[${index}]`);
    return {
      school: asString(itemData.school, `education[${index}].school`),
      major: asString(itemData.major, `education[${index}].major`),
      degree: asString(itemData.degree, `education[${index}].degree`),
      graduation_time: asString(itemData.graduation_time, `education[${index}].graduation_time`),
    };
  });

  return {
    name: asString(data.name, "name"),
    phone: asString(data.phone, "phone"),
    email: asString(data.email, "email"),
    city: asString(data.city, "city"),
    education,
    skills: asStringArray(data.skills, "skills"),
  };
}

export function validateScoreResult(value: unknown): ScoreResult {
  const data = asObject(value, "AI 返回结果");
  return {
    overall_score: asScore(data.overall_score, "overall_score"),
    skill_score: asScore(data.skill_score, "skill_score"),
    experience_score: asScore(data.experience_score, "experience_score"),
    education_score: asScore(data.education_score, "education_score"),
    comment: asString(data.comment, "comment"),
    interview_questions: asStringArray(data.interview_questions, "interview_questions"),
  };
}
