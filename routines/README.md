# Routines (Phase 5) — run the assistant unattended

The assistant scripts are plain modules you can run by hand or on a schedule:

```bash
python3 -m assistant.daily_rundown    # pre-session briefing  -> reports/rundown-*.md
python3 -m assistant.nightly_recap    # end-of-day recap      -> reports/recap-*.md
python3 -m assistant.grade_trades     # grade vs. rules       -> reports/grades-*.md
python3 -m assistant.weekly_autopsy   # weekly lesson         -> reviews/weekly.md
```

All four work **without** an API key (they emit the deterministic digest). Set
`ANTHROPIC_API_KEY` to add Claude's narrative analysis.

## Scheduling options

**A) cron** (simplest on a VM / Railway with a shell):
```bash
crontab routines/crontab     # edit the cwd path + times first
```

**B) Claude Code routines** — if you run Claude Code, port each line in
`crontab` to a routine; see https://code.claude.com/docs/en/routines. This lets
Claude run the job *and* act on it (e.g. open a PR adjusting `config.json` when
the autopsy recommends a filter change).

**C) Railway cron services** — add a second service per job with the start
command set to the `python3 -m assistant.*` line and a cron schedule.

> The copy bot (`copy_bot.py`) and these routines are decoupled: routines only
> read `journal/trades.jsonl`, so they never interfere with live polling.
