import re
from pathlib import Path
from typing import Any

from pypdf import PdfReader

from .errors import AppError


def read_pdf_text(pdf_path: str) -> dict[str, Any]:
    absolute_path = Path(pdf_path).expanduser().resolve()
    if not absolute_path.exists():
        raise AppError("PDF_NOT_FOUND", f"找不到 PDF 文件：{absolute_path}")
    if not absolute_path.is_file():
        raise AppError("PDF_NOT_A_FILE", f"指定路径不是文件：{absolute_path}")
    if absolute_path.suffix.lower() != ".pdf":
        raise AppError("NOT_PDF", f"文件不是 PDF：{absolute_path}")

    try:
        reader = PdfReader(str(absolute_path), strict=False)
        pages = len(reader.pages)
        page_text = [(page.extract_text() or "") for page in reader.pages]
    except Exception as cause:
        raise AppError(
            "PDF_PARSE_FAILED", f"无法解析 PDF：{absolute_path}", cause=cause
        ) from cause

    text = "\n".join(page_text).replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(
        r"^\s*--\s*\d+\s+of\s+\d+\s*--\s*$", "", text, flags=re.MULTILINE
    ).strip()
    if not text:
        raise AppError(
            "PDF_TEXT_EMPTY", "PDF 中未提取到文本。该文件可能是扫描件，请先进行 OCR。"
        )

    return {"source": str(absolute_path), "pages": pages, "text": text}
