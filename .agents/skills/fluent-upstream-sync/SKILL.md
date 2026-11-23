---
name: fluent-upstream-sync
description: >-
  Selectively sync non-Claude improvements from the upstream Fluent repository
  (m98/fluent) into this Google Antigravity fork. Use when the user asks to
  check for upstream updates, review diffs against upstream/main, or port new
  upstream commits while preserving Antigravity structure and local changes.
---

# Upstream Sync (Antigravity Fork)

Selectively review and port non-Claude improvements from `upstream/main` (`m98/fluent`) into this Antigravity-native repository without overwriting local customizations.

## When to Use

- The user asks to check, review, or sync with upstream changes (`upstream/main`).
- Never auto-run during a language-learning session.

## Instructions

### 1. Find the last synced upstream commit

Look for the most recent `Synced-upstream:` trailer in the git history:

```bash
git log --grep="Synced-upstream:" -n 1
```

- Extract the `<last_synced_sha>` from `Synced-upstream: <sha> (...)`.
- If no `Synced-upstream:` trailer exists yet, check `git log --oneline -n 10` or ask the user which upstream commit/tag was last synced.

### 2. Fetch upstream and list new commits

```bash
git fetch upstream
git log <last_synced_sha>..upstream/main --oneline --stat
```

If there are no new commits, report that the fork is already up to date and stop.

### 3. Identify locally customized files to protect

Before porting anything, check which files have been customized locally on this fork (for example, `.github/workflows/tests.yml`, `GEMINI.md`, `README.md`, `AGENTS.md`, or custom skills/scripts):

```bash
git log --oneline --stat --no-merges <last_synced_sha>..HEAD
```

**Protection rule:**
- Do **not** blindly overwrite or revert files the user has customized locally.
- If an upstream commit modifies a file that has local customizations, skip the conflicting change or explicitly ask the user before applying it.

### 4. Filter and map upstream changes

Inspect each new upstream commit (`git show <sha>`). Never run a blind `git merge upstream/main` or `git pull upstream main`.

**Skip (Claude-specific):**
- `.claude/`, `.claude-plugin/`, `CLAUDE.md`
- Claude-only hook mechanics (e.g., Claude JSONL transcript parsers like `answer-leak-guard.py`, `settings.json` hooks)
- `disable-model-invocation` / Claude `Skill` tool workarounds
- Claude plugin version bumps or release-only commits

**Port (non-Claude improvements), mapping paths to Antigravity:**
- `.claude/hooks/*.py` → `scripts/*.py` (excluding Claude-only hooks)
- `.claude/skills/<name>/SKILL.md` → `.agents/skills/<name>/SKILL.md` (keep Antigravity YAML frontmatter and `scripts/` paths)
- `.claude/references/*` → `.agents/references/*`
- `tests/`, `docs/DB_SCRIPTS.md`, `data-examples/`, `LEARNING_SYSTEM.md`, `PRACTICE.md` → port directly, adapting any remaining Claude path/tool references to Antigravity.

### 5. Verify after porting

Run the test suite and config validation:

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
python3 -c "import json, pathlib; json.loads(pathlib.Path('.agents/hooks.json').read_text(encoding='utf-8'))"
```

If `.github/workflows/tests.yml` was touched, also validate YAML syntax (`ruby -ryaml -e "YAML.load_file('.github/workflows/tests.yml')"`).

### 6. Record the sync point in the commit message

When committing (or suggesting the commit command to the user), always include the `Synced-upstream:` trailer pointing to the latest `upstream/main` commit reviewed:

```text
chore: port upstream <version-or-summary> improvements to Antigravity

Synced-upstream: <full_upstream_head_sha> (<tag-if-any>)
```
