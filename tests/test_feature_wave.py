import copy
import json

import pytest

from crossover_checklist_generator.cli import main
from crossover_checklist_generator.core import carry_progress, expand, load_order


def order(entries):
    return {"version": 1, "title": "Event", "sections": [{"title": "Start", "entries": entries}]}


def test_carry_ranges_additions_removals_author_order():
    old = order(
        [
            {"series": " A ", "start": 1, "end": 3, "status": "read", "note": "remember"},
            {"series": "A", "issue": "Annual 1", "status": "skipped"},
        ]
    )
    revised = order(
        [
            {"series": "A", "issue": 3},
            {"series": "a", "issue": 1},
            {"series": "A", "issue": 4},
            {"series": "A", "issue": "Annual 1"},
        ]
    )
    before = copy.deepcopy((old, revised))
    result = carry_progress(old, revised)
    report = expand(result)
    assert [i["id"] for i in report["issues"]] == ["a::3", "a::1", "a::4", "a::annual 1"]
    assert [i["status"] for i in report["issues"]] == ["read", "read", "pending", "skipped"]
    assert result["progress_migration"] == {
        "matched": ["a::3", "a::1", "a::annual 1"],
        "added": ["a::4"],
        "removed": ["a::2"],
    }
    assert report["issues"][0]["note"] == "remember"
    assert (old, revised) == before


def test_new_graph_branches_and_prerequisites_win():
    old = order(
        [
            {"series": "A", "issue": 1, "status": "read", "note": "old"},
            {"series": "B", "issue": 1, "status": "skipped"},
        ]
    )
    revised = order(
        [
            {
                "series": "B",
                "issue": 1,
                "prerequisites": ["a::1"],
                "branch_group": "route",
                "branch": "alt",
            },
            {"series": "A", "issue": 1, "branch_group": "route", "branch": "main"},
        ]
    )
    revised["branch_choices"] = {"route": "alt"}
    result = carry_progress(old, revised)
    report = expand(result)
    assert report["branch_choices"] == {"route": "alt"}
    assert report["issues"][0]["prerequisites"] == ["a::1"]
    assert report["issues"][0]["status"] == "skipped"
    assert not report["issues"][1]["selected"]
    assert report["warnings"]
    duplicate = order([{"series": "A", "issue": 1}, {"series": "a", "issue": "1"}])
    for previous, new in ((duplicate, revised), (old, duplicate)):
        with pytest.raises(ValueError, match="duplicate"):
            carry_progress(previous, new)


def test_cli_roundtrip_and_unmatched(tmp_path, capsys):
    old, revised = tmp_path / "old.json", tmp_path / "new.json"
    old.write_text(json.dumps(order([{"series": "A", "issue": 1, "status": "read"}])))
    revised.write_text(json.dumps(order([{"series": "Renamed", "issue": 1}])))
    output = tmp_path / "carried.json"
    assert (
        main(
            [
                str(revised),
                "--carry-progress",
                str(old),
                "--format",
                "input",
                "--output",
                str(output),
            ]
        )
        == 0
    )
    result = load_order(output)
    assert expand(result)["counts"] == {"pending": 1}
    assert result["progress_migration"]["removed"] == ["a::1"]
    assert main([str(revised), "--carry-progress", str(old)]) == 0
    assert "removed: a::1" in capsys.readouterr().out
    assert main([str(revised), "--carry-progress", str(old), "--format", "json"]) == 0
    assert "progress_migration" in json.loads(capsys.readouterr().out)


def test_html_reports_unmatched_progress(tmp_path, capsys):
    old, new = tmp_path / "old.json", tmp_path / "new.json"
    old.write_text(json.dumps(order([{"series": "A", "issue": 1}])))
    new.write_text(json.dumps(order([{"series": "B", "issue": 1}])))
    assert main([str(new), "--carry-progress", str(old), "--format", "html"]) == 0
    text = capsys.readouterr().out
    assert "Progress transfer removed: a::1" in text
    assert "Progress transfer added: b::1" in text
