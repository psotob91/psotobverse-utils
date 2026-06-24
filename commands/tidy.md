---
description: Propose relocations for loose / misplaced files and move them only after you confirm (never auto-move).
---

Run the **tidy** workflow (see the `tidy` skill): scan the project for files that sit outside the
allowed structure declared in `.claude/policy/paths.allow.json` or that are obviously misplaced,
then present a `from -> to (reason)` plan grouped by destination. Do NOT move anything yet.

Wait for my approval. Only after I confirm, perform the moves with `git mv` (move and reference-fix
as separate verifiable steps) and report what changed and that nothing broke.

$ARGUMENTS
