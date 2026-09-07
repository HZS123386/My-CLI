import { describe, expect, it } from "vitest";
import { parseModelJson, validateResumeProfile, validateScoreResult } from "./json.js";

describe("AI JSON validation", () => {
  it("accepts JSON returned inside a markdown fence", () => {
    expect(parseModelJson("```json\n{\"name\": \"Alex\"}\n```"))
      .toEqual({ name: "Alex" });
  });

  it("validates the required resume structure", () => {
    expect(validateResumeProfile({
      name: "Alex",
      phone: "",
      email: "alex@example.com",
      city: "Hangzhou",
      education: [{ school: "Example University", major: "CS", degree: "B.S.", graduation_time: "2019" }],
      skills: ["TypeScript"],
    }).skills).toEqual(["TypeScript"]);
  });

  it("rejects scores outside the required 0-100 range", () => {
    expect(() => validateScoreResult({
      overall_score: 101,
      skill_score: 80,
      experience_score: 70,
      education_score: 80,
      comment: "test",
      interview_questions: [],
    })).toThrow("0-100");
  });
});
