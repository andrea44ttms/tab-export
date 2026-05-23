"""Integration tests: CLI round-trip from file to formatted output."""

import textwrap
from pathlib import Path

import pytest

from tab_export.cli import main


@pytest.fixture()
def multi_group_file(tmp_path: Path) -> Path:
    content = textwrap.dedent("""\
        [Dev Tools]
        https://docs.python.org | Python Docs
        https://mypy-lang.org | Mypy

        [Reading]
        https://realpython.com | Real Python
        https://martinfowler.com | Martin Fowler

        [Empty Group]
    """)
    p = tmp_path / "multi.txt"
    p.write_text(content, encoding="utf-8")
    return p


def test_all_groups_present_in_markdown(multi_group_file: Path, capsys: pytest.CaptureFixture) -> None:
    main([str(multi_group_file)])
    out = capsys.readouterr().out
    assert "Dev Tools" in out
    assert "Reading" in out
    assert "Empty Group" in out


def test_all_links_present_in_markdown(multi_group_file: Path, capsys: pytest.CaptureFixture) -> None:
    main([str(multi_group_file)])
    out = capsys.readouterr().out
    assert "https://docs.python.org" in out
    assert "https://realpython.com" in out


def test_round_trip_file_matches_stdout(
    multi_group_file: Path, tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    out_file = tmp_path / "out.md"
    main([str(multi_group_file), "-o", str(out_file)])
    # stdout only prints confirmation when writing to file
    file_content = out_file.read_text(encoding="utf-8")

    main([str(multi_group_file)])
    stdout_content = capsys.readouterr().out

    assert file_content == stdout_content


def test_notion_output_has_no_h2(multi_group_file: Path, capsys: pytest.CaptureFixture) -> None:
    main([str(multi_group_file), "-f", "notion"])
    out = capsys.readouterr().out
    assert "## " not in out
    assert "### " in out


def test_output_ends_with_newline(multi_group_file: Path, capsys: pytest.CaptureFixture) -> None:
    main([str(multi_group_file)])
    out = capsys.readouterr().out
    assert out.endswith("\n")
