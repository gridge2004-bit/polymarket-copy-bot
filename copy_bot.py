#!/usr/bin/env python3
"""
════════════════════════════════════════════════════════════
  POLYMARKET COPY BOT — Polymarket US Edition
  Watches:  LaBradfordSmith22 (international Polymarket)
  Executes: Your Polymarket US account (keyId + secretKey)
  No private key needed — CLOB_API_KEY + CLOB_SECRET is enough
════════════════════════════════════════════════════════════
"""

import os, time, json, logging, urllib.request, urllib.error
from dotenv import load_dotenv

# ── load config ──────────────────────────────────────────
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

CLOB_KEY_ID      = os.getenv('CLOB_API_KEY', '')      # Your Polymarket US Key ID
CLOB_SECRET_KEY  = os.getenv('CLOB_SECRET', '')        # Your Polymarket US Secret Key
COPY_WALLET      = "0x9495425feeb0c250accb89275c97587011b19a27"  # LaBradfordSmith22
SCALE_FACTOR     = float(os.getenv('SCALE_FACTOR', '0.003'))
MAX_BET_USDC     = float(os.getenv('MAX_BET_USDC', '3.0'))
MIN_BET_USDC     = float(os.getenv('MIN_BET_USDC', '0.50'))
POLL_INTERVAL    = int(os.getenv('POLL_INTERVAL', '5'))
DRY_RUN          = os.getenv('DRY_RUN', 'true').lower() != 'false'
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
slug_cache   = {}   # token_id → Polymarket US market slug
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
    raw = their_size_usdc * SCALE_FACTOR
    return round(min(MAX_BET_USDC, max(MIN_BET_USDC, raw)), 2)


def get_market_slug(token_id: str, title: str, client) -> str | None:
    """
    Map an international Polymarket token_id to a Polymarket US market slug.
    Uses title search with caching to minimize API calls.
    """
    if token_id in slug_cache:
        return slug_cache[token_id]

    try:
        # Search using first 6 words of the market title
        query = ' '.join(title.split()[:6])
        results = client.search.query({"query": query, "limit": 5})
        markets = results.get('markets', [])

        if markets:
            slug = markets[0].get('slug')
            if slug:
                slug_cache[token_id] = slug
                log.info(f"  🔍 Mapped to US market: {slug}")
                return slug
        log.warning(f"  ⚠ No US market found for: '{title[:50]}'")
    except Exception as e:
        log.warning(f"  ⚠ Market search failed for '{title[:40]}': {e}")

    return None


def map_intent(side: str, outcome: str) -> str:
    """
    Map international Polymarket side + outcome to Polymarket US order intent.
    BUY YES  → ORDER_INTENT_BUY_LONG   (buy YES shares)
    BUY NO   → ORDER_INTENT_BUY_SHORT  (buy NO = short YES)
    SELL YES → ORDER_INTENT_SELL_LONG  (sell/close YES position)
    SELL NO  → ORDER_INTENT_SELL_SHORT (sell NO shares)
    """
    out = outcome.upper().strip()
    is_yes = out in ('YES', '1', 'LONG', 'TRUE')

    if side == 'BUY' and is_yes:
        return 'ORDER_INTENT_BUY_LONG'
    elif side == 'BUY' and not is_yes:
        return 'ORDER_INTENT_BUY_SHORT'
    elif side == 'SELL' and is_yes:
        return 'ORDER_INTENT_SELL_LONG'
    else:
        return 'ORDER_INTENT_SELL_SHORT'


