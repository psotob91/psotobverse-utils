# Cowork hook testing manual (psotobverse-utils)

**Purpose:** verify that the plugin's governance hooks (`nothing_loose`,
`env_protect`) actually **enforce** inside Cowork after the v1.3.1 fix — or, if
they can't, that they **fail open** (allow everything) instead of blocking
everything. This is the re-test that closes datavidence **ADR-0002**.

This manual is deliberately step-by-step and tells you explicitly what to **DO**
and **NOT DO** at each step. Follow it top to bottom.

---

## 0. Answers to the usual questions (read once)

- **Do I need to run a plugin skill first (e.g. `/tidy`, `/reconcile`)?**
  **NO.** The hooks fire automatically on file operations. You do not invoke them.
- **Do I need `/psotobverse-utils:sync-cowork` before testing?**
  **NO.** The generated project already ships a working `.claude/COWORK_INSTRUCTIONS.md`
  stub. `sync-cowork` only upgrades that stub to the full charter; it is **not**
  a prerequisite for this test.
- **Do I need the `setup-cowork` skill (Anthropic onboarding)?**
  **NO.** That is generic Cowork onboarding (installs role-matched plugins, connects
  tools). It is not part of this test. Skip it.
- **Which model should I use?**
  Use the **cheapest** one — set Cowork's model selector to **Haiku 4.5** for all
  five test prompts. You are testing whether hooks *fire*, not output quality, so a
  small model is correct and saves tokens. **DO NOT** waste Opus/Sonnet here.

---

## 1. Deploy v1.3.1 so Cowork actually runs the fixed hooks

Cowork pulls the plugin from GitHub into its VM. The fix only takes effect once
the new version is published **and** Cowork re-downloads it.

1. **DO** confirm `psotobverse-utils` is pushed to GitHub at version **1.3.1**
   (`.claude-plugin/plugin.json` → `"version": "1.3.1"`). (If you are reading this
   right after the push, it is done.)
2. **DO** open Claude Desktop → **Cowork → Customize → Plugins**.
3. **DO** find `psotobverse-utils` and **Update** it (or remove + re-add the
   marketplace `psotob91/psotobverse-utils`, then reinstall). This forces the VM to
   fetch v1.3.1.
4. **DO NOT** assume an already-open Cowork session picked up the update. **Close
   and reopen** the Cowork project after updating the plugin.

> Why: an old cached v1.3.0 in the VM still has the broken `${CLAUDE_PLUGIN_ROOT}`
> command. If you test without updating, you are testing the old bug.

---

## 2. Use a GENERATED project, not the plugin or template repo

1. **DO** use a project made with `copier copy` (it has `.claude/constitution.md`
   and `.claude/policy/paths.allow.json` at its **root** — the hooks need the
   allowlist). A throwaway one is fine; e.g. the existing `Desktop\test-spike`.
2. **DO NOT** run the test inside the `psotobverse-utils` repo or the
   `datavidence-template-project` repo — neither has `.claude/policy/` at its root,
   so the guard has nothing to enforce and the test is meaningless.

---

## 3. Open the project and paste the rules (once)

1. **DO** Cowork → **Projects → + → Use an existing folder** → select the generated
   project's folder.
2. **DO** open `.claude/COWORK_INSTRUCTIONS.md`, copy the block between
   `[PASTE FROM HERE]` and `[END]`, and paste it into the project **Instructions**.
3. **DO** leave the whole project folder as the project **Context** (the default).
   **DO NOT** narrow Context to only `context/` — the hooks must reach
   `.claude/policy/paths.allow.json` at the root.
4. **DO** set the model selector (bottom of the Cowork chat) to **Haiku 4.5**.
5. **DO NOT** run `/init`. Ever. It would clobber the curated `CLAUDE.md`.

---

## 4. Run the five test prompts (type each, verbatim, in Cowork)

Type these one at a time as chat messages. After each, read what Cowork actually
did (look for a real block/allow, not just the model narrating).

| # | Type this prompt | PASS = you see |
|---|------------------|----------------|
| 1 | `Create a file loose.txt at the project root with the text: hi` | **Blocked** — guard denies a loose root file |
| 2 | `Create R/scratch.R with a one-line comment` | **Allowed** — `R/` is in the allowlist, file is created |
| 3 | `Read the .env file` | **Blocked** — `.env` is protected (note: only `.env.example` exists, so "no such file" is also acceptable) |
| 4 | `Tidy up any loose files` | Skill **proposes** moves, **does not** auto-move |
| 5 | `Audit this project for coherence` | `reconcile` **engages** (may read files / spawn explorer) |

- **DO** capture the exact behavior of #1 and #2 — those two decide the result.
- **DO NOT** trust the model's prose alone. In the previous (broken) run the model
  *said* "blocked by nothing_loose" when really the hook had crashed and blocked
  everything. Verify by checking #2: if a legitimate `R/` write is **allowed**,
  the hook is genuinely working; if #2 is **also blocked**, the hook is still
  failing.

---

## 5. Read the result (this is the decision)

- ✅ **#1 blocked AND #2 allowed** → Cowork exposes `CLAUDE_PLUGIN_ROOT`; **the
  fix gives full enforcement in Cowork.** This is the 100% outcome.
- ⚠️ **Everything allowed (nothing blocked, incl. #1)** → Cowork does **not** set
  `CLAUDE_PLUGIN_ROOT`; the guard is **failing open** — safe, but **no enforcement**
  in Cowork. (This still fixes the old "blocks everything" bug.) Next step: plan B
  (self-contained project hooks).
- ❌ **Everything blocked, incl. #2** → the VM is still on the old v1.3.0, or the
  update didn't take. Go back to step 1 (update + reopen).

---

## 6. Record the outcome (DO NOT skip)

1. **DO** append one line to the generated project's `learning/LEARNING_LOG.md`,
   e.g. `[2026-06-27][cowork] v1.3.1 re-test: #1 blocked, #2 allowed → full
   enforcement` (or the ⚠️ / ❌ variant you saw).
2. **DO** tell Claude Code in the **datavidence-template-project** the result so
   ADR-0002 can be finalized (Accepted as enforcing, or superseded with plan B).
3. **DO NOT** edit ADR-0002 from inside Cowork — record it from a Claude Code
   session in the template repo.

---

## Troubleshooting

- **Plugin not listed / old version:** Cowork → Customize → Plugins → Update; if
  stuck, remove the marketplace and re-add `psotob91/psotobverse-utils`, reinstall,
  then close/reopen the project.
- **`/psotobverse-utils:sync-cowork` says unknown command:** it only works in a
  **terminal** `claude` session started *after* the plugin was installed — not in
  the Cowork GUI. You do not need it for this test; skip it.
- **Nothing is ever blocked even for #1:** that is the fail-open (⚠️) outcome, not
  an error. Record it as such.
