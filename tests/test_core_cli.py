import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from crossover_checklist_generator.cli import main
from crossover_checklist_generator.core import expand, load_order, render_markdown


def order() -> dict[str, Any]:
    return {
        "version": 1,
        "title": "Signal War",
        "sections": [
            {
                "title": "Opening",
                "entries": [
                    {"series": "North Signal", "start": 3, "end": 1, "status": "read"},
                    {"series": "Relay Team", "issue": "Annual 1", "note": "After issue one"},
                ],
            }
        ],
    }


def write(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def test_expansion_order_and_markdown() -> None:
    report = expand(order())
    assert [item["issue"] for item in report["issues"]] == [3, 2, 1, "Annual 1"]
    assert report["counts"] == {"pending": 1, "read": 3}
    assert "After issue one" in render_markdown(report)
    duplicate = order()
    duplicate["sections"][0]["entries"].append({"series": "north signal", "issue": 1})
    with pytest.raises(ValueError, match="duplicate"):
        expand(duplicate)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda data: data.update(version=2), "version 1"),
        (lambda data: data.update(title=""), "requires a title"),
        (lambda data: data.update(sections=[]), "non-empty"),
        (lambda data: data["sections"][0].update(entries=[]), "requires entries"),
        (lambda data: data["sections"][0]["entries"][0].pop("series"), "requires a series"),
        (lambda data: data["sections"][0]["entries"][0].update(issue=1), "either issue"),
        (lambda data: data["sections"][0]["entries"][0].update(start="1"), "must be integers"),
        (lambda data: data["sections"][0]["entries"][0].update(status="bad"), "invalid status"),
        (lambda data: data["sections"][0]["entries"][0].update(note=4), "note must"),
    ],
)
def test_validation(tmp_path: Path, change: Callable[[dict[str, Any]], None], message: str) -> None:
    data = order()
    change(data)
    path = tmp_path / "order.json"
    write(path, data)
    with pytest.raises((TypeError, ValueError), match=message):
        load_order(path)


def test_cli_json_and_safe_output(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "order.json"
    write(path, order())
    assert main([str(path), "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["issue_count"] == 4
    output = tmp_path / "checklist.md"
    assert main([str(path), "--output", str(output)]) == 0
    assert main([str(path), "--output", str(output)]) == 2
