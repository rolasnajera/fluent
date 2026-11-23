"""
Fluent path resolution for Google Antigravity.

Data directory resolution precedence:
  1. $FLUENT_DATA_DIR if set (absolutized)
  2. ./data if ./data/learner-profile.json exists (workspace cwd)
  3. <repo_root>/data if <repo_root>/data/learner-profile.json exists
  4. ./data if ./data directory exists (initial setup in cloned repo)
  5. ~/.gemini/fluent-data (global fallback)

Pure resolvers (data_dir / repo_root / backups_dir) do not create directories.
Call ensure_data_dir() before writing.
"""
from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path


def force_utf8_io() -> None:
    """Make stdout/stderr UTF-8 so emoji/CJK output doesn't crash on Windows."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


@lru_cache(maxsize=1)
def repo_root() -> Path:
    """Resolve the repository root directory (parent of scripts/)."""
    return Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def data_dir() -> Path:
    """Resolve the runtime data directory (pure — does not create it)."""
    env = os.environ.get("FLUENT_DATA_DIR")
    if env:
        return Path(env).expanduser().resolve()

    cwd_data = (Path.cwd() / "data").resolve()
    if (cwd_data / "learner-profile.json").exists():
        return cwd_data

    root_data = (repo_root() / "data").resolve()
    if (root_data / "learner-profile.json").exists():
        return root_data

    if cwd_data.is_dir():
        return cwd_data

    return (Path.home() / ".gemini" / "fluent-data").resolve()


def ensure_data_dir() -> Path:
    """Resolve the data directory and create it if missing. Call before writing."""
    d = data_dir()
    d.mkdir(parents=True, exist_ok=True)
    return d


@lru_cache(maxsize=1)
def backups_dir() -> Path:
    """Resolve the backups directory (always nested inside data_dir)."""
    return data_dir() / ".backups"


def ensure_backups_dir() -> Path:
    """Resolve the backups directory and create it if missing."""
    b = backups_dir()
    b.mkdir(parents=True, exist_ok=True)
    return b
