---
name: premarket-rundown
description: Build a prioritized pre-session trading briefing (the SMB "Daily Market Rundown"). Use when the user asks for a morning rundown, pre-market game plan, watchlist prioritization, "what should I watch today", or pastes overnight headlines / pre-market data and wants it turned into a ranked watchlist. Turns raw inputs into one prioritized table in minutes instead of an hour.
---

# Pre-Market Rundown

Replicates SMB Capital's pre-market automation (Jeff Holden, practice #2; "I
Automated My Pre-Market Research With AI"). Goal: process overnight info into a
single prioritized briefing **before the open** — not predictions, prioritization.

## Inputs to ask for (only if missing)
- Overnight/pre-market headlines, gainers/losers, gap scanners, earnings.
- The user's traded markets/tickers and time zone.
- Their setups (default: ORB, VWAP reclaim, momentum continuation).
- If a `rules/strategy.md` exists in the repo, read it and respect its filters.

## Process
1. Parse every name out of the pasted data.
2. For each, capture: **catalyst/news driver**, **pre-market action** (gap %,
   relative volume, strength/weakness), **key levels** (support/resistance,
   prior day H/L, premarket H/L), and **setup potential** (which pattern could
   trigger).
3. Score priority **High / Medium / Low** by catalyst strength × clean technical
   level × liquidity. Be skeptical; most names are Low.

## Output (always this shape)
A markdown table, one row per name, **sorted High first**:

| Ticker | Priority | Catalyst | Pre-mkt action | Key levels | Setup to watch |
|---|---|---|---|---|---|

Then **2–3 sentences** of overall market context (tone, index posture, the one
theme of the day). Then a one-line **"If I only watch 3"** shortlist.

## Rules
- Never give a buy/sell call or price target. You prioritize; the trader decides.
- If data is thin, say so and mark names Low rather than inventing catalysts.
- Keep it skimmable — a trader reads this in under 60 seconds before the bell.
