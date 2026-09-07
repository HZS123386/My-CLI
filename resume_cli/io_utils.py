import json
import os
from pathlib import Path
from typing import Any, Iterable

from .errors import AppError


def load_dotenv(path: str = ".env") -> None:
    """Load simple KEY=VALUE entries without overriding shell environment variables."""
    env_path = Path(path)
    if not env_path.is_file():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def print_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def save_json(
    value: Any, output_path: str | None, *, protected_paths: Iterable[str] = ()
) -> None:
    if not output_path:
        return
    absolute_path = Path(output_path).expanduser().resolve()
    protected = {Path(item).expanduser().resolve() for item in protected_paths}
    if absolute_path in protected:
        raise AppError(
            "OUTPUT_CONFLICT",
            f"输出路径不能覆盖输入文件：{absolute_path}",
        )
    try:
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
        absolute_path.write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    except OSError as cause:
        raise AppError(
            "OUTPUT_WRITE_FAILED", f"无法写入输出文件：{absolute_path}", cause=cause
        ) from cause
    print(f"结果已保存到 {absolute_path}", file=os.sys.stderr)


def read_job_description(jd_path: str) -> str:
    absolute_path = Path(jd_path).expanduser().resolve()
    if not absolute_path.exists():
        raise AppError("JD_NOT_FOUND", f"找不到 JD 文件：{absolute_path}")
    if not absolute_path.is_file():
        raise AppError("JD_NOT_A_FILE", f"指定的 JD 路径不是文件：{absolute_path}")
    try:
        content = absolute_path.read_text(encoding="utf-8").strip()
    except OSError as cause:
        raise AppError(
            "JD_READ_FAILED", f"无法读取 JD 文件：{absolute_path}", cause=cause
        ) from cause
    if not content:
        raise AppError("JD_EMPTY", f"JD 文件为空：{absolute_path}")
    return content
