#!/bin/bash
# SessionStart hook for Claude Code on the web.
# Installs runtime + dev dependencies so the bot can run and so tests/linters
# work during web sessions. Idempotent and non-interactive.
set -euo pipefail

cd "${CLAUDE_PROJECT_DIR:-.}"

# Runtime dependencies (polymarket-us, python-dotenv)
pip3 install --quiet -r requirements.txt

# Dev tooling: linter + test runner
pip3 install --quiet ruff pytest

echo "session-start: dependencies installed"
