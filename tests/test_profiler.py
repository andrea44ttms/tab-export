"""Tests for tab_export.profiler."""
import pytest
from tab_export.parser import TabExport, Tab
from tab_export.profiler import ProfileResult, profile_export


@pytest.fixture()
def sample_export() -> TabExport:
    return TabExport(
        source_file="test.txt",
        raw_groups={
            "Work": [
                Tab(title="GitHub", url="https://github.com/org/repo"),
                Tab(title="GitHub Issues", url="https://github.com/org/repo/issues"),
                Tab(title="Jira", url="https://jira.example.com/board"),
            ],
            "News": [
                Tab(title="BBC", url="https://bbc.co.uk/news"),
                Tab(title="Reuters", url="https://reuters.com"),
            ],
            "Solo": [
                Tab(title="Unique Site", url="https://uniquesite.io"),
            ],
        },
    )


def test_profile_returns_profile_result(sample_export):
    result = profile_export(sample_export)
    assert isinstance(result, ProfileResult)


def test_total_tabs(sample_export):
    result = profile_export(sample_export)
    assert result.total_tabs == 6


def test_total_groups(sample_export):
    result = profile_export(sample_export)
    assert result.total_groups == 3


def test_top_domains_are_tuples(sample_export):
    result = profile_export(sample_export)
    for item in result.top_domains:
        assert isinstance(item, tuple)
        assert len(item) == 2


def test_github_is_top_domain(sample_export):
    result = profile_export(sample_export)
    top_domain_names = [d for d, _ in result.top_domains]
    assert "github.com" in top_domain_names


def test_unique_domains_count(sample_export):
    result = profile_export(sample_export)
    # github.com, jira.example.com, bbc.co.uk, reuters.com, uniquesite.io
    assert result.unique_domains == 5


def test_largest_group_is_work(sample_export):
    result = profile_export(sample_export)
    assert result.largest_group == "Work"


def test_smallest_group_is_solo(sample_export):
    result = profile_export(sample_export)
    assert result.smallest_group == "Solo"


def test_group_sizes_keys_match_groups(sample_export):
    result = profile_export(sample_export)
    assert set(result.group_sizes.keys()) == {"Work", "News", "Solo"}


def test_solo_domain_tabs(sample_export):
    result = profile_export(sample_export)
    # jira.example.com, bbc.co.uk, reuters.com, uniquesite.io each appear once
    assert result.solo_domain_tabs == 4


def test_summary_lines_is_list_of_strings(sample_export):
    result = profile_export(sample_export)
    lines = result.summary_lines
    assert isinstance(lines, list)
    assert all(isinstance(ln, str) for ln in lines)


def test_summary_contains_total_tabs(sample_export):
    result = profile_export(sample_export)
    combined = "\n".join(result.summary_lines)
    assert "6" in combined


def test_top_n_limits_domains(sample_export):
    result = profile_export(sample_export, top_n=2)
    assert len(result.top_domains) <= 2
