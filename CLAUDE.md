# CLAUDE.md — Project Context for the AI Trading Assistant

> This file is read automatically at the start of every Claude session.
> It is the "project knowledge" layer (Step 1 of the SMB 4-step build).
> Keep it accurate — every other part of the system is graded against it.

## What this project is

A **copy-trading bot** for prediction markets plus an **AI trading-assistant**
layer modeled on the SMB Capital "Trading Floor" videos (see
`docs/VIDEO_REVIEW_ACTION_PLAN.md`). The bot watches one wallet on
international Polymarket and mirrors its trades, scaled down, onto a
Polymarket US account. The assistant layer journals every decision, produces a
daily rundown, grades trades against written rules, and runs a weekly autopsy.

## Core components

| File | Role |
| --- | --- |
| `copy_bot.py` | The executor. Polls the followed wallet, matches markets, places scaled orders. |
| `assistant/journal.py` | Structured trade journal (writes `journal/trades.jsonl`). |
| `assistant/alerts.py` | Surgical multi-condition filter — decides if a signal is worth copying. |
| `assistant/config.json` | Tunable alert thresholds + assistant settings (no code edits needed). |
| `assistant/daily_rundown.py` | Pre-session briefing: prioritized table of recent signals/markets. |
| `assistant/nightly_recap.py` | End-of-day recap of what fired / was skipped / P&L. |
| `assistant/grade_trades.py` | Grades each trade against `rules/strategy.md`. |
| `assistant/weekly_autopsy.py` | Finds the single biggest recurring mistake + one fix. |
| `routines/` | Schedules (cron / Claude Code routines) that run the above unattended. |
| `rules/strategy.md` | The written trading rules. The source of truth for grading. |

## How money flows / sizing

- Watches `COPY_WALLET` via the Polymarket data API.
- `SCALE_FACTOR` (default `0.003`) × their USDC size = our raw bet.
- Clamped between `MIN_BET_USDC` and `MAX_BET_USDC`.
- `DRY_RUN=true` by default — **no real orders** until explicitly disabled.

## Configuration (env vars, set in `.env` / Railway Variables)

| Var | Meaning | Default |
| --- | --- | --- |
| `CLOB_API_KEY` | Polymarket US key id | — |
| `CLOB_SECRET` | Polymarket US secret key | — |
| `COPY_WALLET` | Wallet to mirror | `0x9495…a27` |
| `SCALE_FACTOR` | Fraction of their size to copy | `0.003` |
| `MAX_BET_USDC` / `MIN_BET_USDC` | Bet clamps | `1.0` / `0.50` |
| `POLL_INTERVAL` | Seconds between polls | `5` |
| `DRY_RUN` | `true` = simulate only | `true` |
| `ANTHROPIC_API_KEY` | For the AI assistant scripts | — |
| `ASSISTANT_MODEL` | Claude model for assistant jobs | `claude-sonnet-4-6` |

## Rules of engagement for Claude working in this repo

1. **Safety first.** Never flip `DRY_RUN` to `false` in code or commit live
   credentials. Going live is a human decision made via env vars.
2. **The journal is append-only.** Don't rewrite history in `journal/`.
3. **Grade against `rules/strategy.md`,** not against your own opinion of the trade.
4. **Keep the executor and the assistant decoupled** — assistant scripts read
   the journal; they must never block or slow the polling loop.
5. Match the existing code style in `copy_bot.py` (stdlib-first, emoji log lines).

## Known issues / cleanup backlog

- `copy_bot.py` had a `THESHOLD` typo (fixed) that would `NameError` on the
  first matched market in live mode.
- `_TEAM_NAMES` has a stray-tab typo in the `phillies` key and some duplicate
  keys (e.g. `cardinals`, `giants`, `panthers`, `kings`, `jets`) where the
  last definition wins — review before relying on those sports.
