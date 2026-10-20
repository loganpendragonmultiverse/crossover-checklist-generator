import json

import pytest

from crossover_checklist_generator.cli import main
from crossover_checklist_generator.core import expand, render_markdown


def order(entries):
    return {"version": 1, "title": "Event", "sections": [{"title": "Start", "entries": entries}]}


@pytest.mark.parametrize(
    "patch", [{"series": " "}, {"issue": " "}, {"status": []}, {"branch_group": "", "branch": ""}]
)
def test_invalid_entry_rejected_before_reporting(patch):
    with pytest.raises((TypeError, ValueError)):
        expand(order([{"series": "A", "issue": 1, **patch}]))


def test_bool_version_and_bounded_ranges():
    with pytest.raises(ValueError, match="version 1"):
        expand({**order([{"series": "A", "issue": 1}]), "version": True})
    with pytest.raises(ValueError, match="10000 issue limit"):
        expand(order([{"series": "A", "start": 0, "end": 10**30}]))
    assert expand(order([{"series": "A", "start": 10000, "end": 1}]))["issue_count"] == 10000


def test_long_graph_and_cycle():
    entries = [
        {"series": "A", "issue": n, "prerequisites": [f"a::{n + 1}"] if n < 1200 else []}
        for n in range(1201)
    ]
    report = expand(order(entries))
    assert len(report["warnings"]) == 1200
    entries[-1]["prerequisites"] = ["a::0"]
    with pytest.raises(ValueError, match="cycle"):
        expand(order(entries))


def test_markdown_shows_excluded_branch_and_warning():
    data = order(
        [
            {"series": "A", "issue": 1, "prerequisites": ["b::1"]},
            {"series": "B", "issue": 1, "branch_group": "route", "branch": "side"},
            {"series": "C", "issue": 1, "branch_group": "route", "branch": "main"},
        ]
    )
    text = render_markdown(expand(data, {"route": "main"}))
    assert "excluded by selected branch" in text
    assert "requires excluded branch issue b::1" in text


def test_dangling_output_is_not_followed(tmp_path):
    source = tmp_path / "source.json"
    source.write_text(json.dumps(order([{"series": "A", "issue": 1}])))
    target, output = tmp_path / "absent", tmp_path / "output"
    try:
        output.symlink_to(target)
    except OSError:
        pytest.skip("symlink unavailable")
    assert main([str(source), "--output", str(output)]) == 2
    assert not target.exists()


def test_invalid_utf8_is_clean_error(tmp_path, capsys):
    source = tmp_path / "invalid.json"
    source.write_bytes(b"\xff")
    assert main([str(source)]) == 2
    assert "Traceback" not in capsys.readouterr().err


def test_markdown_keeps_authored_markup_literal():
    hostile = "<img src=x onerror=alert(1)>\n# Forged\n- [x] done"
    data = order([{"series": hostile, "issue": "*1*", "note": hostile}])
    data["title"] = hostile
    data["sections"][0]["title"] = hostile
    text = render_markdown(expand(data))
    assert "<img" not in text
    assert "&lt;img" in text
    assert "\n# Forged" not in text
    assert "\n- [x] done" not in text
    assert "\\# Forged" in text
