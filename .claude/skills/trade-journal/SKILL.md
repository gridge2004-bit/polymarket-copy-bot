---
name: trade-journal
description: Capture a trade as a structured journal entry so it can be graded and reviewed later (Step 2 of the SMB build). Use when the user says "journal this trade", "log my trade", describes a fill they want recorded, or wants to start/maintain a trading journal. Writes a consistent record with the reasoning, not just the numbers.
---

# Trade Journal

Replicates the SMB "trade journal" step — the structured memory the daily review
and weekly autopsy depend on. A journal without the *reasoning* can't be graded,
so capture the thesis, not just the fill.

## Fields to capture (ask only for what's missing)
- **Timestamp / session** (ET) and which session window (open / midday / close)
- **Instrument:** NQ / MNQ / option contract (strike, expiry)
- **Direction & size** (# contracts)
- **Setup** (ORB, VWAP reclaim, prior-day level, trend pullback)
- **Entry, stop, target** (in points) and the **trigger** that got you in
- **Thesis** in one sentence — why this trade, what the macro/bias was
- **Was a red-folder event near?** (and did you respect the no-trade window)
- **Outcome:** points / $ P&L, or open
- **Emotion / notes** (optional but valuable for the autopsy)

## Output / storage
- Default for a futures trader: append one line to `journal/futures.jsonl` with
  the fields above (stable key names so the weekly-autopsy can read them), or a
  clean markdown table row if the user prefers a readable log. Confirm before writing.
- (The copy bot uses a separate `journal/trades.jsonl` via `assistant/journal.py`
  — don't mix futures trades into it.)

## Rules
- **Append-only.** Never rewrite past entries.
- Record the thesis at entry time, uncolored by the outcome.
- Keep field names stable across entries — consistency is what makes the journal
  analyzable.
