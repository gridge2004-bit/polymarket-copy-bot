# Setup — AI Trading Assistant layer

Everything below the copy bot was added per the SMB "Trading Floor" video
action plan (`docs/VIDEO_REVIEW_ACTION_PLAN.md`). This file is the ~15-minute
checklist to finish when you're at your laptop.

## 1. Pull the branch
```bash
git fetch origin claude/video-review-action-plan-ECYlG
git checkout claude/video-review-action-plan-ECYlG
pip install -r requirements.txt
```

## 2. Configure
```bash
cp .env.example .env
# Fill in CLOB_API_KEY / CLOB_SECRET (for live) and ANTHROPIC_API_KEY (for AI notes).
# Leave DRY_RUN=true.
```

## 3. Tune your rules (no code)
- Edit `rules/strategy.md` — the written plan everything is graded against.
- Edit `assistant/config.json` — the surgical filter thresholds.

## 4. Run in dry-run and watch the journal fill
```bash
python3 copy_bot.py            # mirrors signals (simulated), writes journal/trades.jsonl
```
In another shell, generate reports any time:
```bash
python3 -m assistant.daily_rundown
python3 -m assistant.nightly_recap
python3 -m assistant.grade_trades
python3 -m assistant.weekly_autopsy
```

## 5. Schedule it
See `routines/README.md` (cron, Claude Code routines, or Railway cron).

## 6. Go live (only after ≥ 1 week of clean dry-run)
- Set `DRY_RUN=false` in `.env` / Railway Variables. **This is the only step
  that places real orders.** Code never flips it for you.

## What runs where
| Piece | Needs API key? | Needs Polymarket creds? |
| --- | --- | --- |
| `copy_bot.py` dry-run | no | no |
| `copy_bot.py` live | no | yes |
| daily_rundown | optional | no (reads public data API) |
| recap / grade / autopsy | optional | no |
