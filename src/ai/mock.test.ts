import { describe, expect, it } from "vitest";
import { extractWithMock, scoreWithMock } from "./mock.js";

const resume = `Name: Alex Chen
Phone: +1 415 555 0123
Email: alex@example.com
City: Hangzhou
4 years of experience with TypeScript, React, Node.js, SQL and Docker.
2015 - 2019 | Example University | B.S. Computer Science`;

describe("mock demonstration mode", () => {
  it("extracts common contact fields and skills", () => {
    const result = extractWithMock(resume);
    expect(result.email).toBe("alex@example.com");
    expect(result.skills).toEqual(expect.arrayContaining(["TypeScript", "React", "Node.js"]));
  });

  it("produces bounded deterministic JD scores", () => {
    const result = scoreWithMock(resume, "Need TypeScript, React, Node.js, Docker and AWS experience.");
    expect(result.overall_score).toBeGreaterThanOrEqual(0);
    expect(result.overall_score).toBeLessThanOrEqual(100);
    expect(result.comment).toContain("Mock 评分");
  });
});
