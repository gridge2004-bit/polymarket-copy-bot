"""Shared config + path helpers for the assistant layer.

Single source of truth for loading assistant/config.json and resolving repo
paths, so every script (journal, alerts, rundown, recap, grading, autopsy)
agrees on where things live.
"""
import json
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(REPO_ROOT, "assistant", "config.json")

_DEFAULTS = {
    "alerts": {
        "allowed_sides": ["BUY"],
        "min_their_size_usdc": 50,
        "max_their_size_usdc": None,
        "price_min": 0.10,
        "price_max": 0.90,
        "title_blocklist": [],
        "title_allowlist": [],
        "max_trades_per_day": 20,
        "max_daily_spend_usdc": 10.0,
    },
    "assistant": {
        "model": "claude-sonnet-4-6",
        "timezone": "America/New_York",
        "journal_path": "journal/trades.jsonl",
        "reports_dir": "reports",
    },
}


def load_config() -> dict:
    """Load config.json, falling back to defaults if missing/partial."""
    cfg = {k: dict(v) for k, v in _DEFAULTS.items()}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            disk = json.load(f)
        for section in ("alerts", "assistant"):
            if isinstance(disk.get(section), dict):
                cfg[section].update(disk[section])
    except FileNotFoundError:
        pass
    return cfg


def repo_path(*parts: str) -> str:
    """Resolve a path relative to the repo root."""
    return os.path.join(REPO_ROOT, *parts)


def journal_path() -> str:
    return repo_path(*load_config()["assistant"]["journal_path"].split("/"))


def model_name() -> str:
    return os.getenv("ASSISTANT_MODEL") or load_config()["assistant"]["model"]
