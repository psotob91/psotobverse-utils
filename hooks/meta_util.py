"""Shared helpers for the meta-learner session hooks (stdlib only).

These hooks are GENERIC and live in the plugin, but they are OPT-IN per project:
they only act if the project (CLAUDE_PROJECT_DIR) ships a `.claude/meta-learner.json`
config. Absent config → the hook is a no-op (so the plugin never litters unrelated
repos with a learning/ tree). The config also carries the project's domain signal
patterns and which "consensus radar" file durable signals route to.

Every hook FAILS OPEN: any error returns 0 and never blocks a session.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone

CONFIG = (".claude", "meta-learner.json")
STATE = (".claude", "state", "session.json")
QUEUE = ("learning", "queue", "signals.jsonl")
SESSIONS_DIR = ("learning", "sessions")
SESSION_STATE_MD = ("SESSION_STATE.md",)

# Baked-in defaults used when the config omits a pattern list.
DEFAULT_CORRECTION = [
    r"\bno,", "no es así", "no era", "en realidad", r"\bactually\b",
    "that'?s (wrong|not right|incorrect|not)", "incorrect", "te equivocas",
    "estás? mal", "eso está mal", "mal hecho", "equivocad", "deberías", "debías",
    "should(n'?t)? have", "en vez de", "instead of", "fix this", "no deberías",
]
DEFAULT_CONSENSUS = [
    "guideline", "gu[ií]a", "consensus", "consenso", "controvers", "best practice",
    "mala práctica", "bad practice", "standard", "est[aá]ndar", "deprecat",
    "framework", "new (consensus|standard)",
]


def root() -> str:
    return os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


def p(*parts: str) -> str:
    return os.path.join(root(), *parts)


def load_config():
    """Return the project's meta-learner config, or None if not opted in."""
    try:
        with open(p(*CONFIG), encoding="utf-8") as f:
            cfg = json.load(f)
    except (OSError, ValueError):
        return None
    if cfg.get("enabled") is False:
        return None
    return cfg


def project_label(cfg: dict) -> str:
    return cfg.get("label") or os.path.basename(os.path.normpath(root())) or "project"


def radar(cfg: dict) -> str:
    return cfg.get("radar", "learning/CONSENSUS_WATCH.md")


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")


def git(*args: str) -> str:
    try:
        out = subprocess.run(
            ["git", *args], cwd=root(), capture_output=True, text=True, timeout=10
        )
        return out.stdout.strip() if out.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def branch() -> str:
    return git("rev-parse", "--abbrev-ref", "HEAD") or "(no-git)"


def read_state() -> dict:
    try:
        with open(p(*STATE), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def write_state(d: dict) -> None:
    path = p(*STATE)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2)
    os.replace(tmp, path)  # atomic


def read_stdin_json() -> dict:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw and raw.strip() else {}
    except (ValueError, OSError):
        return {}


def queue_count() -> int:
    try:
        with open(p(*QUEUE), encoding="utf-8") as f:
            return sum(1 for line in f if line.strip())
    except OSError:
        return 0


def read_head(path: str, n: int = 30) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            return "".join(f.readlines()[:n]).rstrip()
    except OSError:
        return ""
