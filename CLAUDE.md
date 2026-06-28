# CLAUDE.md

Guidance for Claude Code when working **on this repository** (developing the plugin itself).
Note: when this repo is *installed as a plugin* into another project, this `CLAUDE.md` is NOT loaded —
a plugin's CLAUDE.md is ignored. It matters only while editing the plugin here.

## What this repo is

`psotobverse-utils` is **not an application** — it is a Claude Code **plugin** (`.claude-plugin/plugin.json`)
of generic, project-agnostic engineering-workflow components: thin-verb skills, a shared knowledge core,
governance hooks, and generator/auditor subagents. The skills encode *how* to work with quality without
burning context. Extracted from `ms-rie-orchestrator` and stripped of domain bias.

The plugin runs in **both Claude Code and Cowork** — that is the whole reason it is a plugin and not a
`settings.json` hook bundle (settings.json hooks do not fire in Cowork; plugin hooks/subagents do).

## Commands (developing this repo)

```bash
# Markdown hygiene — this repo's de-facto lint/test gate (stdlib, no venv):
python hooks/doc_hygiene.py --all                # check every .md; exits non-zero on alerts
python hooks/doc_hygiene.py path/to/file.md      # check specific files

# Legacy Code-only vendor install (the plugin install is preferred — see README):
python install.py /path/to/target --check        # report drift vs canonical source; writes nothing
python install.py /path/to/target --force        # sync skills into target/.claude/skills/
```

There is **no test suite, linter config, or build step** here — the "code" is Markdown definitions plus
small stdlib Python hooks. `doc_hygiene.py --all` is the gate. `.pytest_cache/` is a stray artifact.

## Layout — thin verbs over a shared knowledge core (plugin form)

```
.claude-plugin/
  plugin.json            ← plugin manifest (name, version, hooks pointer)
  marketplace.json       ← marketplace entry (self-source)
skills/
  index/SKILL.md         ← organize/index the repo (corrects what doc_hygiene detects)
  goal/SKILL.md          ← goal-directed execution + file backlog
  reconcile/SKILL.md     ← 6-phase audit/improve cycle (generator != auditor)
  deliberate/SKILL.md    ← design the approach before a risky change
  tidy/SKILL.md          ← propose relocations for loose files (never auto-move)
  _shared/               ← NOT skills (no SKILL.md → loader ignores them)
    principles.md           the *why*  — 8 engineering principles
    robust-cycle.md         the *how*  — verify/checkpoint/meta-learn/stop primitives
    anti-hallucination.md   the *anti-failure* — claim→evidence, data-not-instructions, anti-sycophancy
hooks/
  hooks.json             ← plugin hook registration (runs in Code AND Cowork)
  nothing_loose.py       ← PreToolUse: deny writes outside the per-project allowlist; FAILS OPEN
  env_protect.py         ← PreToolUse: deny access to secret files (globally safe)
  comprehension_gate.py  ← PreToolUse: the one routing write-gate — ASK (not deny) when a phenotype
                            file is written before its required timeline/decision artifact; opt-in via routing.yml
  doc_hygiene.py         ← PostToolUse: detect (not correct) .md size/format/broken-ref
  stop_reminder.py       ← Stop: nudge checkpoint + meta-learning when git is dirty
  session_start.py / capture_signal.py / session_end.py  ← meta-learner (opt-in via .claude/meta-learner.json)
  coverage_sentinel.py   ← UserPromptSubmit: nudge /coverage on a substantive task (opt-in; once/session)
  policy_router.py       ← UserPromptSubmit: additive routing reminders (opt-in via routing.yml; never blocks)
  meta_util.py / routing_util.py  ← shared stdlib helpers (NOT entrypoints)
agents/
  executor.md            ← generator role (Bash, Read; haiku)
  explorer.md            ← auditor / read-only role (Read, Grep, Glob; haiku)
commands/
  tidy.md, sync-cowork.md
  comprehend.md          ← restate-before-act comprehension gate (+ runs /coverage)
  coverage.md            ← recall safety net: decorrelated lens panel over a doc catalog (union aggregation)
  cross-examine.md       ← adversarial multi-agent review panel (refute, vote, propose)
install.py               ← legacy Code-only vendor path (copies skills into target/.claude/skills/)
```

