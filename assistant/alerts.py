"""Surgical multi-condition filter (Phase 3, from Jeff Holden's "custom alerts").

Instead of copying every signal the followed wallet emits, only act when a
trade passes ALL configured conditions. This is the prediction-market analogue
of "fire only if price breaks the ORB high on 1.5x volume above VWAP" — a
precise gate that cuts noise and enforces rules/strategy.md.

Pure functions, no side effects, no network — trivially testable.
"""
from .config import load_config


def _today_totals(todays_rows):
    """Count copied trades and spend from today's journal rows."""
    from .journal import PLACED, DRY_RUN
    copied = [r for r in todays_rows if r.get("status") in (PLACED, DRY_RUN)]
    spent = sum(float(r.get("our_bet_usdc") or 0) for r in copied)
    return len(copied), spent


def should_copy(trade: dict, their_size: float, our_bet: float,
                todays_rows=None, cfg=None):
    """Return (ok: bool, reason: str).

    `trade` is a raw Polymarket activity dict. `todays_rows` are journal rows
    from the current day, used for the daily budget checks.
    """
    a = (cfg or load_config())["alerts"]
    todays_rows = todays_rows or []

    side = (trade.get("side") or "").upper()
    title = (trade.get("title") or "")
    title_l = title.lower()
    try:
        price = float(trade.get("price", 0.5))
    except (TypeError, ValueError):
        price = 0.5

    # 1. Side
    allowed = [s.upper() for s in a.get("allowed_sides", ["BUY"])]
    if allowed and side not in allowed:
        return False, f"side {side} not in {allowed}"

    # 2. Conviction proxy (their size)
    if their_size < float(a.get("min_their_size_usdc", 0) or 0):
        return False, f"their size ${their_size:.0f} < min ${a['min_their_size_usdc']}"
    mx = a.get("max_their_size_usdc")
    if mx is not None and their_size > float(mx):
        return False, f"their size ${their_size:.0f} > max ${mx}"

    # 3. Price band
    if price < float(a.get("price_min", 0)) or price > float(a.get("price_max", 1)):
        return False, f"price {price:.2f} outside [{a['price_min']},{a['price_max']}]"

    # 4. Market type allow/block
    block = [b.lower() for b in a.get("title_blocklist", [])]
    if any(b in title_l for b in block):
        return False, "title in blocklist"
    allow = [w.lower() for w in a.get("title_allowlist", [])]
    if allow and not any(w in title_l for w in allow):
        return False, "title not in allowlist"

    # 5. Daily budget
    n_today, spent_today = _today_totals(todays_rows)
    if n_today >= int(a.get("max_trades_per_day", 10**9)):
        return False, f"daily trade cap {a['max_trades_per_day']} reached"
    if spent_today + our_bet > float(a.get("max_daily_spend_usdc", 10**9)):
        return False, f"daily spend cap ${a['max_daily_spend_usdc']} would be exceeded"

    return True, "passed all filters"
