---
name: trading-assistant
description: Entry point and mindset for using Claude as a trading research/infrastructure partner, modeled on SMB Capital's "Trading Floor" videos. Use when the user asks how to use Claude/AI in their trading, wants to set up an AI trading workflow, asks "what can you do for my trading", or isn't sure which trading skill they need. Explains the framework and routes to the specific skills.
---

# Trading Assistant (SMB framework)

How to use Claude in trading the way SMB Capital teaches it. Source:
`docs/VIDEO_REVIEW_ACTION_PLAN.md`.

## The mindset (set expectations first)
Three tiers of traders:
- **Tier 1 (~90%)** — everything manual, capped by the platform.
- **Tier 2 (~7%)** — misuse AI as a "fortune teller," asking it to predict price.
- **Tier 3 (~3%)** — use AI as a **research + infrastructure partner** to remove
  bottlenecks. **This is the target.**

So: never ask "should I buy X?" Instead bring a thesis, the data, and the risk
you're worried about — and have Claude pressure-test your process. Claude can't
pick trades; it can make you decide better and enforce your own rules.

## The four foundations (the SMB 4-step build)
1. **Project knowledge** — persistent context (a `CLAUDE.md`) describing the
   trader's style, setups, and rules.
2. **Trade journal** — structured log of every decision + reasoning.
3. **Daily routine** — pre-market prep, mid-session alerts, post-trade review.
4. **Custom instructions / rules** — the written rules everything is graded
   against. For futures day-trading (NQ/MNQ + options) that's
   `rules/futures_strategy.md`; the copy bot uses `rules/strategy.md`.

## Route to the right skill
- Morning prep / watchlist → **premarket-rundown**
- Build a precise multi-condition alert → **surgical-alert**
- Review a trade I took / "did I follow my rules?" → **post-trade-review**
- End-of-week "what's my biggest leak?" → **weekly-autopsy**
- "Journal this trade" → **trade-journal**

## In this repo
A working implementation already exists: `copy_bot.py` (executor) plus the
`assistant/` package (journal, alerts, daily_rundown, nightly_recap,
grade_trades, weekly_autopsy) and `routines/` for scheduling. These skills are
the conversational front door to the same workflow; the Python scripts are the
unattended/scheduled version. See `SETUP.md`.

## Rules
- Stay in Tier 3: research, infrastructure, accountability — never predictions.
- Always grade against the trader's **written** rules, not your market opinion.
- Respect `DRY_RUN` and never advise flipping it; going live is a human decision.
