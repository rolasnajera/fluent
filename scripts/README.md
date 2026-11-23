# Fluent Scripts & Antigravity Hooks

This directory contains the offline Python scripts that manage Fluent's local JSON databases and wire into **Google Antigravity's native lifecycle hooks** (`.agents/hooks.json`).

## Scripts Overview

| Script | Purpose |
|--------|---------|
| `fluent_paths.py` | Data directory resolution (`$FLUENT_DATA_DIR` → `./data/` → `<repo_root>/data/` → `~/.gemini/fluent-data/`) |
| `read-db.py` | Loads all 6 JSON databases + computed fields (`due_reviews_count`, `next_session_id`, `streak_active`) in one call |
| `update-db.py` | Atomically updates all 6 databases from a JSON session report on `stdin` (with automatic pre-write backups) |
| `ensure_data_dir.py` | Prints and creates the resolved data directory |
| `session-start.py` | Antigravity `SessionStart` hook — injects learner welcome, streak, and due review count |
| `validate-data.py` | Antigravity `PostToolUse` hook — validates JSON and rotates timestamped backups after `write_file` / `edit_file` |
| `session-end.py` | Creates a daily snapshot backup in `.backups/YYYYMMDD/` and prints session stats |

## Antigravity Hooks (`.agents/hooks.json`)

Antigravity automatically discovers `.agents/hooks.json` in the workspace root:

- **`SessionStart`** → runs `scripts/session-start.py`, returning a `systemMessage` step with your streak and due review count.
- **`PostToolUse`** (matcher: `write_file|edit_file`) → runs `scripts/validate-data.py`, validating any edited JSON inside the data directory and keeping the 10 most recent timestamped backups.

## Data Privacy

All scripts use only the Python 3 standard library (`json`, `os`, `pathlib`, `shutil`, `datetime`, `math`, `re`). Zero network requests, zero telemetry, zero external dependencies.
