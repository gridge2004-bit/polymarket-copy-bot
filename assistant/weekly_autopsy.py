#!/usr/bin/env python3
"""Phase 4 (weekly) — Trade autopsy.

Feeds the last 7 days of journal to Claude and asks for the SINGLE most
important recurring mistake plus one concrete fix (the SMB "autopsy"). Appends
the lesson to reviews/weekly.md so improvements compound over time.

Run: python3 -m assistant.weekly_autopsy
"""
import os
from datetime import datetime, timedelta, timezone

from . import journal
from .ai import ask
from .config import load_config, repo_path


def main():
    cfg = load_config()
    since = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%dT00:00:00")
    rows = journal.load(since=since)
    s = journal.summarize(rows)

    digest = (
        f"- Window: last 7 days\n"
        f"- Decisions: {s['total']} | copied {s['copied']} | skipped {s['skipped']} | errors {s['errors']}\n"
        f"- Spend: ${s['spent_usdc']} | realized P&L: ${s['realized_pnl_usdc']}\n"
        f"- Top skip reasons: {s['skip_reasons']}\n"
    )

    ai = ask(
        system=(
            "You are a head of trader development running a weekly autopsy. Identify the "
            "ONE highest-leverage recurring mistake and give exactly one concrete, "
            "actionable fix (a config change, a rule edit, or a process change). Be direct."
        ),
        prompt=(
            "Weekly copy-bot digest:\n\n" + digest + "\n"
            "Raw decisions (JSON lines):\n\n"
            + "\n".join(str(r) for r in rows[-200:]) + "\n\n"
            "Output:\n1. The single biggest recurring issue.\n2. One concrete fix.\n"
            "3. A metric to confirm the fix worked next week."
        ),
        max_tokens=900,
    )

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    entry = f"## Autopsy — week ending {today}\n\n{digest}\n"
    entry += (ai + "\n") if ai else "_(Set ANTHROPIC_API_KEY for the AI autopsy.)_\n"
    entry += "\n---\n\n"

    out_dir = repo_path("reviews")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "weekly.md")
    # Prepend newest on top, keeping history.
    prior = ""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            prior = f.read()
    else:
        prior = "# Weekly Autopsies\n\n"
    head, _, rest = prior.partition("\n\n")
    with open(path, "w", encoding="utf-8") as f:
        f.write(head + "\n\n" + entry + rest)
    print(entry)
    print(f"[updated] {path}")


if __name__ == "__main__":
    main()
