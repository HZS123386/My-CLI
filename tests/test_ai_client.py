import socket
import urllib.error
import urllib.request

import pytest

from resume_cli.ai_client import extract_with_ai
from resume_cli.errors import AppError


def test_ai_timeout_is_reported(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    def timeout(*args: object, **kwargs: object) -> None:
        raise TimeoutError("request timed out")

    monkeypatch.setattr(urllib.request, "urlopen", timeout)
    with pytest.raises(AppError, match="AI 请求超过") as error:
        extract_with_ai("Name: Test Candidate")
    assert error.value.code == "AI_TIMEOUT"


def test_wrapped_timeout_is_reported(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    def timeout(*args: object, **kwargs: object) -> None:
        raise urllib.error.URLError(socket.timeout("request timed out"))

    monkeypatch.setattr(urllib.request, "urlopen", timeout)
    with pytest.raises(AppError) as error:
        extract_with_ai("Name: Test Candidate")
    assert error.value.code == "AI_TIMEOUT"


def test_invalid_base_url_is_reported(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "not a valid url")

    with pytest.raises(AppError) as error:
        extract_with_ai("Name: Test Candidate")
    assert error.value.code == "AI_CONFIG_INVALID"
