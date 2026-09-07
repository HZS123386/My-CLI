from pathlib import Path

import pytest

from resume_cli.errors import AppError
from resume_cli.io_utils import save_json


def test_output_cannot_overwrite_an_input_file(tmp_path: Path) -> None:
    source = tmp_path / "resume.pdf"
    original = b"%PDF-1.4\noriginal"
    source.write_bytes(original)

    with pytest.raises(AppError, match="输出路径不能覆盖输入文件") as error:
        save_json({"text": "result"}, str(source), protected_paths=[str(source)])

    assert error.value.code == "OUTPUT_CONFLICT"
    assert source.read_bytes() == original
