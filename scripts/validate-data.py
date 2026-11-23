#!/usr/bin/env python3
"""
Fluent Data Validation Hook (Antigravity PostToolUse)
Validates JSON structure and creates timestamped backups after write_file/edit_file operations.
"""
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fluent_paths import data_dir, force_utf8_io  # noqa: E402

force_utf8_io()
MAX_BACKUPS_PER_FILE = 10


def rotate_backups(file_path: str, keep: int = MAX_BACKUPS_PER_FILE) -> None:
    """Keep only the most recent `keep` .backup-* files for a given data file."""
    parent = Path(file_path).parent
    stem = Path(file_path).name
    backups = sorted(parent.glob(f"{stem}.backup-*"), reverse=True)
    for old in backups[keep:]:
        try:
            old.unlink()
        except OSError:
            pass


def extract_file_path(hook_input: dict) -> str:
    """Extract target file path from Antigravity PostToolUse payload."""
    tool_call = hook_input.get("toolCall", {})
    args = tool_call.get("args", {}) if isinstance(tool_call, dict) else {}
    return args.get("Path") or args.get("path") or ""


def main():
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        print("{}")
        sys.exit(0)

    file_path = extract_file_path(hook_input)
    if not file_path or not file_path.endswith(".json"):
        print("{}")
        sys.exit(0)

    # Only validate files inside the resolved data dir
    data = data_dir().resolve()
    try:
        resolved = Path(file_path).resolve()
        resolved.relative_to(data)
    except (ValueError, OSError):
        print("{}")
        sys.exit(0)

    if not os.path.exists(file_path):
        print("{}")
        sys.exit(0)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            json.load(f)

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = f"{file_path}.backup-{timestamp}"
        shutil.copy2(file_path, backup_path)
        rotate_backups(file_path)

        print("{}")
        sys.exit(0)

    except json.JSONDecodeError as e:
        print(f"[Fluent] ⚠️ WARNING: Invalid JSON in {file_path}: {e}", file=sys.stderr)
        print("{}")
        sys.exit(2)
    except Exception as e:
        print(f"[Fluent] Error processing {file_path}: {e}", file=sys.stderr)
        print("{}")
        sys.exit(1)


if __name__ == "__main__":
    main()
