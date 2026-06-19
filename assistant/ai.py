"""Thin wrapper around the Claude API for the assistant scripts.

Every assistant job (rundown, recap, grading, autopsy) builds a deterministic
data digest first, then optionally asks Claude for narrative analysis. If
ANTHROPIC_API_KEY or the SDK is missing, `ask()` returns None and the caller
falls back to the deterministic digest — so the routines still produce useful
output before any secrets are configured.
"""
import os

from .config import model_name


def available() -> bool:
    return bool(os.getenv("ANTHROPIC_API_KEY"))


def ask(system: str, prompt: str, max_tokens: int = 1500) -> str | None:
    """Send one message to Claude. Returns text, or None if unavailable."""
    if not available():
        return None
    try:
        from anthropic import Anthropic
    except ImportError:
        return None
    try:
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        resp = client.messages.create(
            model=model_name(),
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(
            block.text for block in resp.content if getattr(block, "type", None) == "text"
        ).strip()
    except Exception as e:  # noqa: BLE001
        return f"_(AI analysis unavailable: {e})_"
