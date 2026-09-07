# Crossover Checklist Generator

[![CI](https://github.com/loganpendragonmultiverse/crossover-checklist-generator/actions/workflows/ci.yml/badge.svg)](https://github.com/loganpendragonmultiverse/crossover-checklist-generator/actions/workflows/ci.yml)

Crossover Checklist Generator expands explicitly supplied comic issue ranges and single issues into a numbered reading checklist. It preserves the authored section order, supports ascending or descending integer ranges, records optional notes, and rejects duplicate issue identities before producing Markdown or JSON.

## Three-minute start

```bash
python -m pip install .
crossover-checklist examples/crossover.json
crossover-checklist examples/crossover.json --format json
```

Progress states are `pending`, `read`, and `skipped`. Range entries can set one state for the generated issues; individual issues can carry labels for annuals, specials, or non-numeric identifiers.

The tool does not scrape reading orders, decide chronology, or verify publication metadata. It faithfully expands the order supplied by the checklist author. Requires Python 3.10 or newer.

Part of the [Logan Pendragon Forge open-source collection](https://www.loganpendragonforge.com/open-source/). Licensed under the [MIT License](LICENSE).

## Version 1.1.0: reviewed improvements

Add an editable local reading checklist with per-issue progress, round-trip export, authored prerequisites and alternative branches.

```bash
crossover-checklist examples/crossover.json --format html --output checklist.html
```

The HTML checklist edits pending/read/skipped progress and private notes, then downloads a new version 1 input with one entry per issue. Author order and all alternative branches are retained. Issue IDs use normalized series::issue (lowercase, trimmed); prerequisites is an explicit array of these IDs. Entries may supply branch_group and branch; choose with --branch group=option or a branch_choices object. Unknown references, cycles and duplicate issue identities are rejected. Reports warn when a prerequisite follows its dependent or belongs to an excluded branch, without reordering the author's list. Branch selection is explicit and does not invent canonical reading order.
