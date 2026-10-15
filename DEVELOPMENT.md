# Development

Use src and the regression suite. Protected CI must pass before release.

## 1.1.0 improvement session

Add an editable local reading checklist with per-issue progress, round-trip export, authored prerequisites and alternative branches.

The HTML checklist edits pending/read/skipped progress and private notes, then downloads a new version 1 input with one entry per issue. Author order and all alternative branches are retained. Issue IDs use normalized series::issue (lowercase, trimmed); prerequisites is an explicit array of these IDs. Entries may supply branch_group and branch; choose with --branch group=option or a branch_choices object. Unknown references, cycles and duplicate issue identities are rejected. Reports warn when a prerequisite follows its dependent or belongs to an excluded branch, without reordering the author's list. Branch selection is explicit and does not invent canonical reading order.

Local formatting, lint, strict types and regression tests pass. Public release completion requires the protected CI/CodeQL matrix, tagged artifacts and matching Forge catalog/detail deployment.


## 1.2.0 candidate

Carry saved progress into a revised authored order with:

```bash
crossover-checklist revised.json --carry-progress edited-old.json --format input --output carried.json
crossover-checklist carried.json --format html --output checklist.html
```

Both inputs are version 1 authored checklist JSON, including downloads from the existing HTML editor. Only status and private notes transfer, using the existing normalized `series::issue` identity. Ranges expand to single entries so individual progress can survive revised ranges. New section order, prerequisites, branch definitions and branch choices remain authoritative. No title, issue renumbering or branch equivalence is guessed. Duplicate identities or invalid graphs fail through the existing validators. The additive `progress_migration` summary lists matched, added and removed IDs in author order; unmatched new entries retain their revised status/notes. JSON and Markdown reports include that summary. `--format input` saves reusable authored JSON; normal JSON remains a report.
