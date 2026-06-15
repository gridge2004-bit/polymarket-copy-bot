#!/usr/bin/env python3
"""
════════════════════════════════════════════════════════════
  POLYMARKET COPY BOT — Polymarket US Edition
  Watches:  LaBradfordSmith22 (international Polymarket)
  Executes: Your Polymarket US account (keyId + secretKey)
  No private key needed — CLOB_API_KEY + CLOB_SECRET is enough
════════════════════════════════════════════════════════════
"""

import os, re, time, json, logging, urllib.request, urllib.error
from dotenv import load_dotenv

# ── load config ──────────────────────────────────────────
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

CLOB_KEY_ID      = os.getenv('CLOB_API_KEY', '')      # Your Polymarket US Key ID
CLOB_SECRET_KEY  = os.getenv('CLOB_SECRET', '')        # Your Polymarket US Secret Key
COPY_WALLET      = os.getenv('COPY_WALLET', '0x9495425feeb0c250accb89275c97587011b19a27')
SCALE_FACTOR     = float(os.getenv('SCALE_FACTOR', '0.003'))
MAX_BET_USDC     = float(os.getenv('MAX_BET_USDC', '1.0'))
MIN_BET_USDC     = float(os.getenv('MIN_BET_USDC', '0.50'))
POLL_INTERVAL    = int(os.getenv('POLL_INTERVAL', '5'))
DRY_RUN          = os.getenv('DRY_RUN', 'true').lower() != 'false'
DATA_API         = f"https://data-api.polymarket.com/activity?user={COPY_WALLET}&limit=20"

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
slug_cache   = {}   # token_id → Polymarket US market slug (or '__NOT_FOUND__')
total_trades = 0
total_spent  = 0.0

# ── team nickname → city name lookup (for US market matching) ────────────────
_TEAM_NAMES = {
    # NBA
    'thunder': 'oklahoma city', 'okc': 'oklahoma city',
    'spurs': 'san antonio',
    'lakers': 'los angeles', 'laker': 'los angeles',
    'celtics': 'boston', 'celtic': 'boston',
    'warriors': 'golden state',
    'nets': 'brooklyn',
    'knicks': 'new york', 'knick': 'new york',
    'heat': 'miami',
    'bulls': 'chicago',
    'bucks': 'milwaukee',
    'suns': 'phoenix',
    'nuggets': 'denver',
    'clippers': 'los angeles',
    'sixers': 'philadelphia', '76ers': 'philadelphia',
    'hawks': 'atlanta',
    'hornets': 'charlotte',
    'cavaliers': 'cleveland', 'cavs': 'cleveland',
    'pistons': 'detroit',
    'pacers': 'indiana',
    'raptors': 'toronto',
    'magic': 'orlando',
    'wizards': 'washington',
    'pelicans': 'new orleans',
    'grizzlies': 'memphis',
    'jazz': 'utah',
    'timberwolves': 'minnesota', 'wolves': 'minnesota',
    'trail blazers': 'portland', 'blazers': 'portland',
    'kings': 'sacramento',
    'rockets': 'houston',
    'mavericks': 'dallas', 'mavs': 'dallas',
    # NFL
    'chiefs': 'kansas city',
    'eagles': 'philadelphia',
    'cowboys': 'dallas',
    'patriots': 'new england',
    'bills': 'buffalo',
    'dolphins': 'miami',
    'jets': 'new york',
    'giants': 'new york',
    'ravens': 'baltimore',
    'steelers': 'pittsburgh',
    'bengals': 'cincinnati',
    'browns': 'cleveland',
    'texans': 'houston',
    'colts': 'indianapolis',
    'jaguars': 'jacksonville',
    'titans': 'tennessee',
    'broncos': 'denver',
    'raiders': 'las vegas',
    'chargers': 'los angeles',
    'rams': 'los angeles',
    '49ers': 'san francisco',
    'seahawks': 'seattle',
    'cardinals': 'arizona',
    'packers': 'green bay',
    'bears': 'chicago',
    'lions': 'detroit',
    'vikings': 'minnesota',
    'saints': 'new orleans',
    'buccaneers': 'tampa bay', 'bucs': 'tampa bay',
    'falcons': 'atlanta',
    'panthers': 'carolina',
    # MLB
    'yankees': 'new york',
    'red sox': 'boston',
    'dodgers': 'los angeles',
    'cubs': 'chicago',
    'astros': 'houston',
    'mets': 'new york',
    'braves': 'atlanta',
    'phill	es': 'philadelphia',
    'nationals': 'washington',
    'marlins': 'miami',
    'brewers': 'milwaukee',
    'reds': 'cincinnati',
    'pirates': 'pittsburgh',
    'cardinals': 'st. louis',
    'padres': 'san diego',
    'giants': 'san francisco',
    'rockies': 'colorado',
    'diamondbacks': 'arizona', 'd-backs': 'arizona',
    'athletics': 'oakland', 'a\'s': 'oakland',
    'mariners': 'seattle',
    'angels': 'los angeles',
    'rangers': 'texas',
    'twins': 'minnesota',
    'white sox': 'chicago',
    'tigers': 'detroit',
    'royals': 'kansas city',
    'guardians': 'cleveland',
    'orioles': 'baltimore',
    'rays': 'tampa bay',
    'blue jays': 'toronto',
    # NHL
    'bruins': 'boston',
    'sabres': 'buffalo',
    'canadiens': 'montreal', 'habs': 'montreal',
    'senators': 'ottawa',
    'maple leafs': 'toronto',
    'thrashers': 'atlanta',
    'hurricanes': 'carolina',
    'panthers': 'florida',
    'lightning': 'tampa bay',
    'capitals': 'washington',
    'blackhawks': 'chicago',
    'red wings': 'detroit',
    'predators': 'nashville',
    'blues': 'st. louis',
    'coyotes': 'arizona',
    'avalanche': 'colorado',
    'stars': 'dallas',
    'wild': 'minnesota',
    'jets': 'winnipeg',
    'flames': 'calgary',
    'oilers': 'edmonton',
    'canucks': 'vancouver',
    'ducks': 'anaheim',
    'kings': 'los angeles',
    'sharks': 'san jose',
    'golden knights': 'vegas',
    'kraken': 'seattle',
}


