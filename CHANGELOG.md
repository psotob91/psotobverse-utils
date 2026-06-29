# Changelog

All notable changes to **psotobverse-utils** are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning: [SemVer](https://semver.org/).

## [1.8.0] - 2026-06-29

### Added
- **`/rescue-manifest`** -- plans the migration of an arbitrary legacy / source repo into a
  project's target layout: classifies every item KEEP / DROP / REGENERATE / KEEP-EXTERNAL and
  applies four tests (regenerability; the archivist "would a data archivist include it in a
  deposit?" test; a hard-coded-path audit; a size gate), then emits a decision-matrix manifest for
  human sign-off. It PLANS the migration and moves nothing -- approved moves hand off to `/tidy`.
  Generic (no project paths); references the shared robust core + anti-hallucination primitives.

## [1.7.0] - 2026-06-28

### Added
- **`/comprehend`** — a restate-before-act comprehension gate: the agent explains, in
  its own words, the goal, explicit + hidden assumptions, success criteria, ambiguities,
  clarifying questions, scope/data limits, and what it will NOT assume; runs a `/coverage`
  sweep; renders ASCII decision/timeline diagrams when the task is about rules or time
  logic; then hard-stops without planning or executing.
- **`/coverage`** — a recall safety net against false negatives in policy/doc selection:
  fans out N decorrelated reviewer lenses over a project-declared catalog, aggregates by
  **union** (recall) + **votes** (triage: Tier-1 must / Tier-2 consider), reports
  deliberately-excluded items and off-route catches. Benchmarked in the datavidence
  factory: union recall 1.00, 46/46 off-route positives caught (majority lowers recall).
- **`/cross-examine`** — an adversarial multi-agent review panel: independent skeptics
  try to refute a change/finding/plan/claim, vote (confirmed = survives a majority),
  synthesize, and propose (never auto-fix).
- **Routing hooks (opt-in, fail-open, additive):** `policy_router.py` (UserPromptSubmit —
  additive next-policy reminders driven by the child's `.claude/policy/routing.yml`;
  never blocks), `comprehension_gate.py` (PreToolUse — the one write-gate: *asks* before
  writing a phenotype file when its required timeline/decision artifact is missing; never
  denies, never blocks reads), `coverage_sentinel.py` (UserPromptSubmit — once-per-session
  nudge toward `/coverage` on a substantive task). `routing_util.py` is a shared stdlib
  parser. **Invariant 0:** routing is additive, never subtractive.

### Changed
- **Self-hardening (dogfooding):** the repo now opts into the guardrails it ships via
  `.claude/` (constitution pointing at `skills/_shared/`, knowledge-map, self-guard
  `policy/paths.allow.json`, `meta-learner.json`), adds hygiene
  (`.editorconfig`/`.gitattributes`/`.gitleaks.toml`) and CI (`validate-plugin`:
  manifests/hooks parse, py_compile, fail-open-on-empty-stdin, frontmatter, doc_hygiene).
- `CLAUDE.md` refreshed (current hooks/commands) and documents the **safe-edit protocol**
  (the installed/cache copy fires, not the source you edit; config is live but hook
  *behavior* changes need `claude plugin update`; fail-open ⇒ no lock-out).

## [1.6.0] - 2026-06-28

### Fixed
- **Hooks now run in the Claude Desktop app** (`CLAUDE_CODE_ENTRYPOINT=claude-desktop`).
  Empirically (datavidence investigation 2026-06-28): the desktop app *does* fire
  plugin hooks, but it does **not** set `CLAUDE_PLUGIN_ROOT`. The previous
  bootstrapper (read `CLAUDE_PLUGIN_ROOT`, else exit 0) therefore fired-but-no-op'd
  there, so the meta-learner did nothing in desktop sessions. The bootstrapper is
  now **self-discovering**: it tries `CLAUDE_PLUGIN_ROOT` first (terminal CLI — no
  behaviour change), and if absent resolves the install dir at runtime from
  `~/.claude/plugins/installed_plugins.json` (`installPath`), falling back to a glob
  of `~/.claude/plugins/cache/*/psotobverse-utils/*` (newest). Still fail-open if
  nothing resolves. Depends only on what every install creates (the cache +
  `installed_plugins.json`), never on a source checkout — portable to any machine
  or new user. Verified: emits identical output with `CLAUDE_PLUGIN_ROOT` set
  (terminal) and unset (desktop), and a fresh desktop session now writes the
  dirty-bit (`.claude/state/session.json`).

### Known limitation
- The desktop app runs hooks (side effects work: `UserPromptSubmit` signal capture,
  `SessionEnd` handoff, the `SessionStart` dirty-bit) but does **not** inject
  `SessionStart` `additionalContext` into the model (Anthropic feature request
  anthropics/claude-code#47993). So **auto-resume-by-injection only works in the
  terminal**. For desktop, have the project's `CLAUDE.md` instruct the agent to
  self-read `SESSION_STATE.md` at session start (`CLAUDE.md` *is* injected in the
  desktop app).

## [1.5.0] - 2026-06-28

### Added
- **Once-per-machine environment probe** folded into the meta-learner's
  `SessionStart` hook (`hooks/env_probe.py`). On the first session on a machine it
  detects the shell(s) (incl. PowerShell edition/version), available CLIs (git, gh,
  python, uv, copier, node, Rscript, make, jq, rg, docker, quarto, …) and OS
  quirks, then caches the result machine-globally at `~/.claude/environment.json`
  (+ a human-readable `environment.md`). Every later session injects a concise
  summary read from the cache — the agent learns what the machine has (and what to
  avoid, e.g. PowerShell 5.1 `&&`) without re-probing. Missing tools come with
  install hints. Refresh by deleting the cache. Projects extend the probed CLI list
  via a `probe_tools` array in `.claude/meta-learner.json`. Stdlib, fail-open,
  ASCII-safe output. (Aligns with Anthropic's SessionStart guidance: fast, concise,
  dynamic live context over static files.)

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
