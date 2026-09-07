# Development

Use src and the regression suite. Protected CI must pass before release.

## 1.1.0 improvement session

Add an editable local reading checklist with per-issue progress, round-trip export, authored prerequisites and alternative branches.

The HTML checklist edits pending/read/skipped progress and private notes, then downloads a new version 1 input with one entry per issue. Author order and all alternative branches are retained. Issue IDs use normalized series::issue (lowercase, trimmed); prerequisites is an explicit array of these IDs. Entries may supply branch_group and branch; choose with --branch group=option or a branch_choices object. Unknown references, cycles and duplicate issue identities are rejected. Reports warn when a prerequisite follows its dependent or belongs to an excluded branch, without reordering the author's list. Branch selection is explicit and does not invent canonical reading order.

Local formatting, lint, strict types and regression tests pass. Public release completion requires the protected CI/CodeQL matrix, tagged artifacts and matching Forge catalog/detail deployment.