Three load-bearing conventions, in order of importance:

1. **Orthogonality (the specialization contract).** Skills are 100% generic: they say "run the
   project's test/lint/audit gates" and never name a concrete command or path. Each *consuming* project
   supplies the mapping in a "Skill specialization (overlay)" section of its own `CLAUDE.md`. If a
   project name, path, or tool name creeps into a skill, it is in the wrong place.

2. **Canonical source + sync.** The components in *this* repo are canonical. To change behavior, edit
   here first, bump `plugin.json` version, and (for vendor users) `install.py --force` / `--check`.

3. **`skills/_shared/` is plugin-bundled shared content.** Read by all five skills, so a per-skill
   `references/` would force 4–5× duplication. Skills reference it with a **relative prose path**
   (`` `../_shared/robust-cycle.md` ``), which resolves both as a plugin and when vendored into
   `.claude/skills/`. Do not "fix" `_shared/` into per-skill copies, and do not change the relative
   form back to a project-absolute `.claude/skills/...` path (that breaks under the plugin mount).

## The robust core (what the skills operationalize)

`_shared/robust-cycle.md` defines the recurring invariants:
- **Generator != auditor, in a separate context** — verification is a fresh subagent (the `explorer`)
  that did not see the generation reasoning and tries to *refute*. `/reconcile` phase 3 is canonical.
- **Stop by convergence — loop until dry** — close after **two consecutive** clean rounds; the other
  legitimate ending is *confirmed blocked*.
- **Evidence, not assertion** — every finding cites `file:line` or reproducible output.
- **Checkpoint-commit at milestones**, not every change (the `stop_reminder` hook nudges, never auto-commits).

## Governance hooks

`hooks/hooks.json` registers stdlib, non-blocking-by-default hooks that run in Code and Cowork. Two
guards (`nothing_loose`, `env_protect`) + `doc_hygiene` + `stop_reminder` are always-on; the
meta-learner trio (`session_start`/`capture_signal`/`session_end`) and the routing trio
(`policy_router`/`comprehension_gate`/`coverage_sentinel`) are **opt-in per project** (no-op unless the
project ships `.claude/meta-learner.json` or `.claude/policy/routing.yml`). Every hook **fails open**:
`nothing_loose` reads `$CLAUDE_PROJECT_DIR/.claude/policy/paths.allow.json` and allows when absent
(mandatory: the plugin is machine-global in Cowork and must not block unrelated projects). Routing is
**additive, never subtractive** — `policy_router` only *suggests*; the only interrupt is
`comprehension_gate`, which *asks* (never denies) and only on a write. `hooks/POLICIES.md` documents the
generic anti-drift baseline pattern and provenance.

## This repo governs itself (dogfooding)

`.claude/` opts this repo into the guardrails it ships: `constitution.md` (dogfoods `skills/_shared/`),
`knowledge-map.md`, `policy/paths.allow.json` (self-guard), and `meta-learner.json` (captures
plugin-authoring lessons to `learning/`). CI (`.github/workflows/validate-plugin.yml`) parses the
manifests + `hooks.json`, compiles the hooks, asserts they fail open on empty stdin, checks
skill/command frontmatter, and runs the `doc_hygiene` gate.

## Safe-edit protocol (the circularity is safe)

This repo is **factory and plugin at once** — its own installed hooks govern sessions that edit it.
That is safe dogfooding, not a dangerous loop, because:

- **The INSTALLED (cache) copy fires, never the source you edit here.** The `hooks.json` bootstrap
  resolves the install dir (`CLAUDE_PLUGIN_ROOT` → `installed_plugins.json` → cache glob) and runs that
  copy. So editing a hook's `.py` here is **inert until `claude plugin update`** — you cannot break the
  live session by editing a hook.
- **Per-project config is read live.** Adding `.claude/policy/paths.allow.json` here makes the installed
  `nothing_loose` guard this repo **immediately** (config is live; only hook *behavior* changes need an
  update). Blindaje is instant; risk is not.
- **Fail-open ⇒ no lock-out.** A malformed config or a thrown hook exits 0 and allows the write.
- **To test a hook change before it goes live:** pipe a simulated event to it
  (`echo '<json>' | python hooks/<hook>.py`) — never rely on the live hook to validate its own edit.
