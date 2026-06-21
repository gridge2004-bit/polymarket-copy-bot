---
name: surgical-alert
description: Design a precise, multi-condition trade alert that only fires on a high-probability setup (the SMB "custom alerts" practice). Use when the user wants a custom alert, a screener condition, an alert that combines price + volume + VWAP/level + time, or says standard platform alerts are too noisy. Produces the exact condition logic plus an implementation (TradingView Pine, a Python check, or the repo's alerts config).
---

# Surgical Alert Builder

Replicates Jeff Holden's practice #1: instead of a dumb single-line alert, build
a **surgical multi-condition alert** that fires only when an entire setup lines
up — e.g. *"price breaks the 30-min opening-range high on ≥1.5× average volume
while holding above VWAP."* Cuts noise; surfaces only the highest-probability
moments.

## Process
1. **Extract the setup** in plain English from the user. Pin down every
   condition: price trigger, volume condition, trend/level filter (VWAP, MA,
   prior H/L), time window, and any regime filter (only in first hour, only if
   index green, etc.).
2. **Write the boolean** explicitly so there's no ambiguity:
   `trigger = breakout AND volume_ok AND above_vwap AND in_window`.
3. **Pick the target** and emit working code:
   - **TradingView** → a Pine Script `alertcondition` / strategy snippet.
   - **Python / this repo** → either a standalone check function or, for the
     copy bot, new fields in `assistant/config.json` consumed by
     `assistant/alerts.py` (read that file first and match its schema).
   - **Broker/scanner** → the closest expressible filter + note what can't be
     expressed natively.
4. **State the trade-off**: how tight is it? What will it miss (false negatives)
   vs. what noise it removes (false positives)?

## Output
- The plain-English setup.
- The explicit boolean condition list.
- Ready-to-paste code for the chosen target.
- One line on how to loosen/tighten it.

## Rules
- Conditions must be objective and backtestable — no "looks strong."
- Default to fewer, stricter conditions. A surgical alert that fires 2× a day
  beats one that fires 50×.
