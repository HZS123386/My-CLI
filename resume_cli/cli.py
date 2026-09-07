import argparse
import sys
from typing import Sequence

from .ai_client import extract_with_ai, score_with_ai
from .errors import AppError, to_user_error
from .io_utils import print_json, read_job_description, save_json
from .mock import extract_with_mock, score_with_mock
from .pdf_reader import read_pdf_text


class CliArgumentParser(argparse.ArgumentParser):
    """Keep command-line errors in the same JSON error contract as runtime errors."""

    def error(self, message: str) -> None:
        raise AppError(
            "CLI_ARGUMENT_ERROR", f"命令参数错误：{message}。使用 --help 查看命令说明。"
        )


def _add_output_option(command: argparse.ArgumentParser) -> None:
    command.add_argument("-o", "--output", help="将 JSON 结果保存到文件（加分项）")


def build_parser() -> argparse.ArgumentParser:
    parser = CliArgumentParser(
        prog="resume-cli",
        description="读取 PDF 简历、提取结构化信息，并根据 JD 输出匹配评分",
    )
    parser.add_argument("--version", action="version", version="resume-cli 0.2.0")
    commands = parser.add_subparsers(
        dest="command", required=True, parser_class=CliArgumentParser
    )

    parse_command = commands.add_parser("parse", help="提取本地 PDF 的文本内容")
    parse_command.add_argument("pdf_path")
    _add_output_option(parse_command)

    extract_command = commands.add_parser(
        "extract", help="调用 AI 从 PDF 简历中提取结构化信息"
    )
    extract_command.add_argument("pdf_path")
    extract_command.add_argument(
        "--mock", action="store_true", help="使用本地演示数据，不调用 AI（加分项）"
    )
    _add_output_option(extract_command)

    score_command = commands.add_parser(
        "score", help="调用 AI 按 JD 对 PDF 简历进行匹配评分"
    )
    score_command.add_argument("pdf_path")
    score_command.add_argument("--jd", help="岗位描述文本文件路径")
    score_command.add_argument(
        "--mock", action="store_true", help="使用本地演示数据，不调用 AI（加分项）"
    )
    _add_output_option(score_command)
    return parser


def _run(args: argparse.Namespace) -> None:
    if args.command == "parse":
        result = read_pdf_text(args.pdf_path)
        protected_paths = [args.pdf_path]
    elif args.command == "extract":
        resume = read_pdf_text(args.pdf_path)
        result = (
            extract_with_mock(resume["text"])
            if args.mock
            else extract_with_ai(resume["text"])
        )
        protected_paths = [args.pdf_path]
    else:
        if not args.jd or not args.jd.strip():
            raise AppError(
                "JD_REQUIRED",
                "score 命令需要提供 --jd <path>。使用 --help 查看命令说明。",
            )
        jd_text = read_job_description(args.jd)
        resume = read_pdf_text(args.pdf_path)
        result = (
            score_with_mock(resume["text"], jd_text)
            if args.mock
            else score_with_ai(resume["text"], jd_text)
        )
        protected_paths = [args.pdf_path, args.jd]

    save_json(result, args.output, protected_paths=protected_paths)
    print_json(result)


def main(argv: Sequence[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except (AttributeError, OSError):
                pass
    parser = build_parser()
    try:
        _run(parser.parse_args(argv))
    except Exception as error:
        user_error = to_user_error(error)
        print_json({"error": {"code": user_error.code, "message": str(user_error)}})
        return 1
    return 0
