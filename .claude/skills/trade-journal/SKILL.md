---
name: trade-journal
description: Capture a trade as a structured journal entry so it can be graded and reviewed later (Step 2 of the SMB build). Use when the user says "journal this trade", "log my trade", describes a fill they want recorded, or wants to start/maintain a trading journal. Writes a consistent record with the reasoning, not just the numbers.
---

# Trade Journal

Replicates the SMB "trade journal" step — the structured memory the daily review
and weekly autopsy depend on. A journal without the *reasoning* can't be graded,
so capture the thesis, not just the fill.

## Fields to capture (ask only for what's missing)
- **Timestamp / session**
- **Instrument / market**
- **Direction & size**
- **Setup** (e.g. ORB, VWAP reclaim, copy-signal)
- **Entry, stop, target** and the **trigger** that got you in
- **Thesis** in one sentence — why this trade
- **Plan adherence** intent (what "following the plan" means here)
- **Outcome** (P&L / open) when known
- **Emotion / notes** (optional)

## Output / storage
- Default: append one line to `journal/trades.jsonl` matching the schema in
  `assistant/journal.py` (read it first; field names must match so the recap,
  grader, and autopsy can read it). Confirm the JSON before writing.
- If this isn't the copy-bot repo, write a clean markdown table row or a
  Notion-ready block instead, and keep the same fields.

## Rules
- **Append-only.** Never rewrite past entries.
- Record the thesis at entry time, uncolored by the outcome.
- Keep field names stable across entries — consistency is what makes the journal
  analyzable.
