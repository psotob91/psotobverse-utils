"""Machine environment probe (stdlib) — run ONCE per machine, then reuse.

Detects the shell(s), available CLIs, and OS quirks ONE time and caches the
result machine-globally at ~/.claude/environment.json (+ a human-readable
environment.md). Every SessionStart then injects a concise summary read from the
cache instead of re-probing — so the agent knows what the machine has (and what
to avoid, e.g. PowerShell 5.1 `&&`) without rediscovering it each session.

Refresh by deleting ~/.claude/environment.json (e.g. after installing a tool).
Assumes machine stability (Anthropic SessionStart guidance: keep it fast; cache
one-time setup; inject concise live context). Fails open: any error → "".
"""
from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
from datetime import datetime, timezone

_HOME = os.path.expanduser("~")
CACHE = os.path.join(_HOME, ".claude", "environment.json")
CACHE_MD = os.path.join(_HOME, ".claude", "environment.md")

# CLIs worth knowing about. A project extends this via meta-learner.json "probe_tools".
DEFAULT_TOOLS = [
    "git", "gh", "python", "python3", "uv", "pip", "copier", "node", "npm",
    "Rscript", "R", "make", "jq", "rg", "docker", "quarto",
]

# Best-effort install hints (Windows-first, since that is the common case here).
INSTALL_HINTS = {
    "gh": "winget install GitHub.cli   (or scoop install gh)",
    "uv": "pip install uv   (or winget install astral-sh.uv)",
    "copier": "uv tool install copier",
    "jq": "winget install jqlang.jq",
    "rg": "winget install BurntSushi.ripgrep.MSVC",
    "node": "winget install OpenJS.NodeJS",
    "Rscript": "install R from https://cran.r-project.org",
    "docker": "install Docker Desktop",
    "quarto": "winget install Posit.Quarto",
    "make": "scoop install make   (or choco install make; Git Bash does not bundle it)",
}


def _run(cmd) -> str:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
        return (out.stdout or out.stderr or "").strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def _ps() -> dict | None:
    exe = "pwsh" if shutil.which("pwsh") else ("powershell" if shutil.which("powershell") else None)
    if not exe:
        return None
    v = _run([exe, "-NoProfile", "-Command", "$PSVersionTable.PSVersion.ToString()"])
    return {"exe": exe, "version": v or "?"}


def probe(cfg: dict | None = None) -> dict:
    cfg = cfg or {}
    tools = list(dict.fromkeys(DEFAULT_TOOLS + (cfg.get("probe_tools") or [])))
    found = {t: bool(shutil.which(t)) for t in tools}
    osname = platform.system()

    data = {
        "os": f"{osname} {platform.release()}",
        "probed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "shells": {},
        "tools": found,
        "missing": [t for t, ok in found.items() if not ok],
        "quirks": [],
        "suggest": {},
    }

    ps = _ps()
    if ps:
        data["shells"]["powershell"] = ps
    if shutil.which("bash"):
        data["shells"]["bash"] = True

    if ps and str(ps.get("version", "")).startswith("5"):
        data["quirks"].append(
            "Windows PowerShell 5.1: no && / || / ternary / ?? / ?. — chain with ';' and "
            "'if ($?) { ... }'; prefer the Bash tool for POSIX one-liners; use 2>$null not 2>/dev/null."
        )
    if osname == "Windows":
        data["quirks"].append(
            "Windows: read env vars as $env:VAR (PS) not %VAR%; use forward-slash or C:/ paths in Python."
        )

    for t in data["missing"]:
        if t in INSTALL_HINTS:
            data["suggest"][t] = INSTALL_HINTS[t]
    return data


def _write(data: dict) -> None:
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    tmp = CACHE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, CACHE)
    # human-readable mirror
    present = [t for t, ok in data["tools"].items() if ok]
    md = [
        "# Machine environment (auto-probed once; delete this file's .json sibling to refresh)",
        "",
        f"- **Probed:** {data['probed_at']}",
        f"- **OS:** {data['os']}",
        f"- **Shells:** {', '.join(k + ' ' + (v.get('version','') if isinstance(v, dict) else '') for k, v in data['shells'].items()) or '(none detected)'}",
        f"- **Tools present:** {', '.join(present) or '(none)'}",
        f"- **Missing:** {', '.join(data['missing']) or '(none)'}",
        "",
        "## Quirks to respect",
    ]
    md += [f"- {q}" for q in data["quirks"]] or ["- (none)"]
    if data["suggest"]:
        md += ["", "## Suggested installs (only if you need the tool)"]
        md += [f"- `{t}`: {hint}" for t, hint in data["suggest"].items()]
    try:
        with open(CACHE_MD, "w", encoding="utf-8") as f:
            f.write("\n".join(md) + "\n")
    except OSError:
        pass


def summary(data: dict) -> str:
    present = [t for t, ok in data["tools"].items() if ok]
    lines = [f"Machine env (cached {data.get('probed_at', '?')}): {data.get('os', '?')}."]
    sh = []
    if "powershell" in data.get("shells", {}):
        sh.append("PowerShell " + str(data["shells"]["powershell"].get("version", "?")))
    if data.get("shells", {}).get("bash"):
        sh.append("bash")
    if sh:
        lines.append("Shells: " + ", ".join(sh) + ".")
    lines.append("CLIs present: " + (", ".join(present) or "none") + ".")
    if data.get("missing"):
        lines.append("CLIs missing: " + ", ".join(data["missing"]) + " (see ~/.claude/environment.md for install hints).")
    for q in data.get("quirks", []):
        lines.append("(!) " + q)  # ASCII only — raw print to a cp1252 console must not crash
    return "\n".join(lines)


def ensure(cfg: dict | None = None) -> str:
    """Return a concise env summary. Probe + cache only on first machine run."""
    try:
        if os.path.exists(CACHE):
            with open(CACHE, encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = probe(cfg)
            _write(data)
        return summary(data)
    except Exception:
        return ""


if __name__ == "__main__":  # manual: python env_probe.py [--force]
    import sys
    if "--force" in sys.argv and os.path.exists(CACHE):
        os.remove(CACHE)
    print(ensure({}))