def expand_team_names(title: str) -> str:
    """Replace nickname with city name so search matches Polymarket US format."""
    result = title
    for nickname, city in _TEAM_NAMES.items():
        pattern = re.compile(r'\b' + re.escape(nickname) + r'\b', re.IGNORECASE)
        if pattern.search(result):
            result = pattern.sub(city, result)
    return result


# ── stop-words for keyword extraction ────────────────────
_STOP = {
    'will', 'the', 'a', 'an', 'at', 'in', 'on', 'to', 'for', 'of', 'by',
    'vs', 'or', 'and', 'be', 'is', 'are', 'was', 'were', 'have', 'has',
    'had', 'do', 'does', 'did', 'not', 'win', 'lose', 'beat', 'over',
    'under', 'more', 'less', 'than', 'score', 'game', 'match', 'play',
    'first', 'last', 'next', 'this', 'that', 'which', 'who', 'what',
    'when', 'where', 'how', 'if', 'with', 'from', 'its', 'their', 'his',
    'her', 'our', 'get', 'make', 'take', 'come', 'go', 'see', 'know',
    'think', 'look', 'want', 'give', 'use', 'find', 'tell', 'ask',
}


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


def extract_proper_nouns(title: str) -> list:
    """
    Extract likely proper nouns (team names, player names, event names).
    These are capitalized words that aren't at the start of the sentence
    and aren't common articles/prepositions.
    """
    words = title.split()
    nouns = []
    for i, w in enumerate(words):
        clean = w.strip('.,!?;:()')
        if len(clean) > 2 and clean[0].isupper() and clean.lower() not in _STOP:
            nouns.append(clean)
    return nouns


def strip_market_type_prefix(title: str) -> str:
    """
    Remove spread/O/U prefixes so we can find the underlying game.
    e.g. "Spread: Arizona Diamondbacks (-4.5)" → "Arizona Diamondbacks"
         "Athletics vs. San Diego Padres: O/U 5.5" → "Athletics vs. San Diego Padres"
         "MLB: Colorado Rockies vs. Arizona Diamondbacks" → "Colorado Rockies vs. Arizona Diamondbacks"
    """
    # Remove leading league prefix (MLB:, NBA:, NFL:, MLS:, etc.)
    title = re.sub(r'^(MLB|NBA|NFL|NHL|MLS|Soccer|NFL|NCAAB|NCAAF):\s*', '', title, flags=re.IGNORECASE)
    # Remove spread prefix
    title = re.sub(r'^Spread:\s*', '', title, flags=re.IGNORECASE)
    # Remove everything after O/U marker (": O/U 5.5")
    title = re.sub(r':\s*O/U\s*[\d.]+.*$', '', title, flags=re.IGNORECASE)
    # Remove point spread parenthetical e.g. "(-4.5)" or "(+3)"
    title = re.sub(r'\s*\([+-]?[\d.]+\)', '', title)
    return title.strip()


