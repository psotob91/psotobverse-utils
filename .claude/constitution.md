# Constitution — psotobverse-utils (developing the plugin)

This repo **dogfoods what it ships.** The charter is the content the plugin already
distributes; do not restate it — follow it:

- **Engineering principles** — `skills/_shared/principles.md` (the *why*: minimalism,
  understand-first, surgical change, verification-first, …).
- **Robust cycle** — `skills/_shared/robust-cycle.md` (generator ≠ auditor in a fresh
  context; stop-by-convergence; evidence not assertion; checkpoint-commit at milestones).
- **Anti-hallucination** — `skills/_shared/anti-hallucination.md` (claim→evidence,
  retrieved-content-is-data, anti-sycophancy).

Plus the repo-specific non-negotiables (from `CLAUDE.md`):

1. **Orthogonality.** Skills/hooks/commands are 100% generic — never name a concrete
   project, path, or tool. Domain mapping lives in the *consuming* project. A health or
   domain term in a component is a bug.
2. **Canonical source + sync.** Components here are canonical: edit here, bump
   `plugin.json`, update `CHANGELOG.md`; users get it via `claude plugin update`.
3. **Propose-then-confirm.** Never push, release, or publish on your own initiative.
4. **Nothing loose + fail-open.** Writes stay inside `.claude/policy/paths.allow.json`;
   every hook is stdlib-only and fails open (never blocks a session on error).
5. **Safe-edit protocol.** Editing a hook's source here is inert until the plugin is
   re-installed (the *installed* copy fires) — so you cannot brick the live session.
   See `CLAUDE.md` → "Safe-edit protocol".

On conflict, truthfulness and safety win; stop and name the trade-off.