def execute_trade(trade: dict, bet_usdc: float, client=None):
    """Mirror a trade on Polymarket US."""
    global total_trades, total_spent

    token_id = trade['asset']
    side     = trade['side']
    outcome  = trade.get('outcome', 'YES')
    title    = trade.get('title', '?')[:55]
    price    = float(trade.get('price', 0.5))

    log.info(f"  {'[DRY RUN] ' if DRY_RUN else ''}→ {side} {outcome} @ {price:.3f} | ${bet_usdc} | {title}")

    if DRY_RUN:
        total_trades += 1
        total_spent  += bet_usdc
        log.info(f"  ✓ DRY RUN logged. Total: {total_trades} trades, ${total_spent:.2f} simulated")
        return

    # ── LIVE EXECUTION ─────────────────────────────────────
    if not client:
        log.error("❌ No Polymarket US client — cannot execute")
        return

    # Find the US market slug from the title
    slug = get_market_slug(token_id, title, client)
    if not slug:
        log.warning(f"  ✗ Skipping — no matching US market found")
        return

    # Calculate share quantity from USD amount
    # quantity (shares) = bet_usdc / price_per_share
    safe_price = max(price, 0.01)  # avoid divide by zero
    quantity   = round(bet_usdc / safe_price, 4)
    intent     = map_intent(side, outcome)

    try:
        from polymarket_us import NotFoundError, BadRequestError, AuthenticationError

        order = client.orders.create({
            "marketSlug": slug,
            "intent": intent,
            "type": "ORDER_TYPE_LIMIT",
            "price": {"value": str(round(price, 4)), "currency": "USD"},
            "quantity": quantity,
            "tif": "TIME_IN_FORCE_IMMEDIATE_OR_CANCEL",  # IOC = fast execution
        })

        total_trades += 1
        total_spent  += bet_usdc
        log.info(
            f"  ✅ ORDER PLACED — {slug} | {intent} | "
            f"qty={quantity} shares @ ${price:.3f} | ${bet_usdc} | "
            f"id={order.get('orderId', order.get('id', '?'))}"
        )

    except NotFoundError:
        log.warning(f"  ✗ Market '{slug}' not found on Polymarket US — possibly different name")
        # Clear cache so next attempt re-searches
        slug_cache.pop(token_id, None)
    except BadRequestError as e:
        log.error(f"  ✗ Bad order parameters: {e}")
    except AuthenticationError as e:
        log.error(f"  ✗ Auth failed — check CLOB_API_KEY and CLOB_SECRET: {e}")
    except Exception as e:
        log.error(f"  ✗ Execution error: {e}")


def poll(client=None):
    """Fetch latest trades from LaBradfordSmith22, mirror new ones."""
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

    for t in reversed(new_trades):  # oldest new trade first
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

        execute_trade(t, bet, client)
        time.sleep(0.3)


def build_client():
    """Create Polymarket US client if credentials are available."""
    if not CLOB_KEY_ID or not CLOB_SECRET_KEY:
        return None
    try:
        from polymarket_us import PolymarketUS
        return PolymarketUS(key_id=CLOB_KEY_ID, secret_key=CLOB_SECRET_KEY)
    except ImportError:
        log.error("polymarket-us not installed. Run: pip install polymarket-us")
        return None
    except Exception as e:
        log.error(f"Failed to create client: {e}")
        return None


def main():
    log.info("════════════════════════════════════════════")
    log.info("  POLYMARKET COPY BOT — POLYMARKET US EDITION")
    log.info(f"  Target : LaBradfordSmith22")
    log.info(f"  Scale  : {SCALE_FACTOR*100:.1f}% of their size (max ${MAX_BET_USDC}, min ${MIN_BET_USDC})")
    log.info(f"  Poll   : every {POLL_INTERVAL}s")
    log.info(f"  Mode   : {'🔴 DRY RUN (no real orders)' if DRY_RUN else '🟢 LIVE — REAL ORDERS ENABLED'}")
    log.info("────────────────────────────────────────────")
    log.info(f"  Credentials:")
    log.info(f"    CLOB_API_KEY (key_id)   : {'✅ set' if CLOB_KEY_ID else '❌ NOT SET'}")
    log.info(f"    CLOB_SECRET (secret_key): {'✅ set' if CLOB_SECRET_KEY else '❌ NOT SET'}")
    log.info("════════════════════════════════════════════")

    if not DRY_RUN and (not CLOB_KEY_ID or not CLOB_SECRET_KEY):
        log.error("❌ DRY_RUN=false but CLOB_API_KEY or CLOB_SECRET is missing.")
        log.error("   Add them in Railway → Variables and redeploy.")
        return

    # Build Polymarket US client
    client = build_client() if not DRY_RUN else None
    if not DRY_RUN and not client:
        log.error("❌ Could not connect to Polymarket US — check credentials")
        return

    if client:
        # Verify connectivity by fetching account
        try:
            balances = client.account.balances()
            log.info(f"✅ Connected to Polymarket US — account verified")
            log.info(f"   Balances: {balances}")
        except Exception as e:
            log.error(f"❌ Auth check failed: {e}")
            return

    # Seed history so we don't replay past trades
    log.info("Seeding history (ignoring past trades)...")
    try:
        existing = fetch_json(DATA_API)
        for t in existing:
            key = t.get('transactionHash') or f"{t['timestamp']}_{t['asset']}"
            seen_hashes.add(key)
        log.info(f"✓ Seeded {len(seen_hashes)} existing trades — bot will only act on NEW trades")
    except Exception as e:
        log.warning(f"Could not seed history: {e}")

    log.info("Watching for new trades...\n")
    while True:
        try:
            poll(client)
        except KeyboardInterrupt:
            log.info(f"\nBot stopped. Session: {total_trades} trades, ${total_spent:.2f} total")
            if client:
                client.close()
            break
        except Exception as e:
            log.error(f"Unexpected error in poll loop: {e}")
        time.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    main()
