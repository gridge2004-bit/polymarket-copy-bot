# Trading Rules — Source of Truth

> Step 4 of the SMB build ("custom instructions"). Every trade the bot makes is
> graded against THIS file by `assistant/grade_trades.py`. If a rule isn't
> written here, it can't be enforced. Edit this file; don't hard-code rules in
> Python.

## Strategy in one sentence

Mirror a single proven prediction-market trader (`COPY_WALLET`) at a small
fixed fraction of their size, but only when the signal passes our surgical
filters, and review every decision so the filters keep improving.

## Why we copy this wallet

- _Fill in:_ track record, sample size, market types they're good at, known
  weaknesses. (The assistant grades against what you write here, so be honest.)

## Entry rules (when we COPY a signal)

A signal is eligible only if **all** of these hold (enforced in
`assistant/alerts.py`, tuned in `assistant/config.json`):

1. **Side**: it's a `BUY` (we don't copy their exits by default).
2. **Conviction proxy**: their USDC size ≥ `min_their_size_usdc`. Small dabbles
   from them are noise.
3. **Price band**: entry price within `[price_min, price_max]`. We avoid both
   near-certain longshots (no edge, fees dominate) and lottery-ticket tails.
4. **Market type**: not in `title_blocklist` (e.g. markets we don't understand).
5. **Daily budget**: copying it keeps us under `max_trades_per_day` and
   `max_daily_spend_usdc`.

## Sizing rules

- Bet = `SCALE_FACTOR` × their size, clamped to `[MIN_BET_USDC, MAX_BET_USDC]`.
- Never override the clamp manually.
- One position per market — don't stack copies of the same market.

## Risk rules (hard limits)

- **Max daily spend**: `max_daily_spend_usdc` (default $10). Stop for the day if hit.
- **Max open exposure**: _fill in_.
- **Max consecutive losses before pause**: _fill in_.
- `DRY_RUN=true` until a config change has run ≥ 1 week in simulation.

## Exit rules

- Default: mirror the source wallet's exits (when `allowed_sides` includes `SELL`).
- _Optional manual overrides: fill in._

## What "following the plan" means (for grading)

A trade is **graded GREEN** if: it passed all entry rules, was sized by the
clamp, and stayed within daily budget. It's **graded RED** if: it was outside
the price band, over budget, a market type we blocklisted, or manually forced.
The weekly autopsy looks for the most frequent RED reason and proposes one fix.

## Change log

- _YYYY-MM-DD_: initial rules drafted from the SMB video action plan.
