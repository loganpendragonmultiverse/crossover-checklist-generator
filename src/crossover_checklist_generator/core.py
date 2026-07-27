from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

STATUSES = {"pending", "read", "skipped"}


def load_order(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != 1:
        raise ValueError("reading order must be a version 1 object")
    if not isinstance(data.get("title"), str) or not data["title"].strip():
        raise ValueError("reading order requires a title")
    sections = data.get("sections")
    if not isinstance(sections, list) or not sections:
        raise TypeError("sections must be a non-empty list")
    for section in sections:
        if not isinstance(section, dict) or not isinstance(section.get("title"), str):
            raise TypeError("each section requires a title")
        entries = section.get("entries")
        if not isinstance(entries, list) or not entries:
            raise TypeError(f"section {section['title']} requires entries")
        for entry in entries:
            if not isinstance(entry, dict) or not isinstance(entry.get("series"), str):
                raise TypeError("each entry requires a series")
            single = "issue" in entry
            ranged = "start" in entry or "end" in entry
            if single == ranged:
                raise ValueError("each entry must define either issue or start/end")
            if single and not isinstance(entry["issue"], (str, int)):
                raise TypeError("single issue must be text or integer")
            if ranged and (
                not isinstance(entry.get("start"), int)
                or isinstance(entry.get("start"), bool)
                or not isinstance(entry.get("end"), int)
                or isinstance(entry.get("end"), bool)
            ):
                raise TypeError("range start and end must be integers")
            if entry.get("status", "pending") not in STATUSES:
                raise ValueError("entry has an invalid status")
            if "note" in entry and not isinstance(entry["note"], str):
                raise TypeError("entry note must be text")
    return data


def expand(data: dict[str, Any]) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    seen: set[str] = set()
    for section_index, section in enumerate(data["sections"], 1):
        for entry in section["entries"]:
            if "issue" in entry:
                numbers: list[str | int] = [entry["issue"]]
            else:
                step = 1 if entry["end"] >= entry["start"] else -1
                numbers = list(range(entry["start"], entry["end"] + step, step))
            for number in numbers:
                identity = f"{entry['series'].strip().casefold()}::{str(number).strip().casefold()}"
                if identity in seen:
                    raise ValueError(f"duplicate issue: {entry['series']} #{number}")
                seen.add(identity)
                issues.append(
                    {
                        "position": len(issues) + 1,
                        "section": section["title"],
                        "section_index": section_index,
                        "series": entry["series"],
                        "issue": number,
                        "status": entry.get("status", "pending"),
                        "note": entry.get("note"),
                    }
                )
    counts = Counter(issue["status"] for issue in issues)
    return {
        "version": 1,
        "title": data["title"],
        "issue_count": len(issues),
        "counts": dict(sorted(counts.items())),
        "issues": issues,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [f"# {report['title']}", "", f"Issues: **{report['issue_count']}**", ""]
    current = None
    for issue in report["issues"]:
        if issue["section"] != current:
            current = issue["section"]
            lines.extend([f"## {current}", ""])
        marker = "x" if issue["status"] == "read" else " "
        line = f"{issue['position']}. [{marker}] **{issue['series']} #{issue['issue']}** — {issue['status']}"
        lines.append(line)
        if issue.get("note"):
            lines.append(f"   - {issue['note']}")
    return "\n".join(lines).rstrip() + "\n"
