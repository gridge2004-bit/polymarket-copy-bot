# Video Review + Action Plan — Claude AI Trading Assistant

Review and key takeaways of 4 SMB Capital "Trading Floor" videos on building a
Claude AI trading assistant, plus the action plan this repo implements. A
companion copy lives in Notion ("Trading Perfection").

> Summaries were assembled from the creators' published write-ups (SMB Training
> blog, Jeff Holden / Mike Bellafiore threads, official episode notes) because
> the raw YouTube transcripts could not be auto-fetched. Bracketed prompts are
> paraphrased templates, not verbatim quotes.

## The videos

| # | Title | Source |
| --- | --- | --- |
| 1 | How to use Claude To Gain a Huge Day Trading Edge | Jeff Holden / SMB ([video](https://youtu.be/Rqmdw4xyIMM)) |
| 2 | I Automated My Pre-Market Research With AI | SMB ([video](https://youtu.be/sh5h0GJzjNk)) |
| 3 | How To Build Your Own Claude AI Trading Assistant (Beginners) | Trading Floor Ep 15 ([video](https://youtu.be/mssPkDuQnmY)) |
| 4 | The Simple 4-Step Process To Build Your Own AI Trading Assistant | Trading Floor Ep 16 ([video](https://youtu.be/45eaVU5NVi8)) |

## Key takeaways (synthesis)

1. **Be a "Tier-3" trader** — use AI as a research/infrastructure partner, never
   an oracle. (Tier 1 = all manual; Tier 2 = misuse AI to predict; Tier 3 =
   automate bottlenecks.)
2. **Write rules first** — setups, sizing, risk limits. Everything is graded
   against them.
3. **Persistent context is the product** — a `CLAUDE.md` + a structured journal
   are the foundation (the SMB "4-step": project knowledge → journal → daily
   routine → custom instructions).
4. **Automate the loop** — pre-session briefing → surgical alerts → post-trade
   grading → weekly autopsy.
5. **Schedule it** — routines/cron turn one-off prompts into a system.

The 5 high-leverage uses from Video 1: custom multi-condition alerts;
pre-market game-plan automation; post-trade emotional accountability; weekly
trade autopsy; operating like a desk. Video 2's "Daily Market Rundown" = a
scheduled job that reads inputs and emits one prioritized briefing before the
open (setups: ORB, VWAP bounce, momentum continuation).

## How this repo implements it

| Plan phase | Implementation |
| --- | --- |
| 0 — Foundations | `CLAUDE.md`, `rules/strategy.md`, `assistant/config.json` |
| 1 — Trade journal | `assistant/journal.py` → `journal/trades.jsonl`; hooked into `copy_bot.py`; `assistant/nightly_recap.py` |
| 2 — Pre-session rundown | `assistant/daily_rundown.py` (ORB/VWAP → odds-momentum/size/catalyst) |
| 3 — Surgical alerts | `assistant/alerts.py` + `config.json` (multi-condition copy filter) |
| 4 — Grading & autopsy | `assistant/grade_trades.py`, `assistant/weekly_autopsy.py` |
| 5 — Schedule & operate | `routines/` (cron / Claude Code routines / Railway cron) |
| 6 — Refine the loop | autopsy lessons fold back into `rules/` + `config.json` |

See `SETUP.md` for the finish-up checklist and `routines/README.md` for
scheduling.

## Sources
- V1: <https://www.smbtraining.com/blog/ai-trading-prompts-from-the-video-5-best-practices-for-using-claude-in-trading> · <https://x.com/MikeBellafiore/status/2039415251901505953>
- V2: <https://www.smbtraining.com/blog/i-automated-my-pre-market-research-with-ai-heres-how>
- V3: <https://open.spotify.com/episode/2k8Gp6S9MIxaeLZo7ihL98>
- V4: <https://open.spotify.com/episode/7c2OTcKIPlgfEUW4m9NIzm>
