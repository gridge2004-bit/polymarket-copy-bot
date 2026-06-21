# Claude Trading Skills (SMB framework)

Invokable Claude Code skills that replicate SMB Capital's "ways to use Claude in
trading." They live in `.claude/skills/` and are auto-discovered by Claude Code;
type `/<skill-name>` or just describe the task and the matching skill triggers.

| Skill | SMB practice | Use it for |
|---|---|---|
| `trading-assistant` | Framework + 3-tiers mindset | "How do I use Claude for trading?" / not sure which skill |
| `premarket-rundown` | Pre-market automation (#2) | Morning watchlist, prioritized game plan |
| `surgical-alert` | Custom alerts (#1) | A precise multi-condition alert / screener |
| `post-trade-review` | Emotional accountability (#3) | "Did I follow my rules?" on a trade |
| `weekly-autopsy` | Trade autopsy (#4) | Week-end "what's my biggest leak + one fix" |
| `trade-journal` | Journal (build step 2) | "Journal this trade" |

These are the **conversational** front door. The `assistant/` Python package is
the **unattended/scheduled** version of the same workflow (see `routines/` and
`SETUP.md`). Both read the same `rules/strategy.md` and `journal/trades.jsonl`.

Background and video summaries: `docs/VIDEO_REVIEW_ACTION_PLAN.md`.
