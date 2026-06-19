#!/usr/bin/env python3
"""Phase 4 (daily) — Grade trades against rules/strategy.md.

For each copied trade today, asks Claude to judge whether it followed the
written rules (GREEN) or violated them (RED), citing which rule. Falls back to
a deterministic rule-based grade when no API key is set.

Run: python3 -m assistant.grade_trades
"""
import os
from datetime import datetime, timezone

from . import journal
from .ai import ask
from .config import load_config, repo_path


def load_rules() -> str:
    try:
        with open(repo_path("rules", "strategy.md"), "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "(rules/strategy.md not found)"


def deterministic_grade(rows, cfg):
    """Heuristic grade without AI: copied trades that stayed in budget = GREEN."""
    a = cfg["alerts"]
    out = []
    for r in rows:
        if r.get("status") not in (journal.PLACED, journal.DRY_RUN):
            continue
        price = float(r.get("price") or 0.5)
        in_band = a["price_min"] <= price <= a["price_max"]
        grade = "🟢 GREEN" if in_band else "🔴 RED"
        why = "in price band" if in_band else "outside price band"
        out.append(f"- {grade} — {r.get('title','?')[:50]} @ {price:.2f} ({why})")
    return "\n".join(out) or "_No copied trades today._"


def main():
    cfg = load_config()
    midnight = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00")
    rows = journal.load(since=midnight)
    copied = [r for r in rows if r.get("status") in (journal.PLACED, journal.DRY_RUN)]

    det = deterministic_grade(rows, cfg)

    ai = ask(
        system=(
            "You grade prediction-market trades strictly against the trader's written "
            "rules. For each trade output GREEN (followed the plan) or RED (violated it) "
            "and cite the specific rule. Be terse."
        ),
        prompt=(
            "RULES:\n\n" + load_rules() + "\n\n"
            "TODAY'S COPIED TRADES (JSON lines):\n\n"
            + "\n".join(str(r) for r in copied) + "\n\n"
            "Grade each trade GREEN/RED with the rule cited, then one line on overall "
            "discipline today."
        ),
    )

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    body = f"# Trade Grading — {today}\n\n## Rule-based grade\n\n{det}\n"
    if ai:
        body += f"\n## AI grade (vs. rules/strategy.md)\n\n{ai}\n"
    else:
        body += "\n_(Set ANTHROPIC_API_KEY for rule-cited AI grading.)_\n"

    out_dir = repo_path(cfg["assistant"]["reports_dir"])
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"grades-{today}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)
    print(body)
    print(f"\n[written] {path}")


if __name__ == "__main__":
    main()
