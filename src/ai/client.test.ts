import { afterEach, describe, expect, it, vi } from "vitest";
import { extractWithAi } from "./client.js";

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
});

describe("AI client", () => {
  it("turns a timed-out request into an actionable AppError", async () => {
    vi.stubEnv("OPENAI_API_KEY", "test-key");
    const timeout = Object.assign(new Error("request timed out"), { name: "TimeoutError" });
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(timeout));

    await expect(extractWithAi("Name: Test Candidate"))
      .rejects.toMatchObject({ code: "AI_TIMEOUT" });
  });
});
