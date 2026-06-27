# Changelog

All notable changes to **psotobverse-utils** are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning: [SemVer](https://semver.org/).

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
