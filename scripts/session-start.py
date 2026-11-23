#!/usr/bin/env python3
"""
Fluent Session Start Hook (Antigravity SessionStart)
Injects learner stats and due review status at the start of a conversation.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fluent_paths import data_dir, force_utf8_io  # noqa: E402

force_utf8_io()


def build_status_lines() -> list[str]:
    data = data_dir()
    profile_path = data / "learner-profile.json"

    if not profile_path.exists():
        return [
            "[Fluent] 🌍 Welcome to Fluent — The AI Language Learning Kit for Google Antigravity!",
            "[Fluent] 📝 Run /fluent-setup (or ask to set up your profile) to get started.",
        ]

    lines = []
    try:
        with open(profile_path, "r", encoding="utf-8") as f:
            profile = json.load(f)

        learner = profile.get("learner", {})
        name = learner.get("name", "Learner")
        target_lang = learner.get("target_language", "your target language")
        current_level = learner.get("current_level", "...")
        target_level = learner.get("target_level", "...")
        streak = profile.get("current_streak_days", 0)

        lines.append(f"[Fluent] 🌍 Welcome back, {name}!")
        lines.append(f"[Fluent] 📚 Learning: {target_lang} ({current_level} → {target_level}) | 🔥 Streak: {streak} days")

        sr_path = data / "spaced-repetition.json"
        if sr_path.exists():
            try:
                with open(sr_path, "r", encoding="utf-8") as f:
                    sr_data = json.load(f)

                today = datetime.now().strftime("%Y-%m-%d")
                due_count = 0
                items = sr_data.get("items", {})
                iterable = items.values() if isinstance(items, dict) else items
                for item in iterable:
                    due = item.get("due_date") or item.get("next_review_date", "")
                    if due and due <= today:
                        due_count += 1

                if due_count > 0:
                    lines.append(f"[Fluent] 📅 {due_count} items due for review today — run /fluent-review!")
            except Exception:
                pass
    except Exception as e:
        lines.append(f"[Fluent] Error loading profile: {e}")

    return lines


def main():
    hook_mode = False
    if not sys.stdin.isatty():
        try:
            payload = json.load(sys.stdin)
            if isinstance(payload, dict) and ("hookEventName" in payload or "conversationId" in payload):
                hook_mode = True
        except Exception:
            pass

    message = "\n".join(build_status_lines())

    if hook_mode:
        output = {
            "injectSteps": [
                {
                    "systemMessage": {
                        "systemMessage": message,
                    }
                }
            ]
        }
        json.dump(output, sys.stdout, ensure_ascii=False)
        print()
    else:
        print(message)

    sys.exit(0)


if __name__ == "__main__":
    main()
