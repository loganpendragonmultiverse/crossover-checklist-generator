# Testing

Run `ruff format --check .`, `ruff check .`, `mypy src`, `pytest`, and `python -m build`. CI also audits dependencies and runs the supported OS/Python matrix.

## 1.1.0 regression acceptance

Run the complete existing suite plus the new regression fixtures. Confirm the documented command produces the selected output, malformed input remains actionable, and source files remain unchanged. Add an editable local reading checklist with per-issue progress, round-trip export, authored prerequisites and alternative branches.

## Feature-wave regression gate

Run `ruff format --check .`, `ruff check .`, `mypy src`, `pytest`, and `python -m build` after installing `.[dev]` in an isolated environment. The focused regressions are in `tests/test_feature_wave.py`; run them together with the existing suite. Keep the configured coverage threshold. Repository CI supplies the supported OS/Python matrix.

Gold regression fixtures cover malformed records, preserved sources, and exclusive output creation. Run the full suite and install both wheel and source distribution in fresh environments before release.

Existing output symbolic links are refused explicitly on Windows as well as POSIX. Output directories should remain under your control while a command runs.

Wheels install README, development, testing and changelog guides at `share/crossover-checklist-generator/` under the Python environment, with editable examples in its `examples/` subdirectory. Both release distributions must contain these exact tagged files.
