---
name: premarket-rundown
description: Build a prioritized pre-session macro briefing for an index-futures trader (NQ/MNQ), modeled on the SMB "Daily Market Rundown". Use when the user asks for a morning rundown, pre-market game plan, "what should I watch today", a week-ahead, or pastes overnight data and wants it turned into a ranked plan. Covers overnight sessions, the economic calendar, sector/crypto risk tone, and key NQ levels — prioritization, not predictions.
---

# Pre-Market Rundown — Futures (NQ/MNQ)

Replicates SMB Capital's pre-market automation (Jeff Holden, practice #2) tuned
for an index-futures day trader who watches the whole tape. Goal: turn overnight
information into one prioritized briefing **before the cash open** — the morning
macro read that sets the day's bias and levels.

## Inputs (pull what's provided; fetch/ask for the rest)
- **Overnight action:** ES/NQ globex range, Asia + Europe session behavior, gap.
- **Economic calendar (highest priority for futures):** today's releases with
  times in ET — CPI/PPI, FOMC/Fed speakers, jobs (NFP/claims), PMIs, GDP, plus
  any 8:30/10:00 prints. Flag the session-defining event and its time.
- **Risk tone:** DXY, US10Y yields, oil/gold, **crypto (BTC/ETH) as 24h risk
  proxy**, VIX.
- **Sector rotation / leadership:** which sectors and mega-caps (NVDA, AAPL,
  MSFT, etc.) are leading or lagging pre-market; anything moving the NQ weights.
- **Catalysts:** overnight headlines, notable earnings (esp. mega-cap after/before).
- Read `rules/futures_strategy.md` (your plan) and respect its session windows,
  bias inputs, and no-trade rules (e.g. "no new trades before red-folder news").

## Process
1. Establish the **day's bias**: risk-on / risk-off / two-sided, with the
   evidence (overnight trend, yields, crypto, breadth).
2. Mark **NQ key levels**: overnight high/low, prior day H/L and value area,
   globex VWAP, the obvious round numbers / prior swing levels.
3. Build the **event timeline** for the session so the trader knows when to size
   down around news.
4. Prioritize **High / Medium / Low** what actually matters today.

## Output (always this shape)
1. **Bias:** one line — direction lean + conviction + the "this invalidates it" level.
2. **NQ levels to trade against:** a short list (support / resistance / pivot).
3. **Event timeline (ET):** table of today's releases by time + expected impact.

| Time (ET) | Event | Why it matters | Trade plan around it |
|---|---|---|---|

4. **Cross-market tone:** 2–3 sentences — yields, DXY, crypto, sector leadership.
5. **"If I only watch 3 things today":** the three highest-priority items.

If markets are closed (weekend/holiday), produce a **Week-Ahead** version: the
week's red-folder events by day + levels that matter into the next session.

## Rules
- Prioritization and levels, never a price prediction or a buy/sell call.
- Always surface the **next major economic release and its time** — for NQ that
  single fact reshapes the whole session.
- Keep it to a 60-second read before the bell.
