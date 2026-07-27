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
