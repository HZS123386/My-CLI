import "dotenv/config";
import { AppError } from "../core/errors.js";
import { parseModelJson, validateResumeProfile, validateScoreResult } from "./json.js";
import { extractPrompt, scorePrompt } from "./prompts.js";
import type { ResumeProfile, ScoreResult } from "./types.js";

interface ChatCompletionResponse {
  choices?: Array<{ message?: { content?: string | null } }>;
  error?: { message?: string };
}

const AI_REQUEST_TIMEOUT_MS = 30_000;

function endpointFrom(baseUrl: string): string {
  return `${baseUrl.replace(/\/+$/, "")}/chat/completions`;
}

async function requestJson(prompt: string): Promise<unknown> {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    throw new AppError("AI_NOT_CONFIGURED", "未配置 OPENAI_API_KEY。请配置 .env，或使用 --mock 演示模式。");
  }

  const baseUrl = process.env.OPENAI_BASE_URL || "https://api.openai.com/v1";
  const model = process.env.OPENAI_MODEL || "gpt-4o-mini";
  let response: Response;
  try {
    response = await fetch(endpointFrom(baseUrl), {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model,
        temperature: 0.1,
        response_format: { type: "json_object" },
        messages: [
          { role: "system", content: "你只能输出有效 JSON。" },
          { role: "user", content: prompt },
        ],
      }),
      signal: AbortSignal.timeout(AI_REQUEST_TIMEOUT_MS),
    });
  } catch (cause) {
    if (cause instanceof Error && (cause.name === "TimeoutError" || cause.name === "AbortError")) {
      throw new AppError("AI_TIMEOUT", `AI 请求超过 ${AI_REQUEST_TIMEOUT_MS / 1000} 秒未完成，请稍后重试。`, { cause });
    }
    throw new AppError("AI_REQUEST_FAILED", "调用 AI 服务失败，请检查网络和 OPENAI_BASE_URL。", { cause });
  }

  let payload: ChatCompletionResponse;
  try {
    payload = (await response.json()) as ChatCompletionResponse;
  } catch (cause) {
    throw new AppError("AI_RESPONSE_INVALID", "AI 服务返回了无法解析的响应。", { cause });
  }

  if (!response.ok) {
    const detail = payload.error?.message ? `：${payload.error.message}` : "。";
    throw new AppError("AI_REQUEST_FAILED", `AI 服务请求失败（HTTP ${response.status}）${detail}`);
  }

  const content = payload.choices?.[0]?.message?.content;
  if (!content) {
    throw new AppError("AI_RESPONSE_INVALID", "AI 服务未返回可用内容。");
  }
  return parseModelJson(content);
}

export async function extractWithAi(resumeText: string): Promise<ResumeProfile> {
  return validateResumeProfile(await requestJson(extractPrompt(resumeText)));
}

export async function scoreWithAi(resumeText: string, jdText: string): Promise<ScoreResult> {
  return validateScoreResult(await requestJson(scorePrompt(resumeText, jdText)));
}
