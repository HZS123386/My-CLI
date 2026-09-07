from pathlib import Path

import pytest

from resume_cli.errors import AppError
from resume_cli.pdf_reader import read_pdf_text


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_reads_sample_pdf_and_removes_page_separator() -> None:
    result = read_pdf_text(str(PROJECT_ROOT / "examples" / "resume-sample.pdf"))
    assert result["pages"] == 1
    assert "Name: Alex Chen" in result["text"]
    assert "-- 1 of 1 --" not in result["text"]


def test_missing_pdf_has_actionable_error(tmp_path: Path) -> None:
    with pytest.raises(AppError, match="找不到 PDF 文件"):
        read_pdf_text(str(tmp_path / "missing.pdf"))
