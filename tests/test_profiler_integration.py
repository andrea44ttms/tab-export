"""Integration tests for profiler against realistic multi-group exports."""
from tab_export.parser import TabExport, Tab
from tab_export.profiler import profile_export


def _make_export(groups: dict) -> TabExport:
    return TabExport(source_file="integration.txt", raw_groups=groups)


def test_single_group_export():
    export = _make_export({
        "Only": [
            Tab(title="A", url="https://alpha.com"),
            Tab(title="B", url="https://beta.com"),
        ]
    })
    result = profile_export(export)
    assert result.total_groups == 1
    assert result.largest_group == result.smallest_group == "Only"


def test_empty_group_handled_gracefully():
    export = _make_export({
        "Empty": [],
        "Full": [Tab(title="X", url="https://x.com")],
    })
    result = profile_export(export)
    assert result.smallest_group == "Empty"
    assert result.group_sizes["Empty"] == 0


def test_repeated_domain_across_groups():
    export = _make_export({
        "A": [Tab(title="G1", url="https://github.com/a")],
        "B": [Tab(title="G2", url="https://github.com/b")],
        "C": [Tab(title="G3", url="https://github.com/c")],
    })
    result = profile_export(export)
    top_names = [d for d, _ in result.top_domains]
    assert "github.com" in top_names
    assert result.top_domains[0][1] == 3


def test_summary_lines_include_group_info():
    export = _make_export({
        "Research": [
            Tab(title="Paper", url="https://arxiv.org/abs/1234"),
            Tab(title="Blog", url="https://medium.com/post"),
        ]
    })
    result = profile_export(export)
    combined = "\n".join(result.summary_lines)
    assert "Research" in combined


def test_large_export_top_n_respected():
    groups = {
        f"Group{i}": [Tab(title=f"Tab{j}", url=f"https://site{j}.com/page")
                      for j in range(5)]
        for i in range(10)
    }
    export = _make_export(groups)
    result = profile_export(export, top_n=3)
    assert len(result.top_domains) <= 3
    assert result.total_tabs == 50