def extract_keywords(title: str) -> list:
    """
    Extract meaningful search keywords from a market title.
    Returns proper nouns first (team names, etc.), then other significant words.
    """
    # Work from the stripped title so spread/O/U prefixes don't pollute keywords
    clean_title = strip_market_type_prefix(title)
    proper = extract_proper_nouns(clean_title)

    cleaned = re.sub(r"[^\w\s]", " ", title.lower())
    all_words = [w for w in cleaned.split()
                 if len(w) > 2 and w not in _STOP]

    proper_lower = {p.lower() for p in proper}
    extra = [w for w in all_words if w not in proper_lower]

    combined = proper + extra
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for w in combined:
        if w.lower() not in seen:
            seen.add(w.lower())
            unique.append(w)
    return unique[:10]


def title_similarity(a: str, b: str) -> float:
    """
    Word-overlap similarity between two titles.
    Returns 0.0–1.0 (fraction of shorter title's words found in the other).
    """
    words_a = set(re.sub(r"[^\w\s]", " ", a.lower()).split())
    words_b = set(re.sub(r"[^\w\s]", " ", b.lower()).split())
    if not words_a or not words_b:
        return 0.0
    # Remove very short/common words for scoring
    words_a = {w for w in words_a if len(w) > 2 and w not in _STOP}
    words_b = {w for w in words_b if len(w) > 2 and w not in _STOP}
    if not words_a or not words_b:
        return 0.0
    overlap = words_a & words_b
    return len(overlap) / min(len(words_a), len(words_b))


def get_market_slug(token_id: str, title: str, client) -> str | None:
    """
    Map an international Polymarket token to a Polymarket US market slug.

    Strategy:
      1. Extract proper nouns + keywords from the trade title
      2. Try multiple search queries (pairs/triples of top keywords)
      3. Score every result by title similarity
      4. Return the best match above a threshold
      5. Cache hits AND misses to avoid hammering the API
    """
    if token_id in slug_cache:
        cached = slug_cache[token_id]
        return None if cached == '__NOT_FOUND__' else cached

    # Strip spread/O/U prefix to get the underlying game title
    base_title = strip_market_type_prefix(title)
    if base_title != title:
        log.info(f"  🧹 Stripped to base title: '{base_title[:55]}'")

    # Expand team nicknames to city names for Polymarket US matching
    expanded_title = expand_team_names(base_title)
    if expanded_title != base_title:
        log.info(f"  🏙️  Expanded to city names: '{expanded_title[:60]}'")

    keywords = extract_keywords(title)
    expanded_keywords = extract_keywords(expanded_title)
    log.info(f"  🔑 Keywords extracted: {keywords[:6]}")

    # Build a ranked list of search queries to try
    search_queries = []

    # Best: expanded city names (e.g. "Oklahoma City San Antonio")
    if len(expanded_keywords) >= 2:
        search_queries.append(' '.join(expanded_keywords[:2]))
    if len(expanded_keywords) >= 1:
        search_queries.append(expanded_title[:60])
    # Also try original nickname keywords
    if len(keywords) >= 2:
        search_queries.append(' '.join(keywords[:2]))
    # Also try top 3 keywords
    if len(keywords) >= 3:
        search_queries.append(' '.join(keywords[:3]))
    # If title was stripped, also try the stripped title directly
    if base_title != title and len(base_title) > 5:
        search_queries.append(base_title[:60])
    # Try keywords 2-4 (skip the first, which might be a league prefix like "MLB")
    if len(keywords) >= 4:
        search_queries.append(' '.join(keywords[1:4]))
    # Fallback: raw first 4 words of base title
    raw = base_title.split()
    if len(raw) >= 3:
        search_queries.append(' '.join(raw[:4]))
    # Last resort: just first keyword alone
    if keywords:
        search_queries.append(keywords[0])

    # Deduplicate queries while preserving order
    seen_q = set()
    unique_queries = []
    for q in search_queries:
        if q not in seen_q:
            seen_q.add(q)
            unique_queries.append(q)

    best_slug  = None
    best_score = 0.0
    best_title = ''
    THRESHOLD  = 0.30   # At least 30% keyword overlap required

    for query in unique_queries:
        try:
            results = client.search.query({"query": query, "limit": 8})
            markets = results.get('markets', []) if isinstance(results, dict) else []

            for m in markets:
                m_title = (m.get('title') or m.get('name') or
                           m.get('question') or m.get('slug', ''))
               # Score against base_title (stripped) for better matching
                score = title_similarity(base_title, m_title)
                log.debug(f"    [{query}] → '{m_title[:45]}' score={score:.2f}")

                if score > best_score:
                    best_score = score
                    best_slug  = m.get('slug')
                    best_title = m_title

                # Short-circuit if we find a great match (≥60% overlap)
                if score >= 0.60:
                    break

        except Exception as e:
            log.warning(f"  ⚠ Search '{query}' failed: {e}")
            continue

        if best_score >= 0.60:
            break  # No need to try more queries

    if best_slug and best_score >= THRESHOLD:
        slug_cache[token_id] = best_slug
        log.info(f"  🔍 Matched US market: '{best_title[:50]}' → {best_slug} (score={best_score:.2f})")
        return best_slug

    # Cache the miss so we don't hammer the API for the same market
    slug_cache[token_id] = '__NOT_FOUND__'
    log.warning(
        f"  ⚠ No US market found for: '{title[:50]}' "
        f"(best_score={best_score:.2f}, best_candidate='{best_title[:40]}')"
    )
    return None


