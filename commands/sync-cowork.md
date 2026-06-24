---
description: Generate or refresh .claude/COWORK_INSTRUCTIONS.md from the project's constitution and CLAUDE.md overlay, so Cowork gets rule parity with Claude Code.
---

Cowork does NOT auto-read `CLAUDE.md` or `.claude/`. This command produces the bridge file the user
pastes into the Cowork project **Instructions** field.

Steps:
1. Read `.claude/constitution.md` (the charter) and the `CLAUDE.md` "Read first" order + the Skill
   specialization overlay table. Do not invent content — use what is there.
2. Write `.claude/COWORK_INSTRUCTIONS.md` containing a single delimited paste block
   (`[PASTE FROM HERE]` … `[END]`) that restates, verbatim and concisely:
   - the read-first order (constitution -> policies/00-index -> knowledge-map -> PROJECT_BRIEF);
   - the core charter rules: cite-or-IDK / do-not-invent, mark uncertainty, chain-of-verification,
     ask before irreversible or outward actions, write outputs to `outputs/`;
   - the project's overlay (generic gate -> concrete command);
   - a one-line note that Cowork does not auto-load CLAUDE.md, so these instructions stand in for it.
3. Embed a short `source-hash:` line (a hash of constitution.md) so staleness can be detected later.
4. Tell the user the absolute path to `.claude/COWORK_INSTRUCTIONS.md` and instruct them to open it,
   copy the paste block, and paste it into Cowork → their project → Instructions. Also remind them to
   add the `context/` folder as Cowork "Context".

$ARGUMENTS
