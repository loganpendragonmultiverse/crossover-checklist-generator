from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import expand, load_order, render_markdown
from .interactive import render_html


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a crossover reading checklist.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--format", choices=("markdown", "json", "html"), default="markdown")
    parser.add_argument(
        "--branch", action="append", default=[], help="Explicit group=option selection"
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        if any("=" not in value for value in args.branch):
            raise ValueError("--branch requires group=option")
        choices = dict(value.split("=", 1) for value in args.branch) if args.branch else None
        report = expand(load_order(args.input), choices)
        rendered = (
            json.dumps(report, indent=2, ensure_ascii=False) + "\n"
            if args.format == "json"
            else render_markdown(report)
        )
        if args.format == "html":
            rendered = render_html(report)
        if args.output:
            if args.output.exists():
                raise ValueError(f"output already exists: {args.output}")
            args.output.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0