def map_intent(side: str, outcome: str) -> str:
    """
    Map international Polymarket side + outcome to Polymarket US order intent.
    BUY YES  → ORDER_INTENT_BUY_LONG   (buy YES shares)
    BUY NO   in ORDER_INTENT_BUY_SHORT  (buy NO = short YES)
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
    title    = trade.get('title', '?')[:65]
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

    # Find the US market slug using smart fuzzy matching
    slug = get_market_slug(token_id, title, client)
    if not slug:
        log.warning(f"  ✗ Skipping — no matching US market found for '{title[:40]}'")
        return

    # Calculate share quantity from USD amount
    # quantity (shares) = bet_usdc / price_per_share
    safe_price = max(price, 0.01)   # avoid divide by zero
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
            "tif": "TIME_IN_FORCE_IMMEDIATE_OR_CANCEL",
        })

        total_trades += 1
        total_spent  += bet_usdc
        log.info(
            f"  ✅ ORDER PLACED — {slug} | {intent} | "
            f"qty={quantity} shares @ ${price:.3f} | ${bet_usdc} | "
            f"id={order.get('orderId', order.get('id', '?'))}"
        )

    except NotFoundError:
        log.warning(f"  ✗ Market '{slug}' not found on Polymarket US (may differ by slug)")
        # Clear cache so a future trade on the same market can retry
        slug_cache.pop(token_id, None)
    except BadRequestError as e:
        log.error(f"  ✗ Bad order parameters: {e}")
    except AuthenticationError as e:
        log.error(f"  ✗ Auth failed — check CLOB_API_KEY and CLOB_SECRET: {e}")
    except Exception as e:
        log.error(f"  ✗ Execution error: {e}")


def poll(client=None):
    """Fetch latest trades from target wallet, mirror new ones."""
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
            # Only act on actual trades, not redemptions/settlements
            if t.get('type', 'TRADE') == 'TRADE' and t.get('side'):
                new_trades.append(t)

    if not new_trades:
        return

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
    log.info(f"  Target : {COPY_WALLET[:10]}... (LaBradfordSmith22)")
    log.info(f"  Scale  : {SCALE_FACTOR*100:.1f}% of their size (max ${MAX_BET_USDC}, min ${MIN_BET_USDC})")
    log.info(f"  Poll   : every {POLL_INTERVAL}s")
    log.info(f"  Mode   : {'🔴 DRY RUN (no real orders)' if DRY_RUN else '🟢 LIVE — REAL ORDERS ENABLED'}")
    log.info("────────────────────────────────────────────")
    log.info("  Credentials:")
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
            log.info("✅ Connected to Polymarket US — account verified")
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
