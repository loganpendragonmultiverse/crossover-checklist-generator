# Changelog

## 1.2.2 - 2026-10-20

- Reject blank issue identities, malformed statuses/branches and boolean format versions. Bound expansion to 10,000 issues before allocating ranges and validate long prerequisite chains without recursion. Markdown now exposes excluded issues and prerequisite warnings. Create output files exclusively, including refusing dangling symbolic links.

- Markdown treats supplied text as literal, single-line content so notes cannot introduce HTML or forged checklist headings. JSON retains the original text.

## 1.2.1 - 2026-10-16

- Correct release wording and the original publication date; update installation references. Feature behavior is unchanged.

## 1.2.0 - 2026-10-15

- Carry progress and private notes into revised authored orders by existing issue identities.

## 1.1.0 - 2026-09-07

- Add an editable local reading checklist with per-issue progress, round-trip export, authored prerequisites and alternative branches.
- Added regression coverage for the audited behavior and invalid inputs.

## 1.0.0 - 2026-07-26

- Added ordered crossover sections with issue ranges and single issues.
- Added duplicate detection, progress summaries, and notes.
- Added Markdown and JSON reports with safe output behavior.
