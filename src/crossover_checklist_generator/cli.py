from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import carry_progress, expand, load_order, render_markdown
from .interactive import render_html


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a crossover reading checklist.")
    parser.add_argument("input", type=Path)
    parser.add_argument(
        "--format", choices=("markdown", "json", "html", "input"), default="markdown"
    )
    parser.add_argument(
        "--branch", action="append", default=[], help="Explicit group=option selection"
    )
    parser.add_argument("--carry-progress", type=Path, help="Previous authored checklist JSON")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        if any("=" not in value for value in args.branch):
            raise ValueError("--branch requires group=option")
        choices = dict(value.split("=", 1) for value in args.branch) if args.branch else None
        data = load_order(args.input)
        if args.carry_progress:
            data = carry_progress(load_order(args.carry_progress), data)
        if choices is not None:
            data = {**data, "branch_choices": choices}
        report = expand(data, choices)
        if "progress_migration" in data:
            report["progress_migration"] = data["progress_migration"]
            for kind in ("added", "removed"):
                values = data["progress_migration"][kind]
                if values:
                    report["warnings"].append(f"Progress transfer {kind}: {', '.join(values)}")
        rendered = (
            json.dumps(report, indent=2, ensure_ascii=False) + "\n"
            if args.format == "json"
            else render_markdown(report)
        )
        if args.format == "input":
            rendered = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        if args.format == "html":
            rendered = render_html(report)
        if args.output:
            if args.output.is_symlink():
                raise ValueError(f"output path is a symbolic link: {args.output}")
            with args.output.open("x", encoding="utf-8") as output:
                output.write(rendered)
        else:
            sys.stdout.write(rendered)
    except (OSError, UnicodeError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0
