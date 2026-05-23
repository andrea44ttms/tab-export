"""Tests for the CLI entry point."""

import textwrap
from pathlib import Path

import pytest

from tab_export.cli import main


SAMPLE_CONTENT = textwrap.dedent("""\
    [Work]
    https://github.com | GitHub
    https://python.org | Python

    [Personal]
    https://news.ycombinator.com | Hacker News
""")


@pytest.fixture()
def tab_file(tmp_path: Path) -> Path:
    p = tmp_path / "tabs.txt"
    p.write_text(SAMPLE_CONTENT, encoding="utf-8")
    return p


def test_cli_returns_zero_on_success(tab_file: Path) -> None:
    assert main([str(tab_file)]) == 0


def test_cli_returns_nonzero_for_missing_file(tmp_path: Path) -> None:
    assert main([str(tmp_path / "nonexistent.txt")]) == 1


def test_cli_writes_to_stdout(tab_file: Path, capsys: pytest.CaptureFixture) -> None:
    main([str(tab_file)])
    captured = capsys.readouterr()
    assert "GitHub" in captured.out
    assert "Work" in captured.out


def test_cli_writes_to_output_file(tab_file: Path, tmp_path: Path) -> None:
    out_file = tmp_path / "output.md"
    main([str(tab_file), "-o", str(out_file)])
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "GitHub" in content


def test_cli_notion_format(tab_file: Path, capsys: pytest.CaptureFixture) -> None:
    main([str(tab_file), "--format", "notion"])
    captured = capsys.readouterr()
    assert "###" in captured.out


def test_cli_markdown_format_default(tab_file: Path, capsys: pytest.CaptureFixture) -> None:
    main([str(tab_file)])
    captured = capsys.readouterr()
    assert "##" in captured.out


def test_cli_output_file_message(tab_file: Path, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    out_file = tmp_path / "result.md"
    main([str(tab_file), "-o", str(out_file)])
    captured = capsys.readouterr()
    assert "Written to" in captured.out
