---
name: weekly-autopsy
description: Run a weekly trade autopsy that finds the single biggest recurring mistake and one fix (the SMB "trade autopsy" practice). Use at week's end, when the user pastes a batch of trades / a journal / report cards, or asks "what's my biggest leak", "what pattern should I fix", or wants a weekly review. Returns ONE highest-leverage issue, not a laundry list.
---

# Weekly Autopsy

Replicates Jeff Holden's practice #4: take all of the week's trades and ask AI
for **the single most important trend to work on** — the one fix that compounds.

## Inputs to ask for (only if missing)
- The week's trades: a pasted list, a journal file, report cards, or
  `journal/trades.jsonl` from this repo (read it if present).
- The written rules (`rules/futures_strategy.md`, fall back `rules/strategy.md`)
  to grade against.

## Process
1. Aggregate the week: count by setup, win rate, average win vs. average loss,
   biggest loser, rule violations, and recurring emotional patterns.
2. Find the **one** highest-leverage problem — the mistake that cost the most or
   repeated the most. Resist listing five things; force-rank to one.
3. Propose **exactly one** concrete, testable fix (a rule edit, a config change,
   a sizing rule, a "do not trade X" filter).
4. Define the **metric** that will show next week whether the fix worked.

## Output
1. **The week in numbers** (short).
2. **The single biggest recurring mistake** (with evidence).
3. **One concrete fix** to implement now.
4. **The metric to check next week.**

If this repo is in use, offer to write the lesson to `reviews/weekly.md` and, if
the fix is a threshold change, to update `assistant/config.json`.

## Rules
- One issue, one fix. Discipline over completeness.
- Evidence-based — cite the trades/stats behind the call.
- Process leaks rank above unlucky outcomes.
