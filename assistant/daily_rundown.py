#!/usr/bin/env python3
"""Phase 2 — Daily / pre-session rundown (SMB "Daily Market Rundown").

Pulls the followed wallet's recent activity from the Polymarket data API and
produces a prioritized briefing: what they've been doing, which markets are
active, and what our filter would do with each. Asks Claude to turn it into a
clean priority table + 2-3 sentences of context.

Run: python3 -m assistant.daily_rundown
"""
import json
import os
import urllib.request
from datetime import datetime, timezone

from .ai import ask
from .alerts import should_copy
from .config import load_config, repo_path

WALLET = os.getenv("COPY_WALLET", "0x9495425feeb0c250accb89275c97587011b19a27")
DATA_API = f"https://data-api.polymarket.com/activity?user={WALLET}&limit=40"


def fetch_activity():
    req = urllib.request.Request(DATA_API, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Origin": "https://polymarket.com",
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())


def build_digest(trades, cfg) -> str:
    scale = float(os.getenv("SCALE_FACTOR", "0.003"))
    mn, mx = float(os.getenv("MIN_BET_USDC", "0.50")), float(os.getenv("MAX_BET_USDC", "1.0"))
    rows = []
    for t in trades:
        if (t.get("type", "TRADE") != "TRADE") or not t.get("side"):
            continue
        their = float(t.get("usdcSize") or t.get("size") or 0)
        our = round(min(mx, max(mn, their * scale)), 2)
        ok, reason = should_copy(t, their, our, [], cfg)
        rows.append(
            f"| {t.get('title','?')[:48]} | {t.get('side','?')} {t.get('outcome','?')} "
            f"| {float(t.get('price',0)):.2f} | ${their:.0f} | ${our:.2f} | "
            f"{'✅ copy' if ok else '⏭ ' + reason[:28]} |"
        )
    header = (
        "| Market | Signal | Price | Their $ | Our $ | Filter |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
    )
    return header + "\n".join(rows[:25]) if rows else "_No recent trade activity._"


def main():
    cfg = load_config()
    try:
        trades = fetch_activity()
    except Exception as e:
        trades = []
        err = str(e)
    else:
        err = None

    digest = build_digest(trades, cfg) if not err else f"_Could not fetch activity: {err}_"

    context = ask(
        system=(
            "You are a prediction-market analyst preparing a trader's pre-session "
            "briefing. Be concise, neutral, and process-focused. Do not predict outcomes."
        ),
        prompt=(
            "Below is the recent activity of the wallet we copy, with how our filter "
            "would treat each signal:\n\n"
            f"{digest}\n\n"
            "Write 2-3 sentences of context: what themes/markets are they most active in, "
            "anything unusual in size or pacing, and what to watch this session."
        ),
    )

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    body = f"# Daily Rundown — {today}\n\n## Followed wallet — recent signals\n\n{digest}\n"
    if context:
        body += f"\n## Context\n\n{context}\n"
    else:
        body += "\n_(Set ANTHROPIC_API_KEY for AI context.)_\n"

    out_dir = repo_path(cfg["assistant"]["reports_dir"])
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"rundown-{today}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)
    print(body)
    print(f"\n[written] {path}")


if __name__ == "__main__":
    main()
