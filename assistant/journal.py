"""Structured trade journal (Step 2 of the SMB build).

Append-only JSONL. Every decision the bot makes — copied, skipped, or errored —
gets one line here with enough context for later grading and autopsy. The
executor calls `record()`; the assistant scripts read with `load()`.

Designed to never raise into the polling loop: journaling failures are logged
and swallowed so they can't stop trading.
"""
import json
import os
from datetime import datetime, timezone

from .config import journal_path

# Decision outcomes
PLACED = "placed"        # live order submitted
DRY_RUN = "dry_run"      # simulated (DRY_RUN=true)
SKIPPED = "skipped"      # filtered out by alerts / no market match
ERROR = "error"          # execution failed

_FIELDS = (
    "ts", "status", "reason", "title", "token_id", "side", "outcome",
    "price", "their_size_usdc", "our_bet_usdc", "intent", "slug",
    "order_id", "pnl_usdc",
)


def record(**kwargs) -> None:
    """Append one decision to the journal. Best-effort; never raises."""
    try:
        row = {k: kwargs.get(k) for k in _FIELDS}
        if not row.get("ts"):
            row["ts"] = datetime.now(timezone.utc).isoformat()
        path = journal_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, separators=(",", ":")) + "\n")
    except Exception as e:  # noqa: BLE001 — must not break the trading loop
        try:
            import logging
            logging.getLogger(__name__).warning(f"journal write failed: {e}")
        except Exception:
            pass


def load(since=None) -> list:
    """Load journal rows. `since` is an optional ISO date/datetime string."""
    path = journal_path()
    rows = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if since and (row.get("ts") or "") < since:
                    continue
                rows.append(row)
    except FileNotFoundError:
        pass
    return rows


def summarize(rows: list) -> dict:
    """Deterministic counts/totals — works with no API key (Phase 1 fallback)."""
    placed = [r for r in rows if r.get("status") in (PLACED, DRY_RUN)]
    skipped = [r for r in rows if r.get("status") == SKIPPED]
    errors = [r for r in rows if r.get("status") == ERROR]
    spent = sum(float(r.get("our_bet_usdc") or 0) for r in placed)
    realized = sum(float(r.get("pnl_usdc") or 0) for r in rows
                   if r.get("pnl_usdc") is not None)
    skip_reasons = {}
    for r in skipped:
        skip_reasons[r.get("reason") or "?"] = skip_reasons.get(r.get("reason") or "?", 0) + 1
    return {
        "total": len(rows),
        "copied": len(placed),
        "skipped": len(skipped),
        "errors": len(errors),
        "spent_usdc": round(spent, 2),
        "realized_pnl_usdc": round(realized, 2),
        "skip_reasons": dict(sorted(skip_reasons.items(), key=lambda x: -x[1])),
    }
