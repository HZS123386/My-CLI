import json

from resume_cli.cli import main


def test_missing_jd_uses_json_error_contract(capsys) -> None:
    exit_code = main(["score", "resume.pdf"])
    captured = capsys.readouterr()
    assert exit_code == 1
    payload = json.loads(captured.out)
    assert payload["error"]["code"] == "JD_REQUIRED"


def test_invalid_command_argument_uses_json_error_contract(capsys) -> None:
    exit_code = main(["parse"])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert json.loads(captured.out)["error"]["code"] == "CLI_ARGUMENT_ERROR"
