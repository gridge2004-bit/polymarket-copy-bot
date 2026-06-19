#!/usr/bin/env python3
"""Phase 1 — Nightly recap.

Reads today's journal, prints a deterministic digest (what fired, what was
skipped and why, simulated/real spend), then asks Claude for a short coaching
note. Writes the result to reports/recap-YYYY-MM-DD.md.

Run: python3 -m assistant.nightly_recap
"""
import os
from datetime import datetime, timezone

from . import journal
from .ai import ask
from .config import load_config, repo_path


def build_digest(rows: list) -> str:
    s = journal.summarize(rows)
    lines = [
        f"- Decisions logged: **{s['total']}**",
        f"- Copied: **{s['copied']}**  |  Skipped: **{s['skipped']}**  |  Errors: **{s['errors']}**",
        f"- Spend (sim/real): **${s['spent_usdc']}**",
        f"- Realized P&L (where known): **${s['realized_pnl_usdc']}**",
    ]
    if s["skip_reasons"]:
        lines.append("- Skip reasons:")
        for reason, n in s["skip_reasons"].items():
            lines.append(f"    - {reason}: {n}")
    return "\n".join(lines)


def main():
    cfg = load_config()
    midnight = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00")
    rows = journal.load(since=midnight)
    digest = build_digest(rows)

    note = ask(
        system=(
            "You are a disciplined trading coach for a Polymarket copy-trading bot. "
            "Be concise and specific. Focus on process adherence, not predictions."
        ),
        prompt=(
            "Here is today's copy-bot activity digest:\n\n"
            f"{digest}\n\n"
            "In 3-5 bullets: what went well, what looks off, and the single most "
            "important thing to check tomorrow. If there were many skips for one "
            "reason, say whether the filter is too tight or correctly protective."
        ),
    )

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    body = f"# Nightly Recap — {today}\n\n## Numbers\n\n{digest}\n"
    if note:
        body += f"\n## Coach's note\n\n{note}\n"
    else:
        body += "\n_(Set ANTHROPIC_API_KEY for an AI coaching note.)_\n"

    out_dir = repo_path(cfg["assistant"]["reports_dir"])
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"recap-{today}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)
    print(body)
    print(f"\n[written] {path}")


if __name__ == "__main__":
    main()
