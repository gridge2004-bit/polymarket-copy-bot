#!/usr/bin/env python3
"""
════════════════════════════════════════════════════════════
  POLYMARKET COPY BOT — mirrors LaBradfordSmith22 in real time
  Target:     0x9495425feeb0c250accb89275c97587011b19a27
  Scaling:    proportional to their size (capped at MAX_BET_USDC)
  Mode:       set DRY_RUN=false in .env to go live
════════════════════════════════════════════════════════════
"""

import os, time, json, logging, urllib.request, urllib.error
from datetime import datetime
from dotenv import load_dotenv

# ── load config ──────────────────────────────────────────
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

PRIVATE_KEY      = os.getenv('PRIVATE_KEY', '')
COPY_WALLET      = "0x9495425feeb0c250accb89275c97587011b19a27"  # LaBradfordSmith22
SCALE_FACTOR     = float(os.getenv('SCALE_FACTOR', '0.003'))     # 0.3% of their trade size
MAX_BET_USDC     = float(os.getenv('MAX_BET_USDC', '3.0'))       # hard cap per trade
MIN_BET_USDC     = float(os.getenv('MIN_BET_USDC', '0.50'))      # ignore tiny scaled bets
POLL_INTERVAL    = int(os.getenv('POLL_INTERVAL', '5'))           # seconds between polls
DRY_RUN          = os.getenv('DRY_RUN', 'true').lower() != 'false'
CLOB_HOST        = "https://clob.polymarket.com"
DATA_API         = f"https://data-api.polymarket.com/trades?user={COPY_WALLET}&limit=20"

# ── logging ───────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s │ %(levelname)s │ %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'bot.log'))
    ]
)
log = logging.getLogger(__name__)

# ── state ─────────────────────────────────────────────────
seen_hashes  = set()
total_trades = 0
total_spent  = 0.0

# ── helpers ───────────────────────────────────────────────
def fetch_json(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json',
        'Origin': 'https://polymarket.com',
    })
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode())


def scale_bet(their_size_usdc: float) -> float:
    """Scale their trade size to our bet, respecting min/max."""
    raw = their_size_usdc * SCALE_FACTOR
    return round(min(MAX_BET_USDC, max(MIN_BET_USDC, raw)), 2)


def get_best_price(token_id: str, side: str) -> float | None:
    """Fetch best ask (BUY) or best bid (SELL) from Polymarket CLOB order book."""
    try:
        data = fetch_json(f"{CLOB_HOST}/book?token_id={token_id}")
        if side == 'BUY':
            asks = data.get('asks', [])
            if asks:
                return float(sorted(asks, key=lambda x: float(x['price']))[0]['price'])
        else:
            bids = data.get('bids', [])
            if bids:
                return float(sorted(bids, key=lambda x: float(x['price']), reverse=True)[0]['price'])
    except Exception as e:
        log.warning(f"Book fetch failed for {token_id[:16]}...: {e}")
    return None


