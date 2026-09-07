import json
from pathlib import Path

import pytest

from crossover_checklist_generator.cli import main
from crossover_checklist_generator.core import expand, load_order
from crossover_checklist_generator.interactive import render_html


def sample() -> dict:
    return {
        "version": 1,
        "title": "Event",
        "sections": [
            {
                "title": "Start",
                "entries": [
                    {"series": "A", "issue": 1, "status": "read"},
                    {
                        "series": "A",
                        "issue": 2,
                        "prerequisites": ["a::1"],
                        "branch_group": "route",
                        "branch": "main",
                    },
                    {"series": "B", "issue": 1, "branch_group": "route", "branch": "alternate"},
                ],
            }
        ],
    }


def test_branches_preserve_order_and_roundtrip(tmp_path: Path) -> None:
    data = sample()
    data["sections"][0]["entries"].append({"series": "C", "issue": 1, "prerequisites": ["a::2"]})
    report = expand(data, {"route": "alternate"})
    assert [i["id"] for i in report["issues"]] == ["a::1", "a::2", "b::1", "c::1"]
    assert not report["issues"][1]["selected"]
    assert "excluded branch" in report["warnings"][0]
    source, output = tmp_path / "order.json", tmp_path / "editor.html"
    source.write_text(json.dumps(data), encoding="utf-8")
    assert (
        main(
            [
                str(source),
                "--branch",
                "route=alternate",
                "--format",
                "html",
                "--output",
                str(output),
            ]
        )
        == 0
    )
    assert "Download edited checklist" in output.read_text(encoding="utf-8")
    assert main([str(source), "--branch", "broken"]) == 2
    roundtrip = {
        "version": 1,
        "title": report["title"],
        "sections": [
            {
                "title": "Start",
                "entries": [
                    {
                        "series": i["series"],
                        "issue": i["issue"],
                        "status": "read",
                        "prerequisites": i["prerequisites"],
                    }
                    for i in report["issues"]
                ],
            }
        ],
    }
    source.write_text(json.dumps(roundtrip), encoding="utf-8")
    assert expand(load_order(source))["counts"] == {"read": 4}
    data["title"] = "</script><script>alert(1)</script>"
    assert "</script><script>alert" not in render_html(expand(data))


def test_cycles_unknowns_conflicts_and_future_prerequisites() -> None:
    data = sample()
    data["sections"][0]["entries"][0]["prerequisites"] = ["b::1"]
    assert "precedes" in expand(data)["warnings"][0]
    data["sections"][0]["entries"][2]["prerequisites"] = ["a::1"]
    with pytest.raises(ValueError, match="cycle"):
        expand(data)
    for change in ({"prerequisites": ["missing"]}, {"branch_group": "x"}):
        data = sample()
        data["sections"][0]["entries"][0].update(change)
        with pytest.raises(ValueError):
            expand(data)
    with pytest.raises(ValueError, match="Unknown branch"):
        expand(sample(), {"route": "missing"})
    with pytest.raises(TypeError):
        expand({**sample(), "branch_choices": []})
