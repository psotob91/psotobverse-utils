# Changelog

All notable changes to **psotobverse-utils** are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning: [SemVer](https://semver.org/).

## [1.4.0] - 2026-06-28

### Added
- **Opt-in meta-learner** (generic mechanism; activated per-project by a
  `.claude/meta-learner.json` config — absent config ⇒ every hook no-ops, so it
  never litters unrelated repos). Stdlib hooks, fail-open, portable bootstrapper:
  - `SessionStart` (`session_start.py`) — fast resume (injects the project's
    `SESSION_STATE.md` + last handoff) and **crash detection** via a dirty-bit
    (`.claude/state/session.json`: armed `active`, flipped `clean_exit` on a clean
    end; an `active` bit at next start ⇒ the previous session ended uncleanly).
  - `UserPromptSubmit` (`capture_signal.py`) — cheap, append-only capture of
    **correction** and **domain consensus** signals to `learning/queue/signals.jsonl`.
    The domain patterns come from the project config, so one hook serves any repo.
  - `SessionEnd` (`session_end.py`) — one forward-looking handoff to
    `learning/sessions/` (only when the tree is dirty or signals were captured).
- **`/reflect` skill** — human-gated synthesis: turns the signal queue into
  PROPOSED diffs for the project's `learning/` files (incl. the consensus radar
  named in the config); never auto-edits. Pairs with the robust core.
- **`/audit-report` skill** — structures multi-agent audit / workflow output as a
  small indexed `docs/audits/<date>-<slug>/00-summary.md` with raw maps as
  referenced sidecars, instead of an unindexed mega-blob that blows context.

### Notes
- These extend, they do not change, the existing guardrail hooks. The meta-learner
  is the project-coupled learning loop hoisted out of the datavidence template so
  it ships versioned and DRY (one copy in the plugin, opted into per project).

## [1.3.1] - 2026-06-27

### Fixed
- **Cowork hooks no longer fail-closed.** `hooks/hooks.json` previously invoked
  each hook as `python "${CLAUDE_PLUGIN_ROOT}/hooks/<x>.py"`. Cowork does not
  shell-expand `${CLAUDE_PLUGIN_ROOT}`, so the literal string reached Python, the
  script was not found, Python exited 2, and Cowork treated exit-2 as a hard
  block — blocking *all* Write/Read operations (violating the fail-open mandate in
  datavidence ADR-0002). Each command is now a `python -c` bootstrapper that reads
  `CLAUDE_PLUGIN_ROOT` **by name** from `os.environ` (no `${...}`, no inner double
  quotes → portable across bash/cmd/PowerShell) and `runpy`s the real hook; if the
  env var is absent or the script is missing it exits 0 (**fail-open**). Restores
  full enforcement in terminal Claude Code and enables it in Cowork iff
  `CLAUDE_PLUGIN_ROOT` is present as a process env var; otherwise degrades safely.

## [1.3.0] - 2026-06

### Added
- Formalized as a Claude Code plugin: thin-verb skills (`index`, `goal`,
  `reconcile`, `deliberate`, `tidy`) over a shared robust core; governance hooks
  (`nothing_loose` write guard, `.env` protection, doc hygiene, stop reminder);
  generator/auditor subagents (`executor`, `explorer`).
- `install.py` with `--check` / overlay support.

### Fixed
- Stop double-loading `hooks/hooks.json` (do not also declare it in `plugin.json`).
- Removed duplicate `/tidy` command that collided with the `tidy` skill.
- Quoted `${CLAUDE_PLUGIN_ROOT}` paths and corrected install commands.

_Detailed pre-1.3.1 history is in the git log._