def execute_trade(trade: dict, bet_usdc: float):
    """Execute a mirrored trade via Polymarket CLOB API."""
    global total_trades, total_spent

    token_id  = trade['asset']
    side      = trade['side']       # 'BUY' or 'SELL'
    outcome   = trade.get('outcome', '?')
    title     = trade.get('title', '?')[:55]
    their_p   = trade.get('price', 0)

    # Get current live price
    live_price = get_best_price(token_id, side)
    if live_price is None:
        log.warning(f"  ✗ Could not fetch live price — skipping")
        return

    # Warn if price has moved significantly since their trade
    price_drift = abs(live_price - their_p)
    if price_drift > 0.10:
        log.warning(f"  ⚠ Price drifted {price_drift:.2f} since their trade ({their_p:.2f} → {live_price:.2f}) — still executing")

    log.info(f"  {'[DRY RUN] ' if DRY_RUN else ''}→ {side} {outcome} @ {live_price:.3f} | size ${bet_usdc} | {title}")

    if DRY_RUN:
        total_trades += 1
        total_spent  += bet_usdc
        log.info(f"  ✓ DRY RUN logged. Total simulated: {total_trades} trades, ${total_spent:.2f} spent")
        return

    # ── LIVE EXECUTION ────────────────────────────────────
    try:
        from py_clob_client.client import ClobClient
        from py_clob_client.clob_types import OrderArgs, OrderType
        from py_clob_client.order_builder.constants import BUY, SELL

        if not PRIVATE_KEY:
            log.error("PRIVATE_KEY not set in .env — cannot execute live trades")
            return

        client = ClobClient(
            host=CLOB_HOST,
            key=PRIVATE_KEY,
            chain_id=137,       # Polygon mainnet
            signature_type=0,   # EOA (standard for exported Privy key)
        )
        client.set_api_creds(client.derive_api_key())

        order_args = OrderArgs(
            token_id=token_id,
            price=live_price,
            size=bet_usdc,
            side=BUY if side == 'BUY' else SELL,
        )
        signed = client.create_order(order_args)
        resp   = client.post_order(signed, OrderType.FOK)   # Fill or Kill

        if resp and resp.get('success'):
            total_trades += 1
            total_spent  += bet_usdc
            log.info(f"  ✅ ORDER FILLED — {side} {outcome} @ {live_price:.3f} | ${bet_usdc} | order_id={resp.get('orderID','?')}")
        else:
            log.error(f"  ✗ Order rejected: {resp}")

    except ImportError:
        log.error("py-clob-client not installed. Run: pip install py-clob-client")
    except Exception as e:
        log.error(f"  ✗ Execution error: {e}")


def poll():
    """Fetch latest trades, detect new ones, mirror them."""
    try:
        trades = fetch_json(DATA_API)
    except Exception as e:
        log.warning(f"Poll failed: {e}")
        return

    new_trades = []
    for t in trades:
        key = t.get('transactionHash') or f"{t['timestamp']}_{t['asset']}"
        if key not in seen_hashes:
            seen_hashes.add(key)
            new_trades.append(t)

    if not new_trades:
        return

    # Process newest-first, but they arrive newest-first already
    for t in reversed(new_trades):   # oldest new trade first
        their_size = float(t.get('usdcSize') or t.get('size') or 0)
        bet        = scale_bet(their_size)
        ago        = int(time.time() - t['timestamp'])

        log.info(
            f"🎯 NEW TRADE │ {t.get('side','?')} {t.get('outcome','?')} │ "
            f"their_size=${their_size:.0f} → our_bet=${bet} │ "
            f"{ago}s ago │ {t.get('title','')[:50]}"
        )

        if their_size == 0:
            log.warning("  ✗ Zero size trade — skipping")
            continue

        execute_trade(t, bet)
        time.sleep(0.3)   # small gap between rapid trades


def main():
    log.info("════════════════════════════════════════════")
    log.info("  POLYMARKET COPY BOT — STARTING UP")
    log.info(f"  Target : LaBradfordSmith22")
    log.info(f"  Scale  : {SCALE_FACTOR*100:.1f}% of their size (max ${MAX_BET_USDC}, min ${MIN_BET_USDC})")
    log.info(f"  Poll   : every {POLL_INTERVAL}s")
    log.info(f"  Mode   : {'🔴 DRY RUN (no real orders)' if DRY_RUN else '🟢 LIVE — REAL ORDERS ENABLED'}")
    log.info("════════════════════════════════════════════")

    if not DRY_RUN and not PRIVATE_KEY:
        log.error("DRY_RUN=false but PRIVATE_KEY is not set. Add it to .env first.")
        return

    # Pre-seed seen hashes with current trades so we don't replay history
    log.info("Seeding history (ignoring past trades)...")
    try:
        existing = fetch_json(DATA_API)
        for t in existing:
            key = t.get('transactionHash') or f"{t['timestamp']}_{t['asset']}"
            seen_hashes.add(key)
        log.info(f"✓ Seeded {len(seen_hashes)} existing trades — bot will only act on NEW trades from now")
    except Exception as e:
        log.warning(f"Could not seed history: {e}")

    log.info("Watching for new trades...\n")
    while True:
        try:
            poll()
        except KeyboardInterrupt:
            log.info(f"\nBot stopped. Session: {total_trades} trades, ${total_spent:.2f} total")
            break
        except Exception as e:
            log.error(f"Unexpected error in poll loop: {e}")
        time.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    main()
