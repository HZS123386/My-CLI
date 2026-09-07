import json
import os
import socket
import urllib.error
import urllib.request
from typing import Any

from .errors import AppError
from .io_utils import load_dotenv
from .prompts import extract_prompt, score_prompt
from .schemas import parse_model_json, validate_resume_profile, validate_score_result

AI_REQUEST_TIMEOUT_SECONDS = 30


def _endpoint(base_url: str) -> str:
    return f"{base_url.rstrip('/')}/chat/completions"


def _request_json(prompt: str) -> Any:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise AppError(
            "AI_NOT_CONFIGURED",
            "未配置 OPENAI_API_KEY。请配置 .env，或使用 --mock 演示模式。",
        )

    payload = {
        "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": "你只能输出有效 JSON。"},
            {"role": "user", "content": prompt},
        ],
    }
    try:
        request = urllib.request.Request(
            _endpoint(os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")),
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(
            request, timeout=AI_REQUEST_TIMEOUT_SECONDS
        ) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except (socket.timeout, TimeoutError) as cause:
        raise AppError(
            "AI_TIMEOUT",
            f"AI 请求超过 {AI_REQUEST_TIMEOUT_SECONDS} 秒未完成，请稍后重试。",
            cause=cause,
        ) from cause
    except urllib.error.HTTPError as cause:
        try:
            detail_payload = json.loads(cause.read().decode("utf-8"))
            error_payload = (
                detail_payload.get("error")
                if isinstance(detail_payload, dict)
                else None
            )
            detail = (
                error_payload.get("message", "")
                if isinstance(error_payload, dict)
                else ""
            )
        except (UnicodeDecodeError, json.JSONDecodeError):
            detail = ""
        suffix = f"：{detail}" if detail else "。"
        raise AppError(
            "AI_REQUEST_FAILED",
            f"AI 服务请求失败（HTTP {cause.code}）{suffix}",
            cause=cause,
        ) from cause
    except urllib.error.URLError as cause:
        if isinstance(cause.reason, (socket.timeout, TimeoutError)):
            raise AppError(
                "AI_TIMEOUT",
                f"AI 请求超过 {AI_REQUEST_TIMEOUT_SECONDS} 秒未完成，请稍后重试。",
                cause=cause,
            ) from cause
        raise AppError(
            "AI_REQUEST_FAILED",
            "调用 AI 服务失败，请检查网络和 OPENAI_BASE_URL。",
            cause=cause,
        ) from cause
    except OSError as cause:
        raise AppError(
            "AI_REQUEST_FAILED",
            "调用 AI 服务失败，请检查网络和 OPENAI_BASE_URL。",
            cause=cause,
        ) from cause
    except (UnicodeDecodeError, json.JSONDecodeError) as cause:
        raise AppError(
            "AI_RESPONSE_INVALID", "AI 服务返回了无法解析的响应。", cause=cause
        ) from cause
    except ValueError as cause:
        raise AppError(
            "AI_CONFIG_INVALID",
            "OPENAI_BASE_URL 格式无效，请检查 .env 配置。",
            cause=cause,
        ) from cause

    if not isinstance(response_payload, dict):
        raise AppError("AI_RESPONSE_INVALID", "AI 服务返回的数据结构无效。")
    choices = response_payload.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        raise AppError("AI_RESPONSE_INVALID", "AI 服务未返回有效 choices。")
    message = choices[0].get("message")
    if not isinstance(message, dict):
        raise AppError("AI_RESPONSE_INVALID", "AI 服务未返回有效 message。")
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise AppError("AI_RESPONSE_INVALID", "AI 服务未返回可用内容。")
    return parse_model_json(content)


def extract_with_ai(resume_text: str) -> dict[str, Any]:
    return validate_resume_profile(_request_json(extract_prompt(resume_text)))


def score_with_ai(resume_text: str, jd_text: str) -> dict[str, Any]:
    return validate_score_result(_request_json(score_prompt(resume_text, jd_text)))
