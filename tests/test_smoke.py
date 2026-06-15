"""Smoke tests for the pure trading-logic helpers in copy_bot.

These import the module in DRY_RUN mode (no network, no orders) and verify
the bet-scaling bounds and the side/outcome -> order-intent mapping. Run with:
    pytest -q
"""
import os
import sys

os.environ.setdefault("DRY_RUN", "true")
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import copy_bot  # noqa: E402


def test_scale_bet_respects_min():
    # A tiny copied trade should be floored at MIN_BET_USDC.
    assert copy_bot.scale_bet(1.0) == copy_bot.MIN_BET_USDC


def test_scale_bet_respects_max():
    # A huge copied trade should be capped at MAX_BET_USDC.
    assert copy_bot.scale_bet(10_000_000.0) == copy_bot.MAX_BET_USDC


def test_scale_bet_is_within_bounds():
    for size in (0, 50, 500, 5_000, 500_000):
        bet = copy_bot.scale_bet(size)
        assert copy_bot.MIN_BET_USDC <= bet <= copy_bot.MAX_BET_USDC


def test_map_intent_buy_yes():
    assert copy_bot.map_intent("BUY", "YES") == "ORDER_INTENT_BUY_LONG"


def test_map_intent_buy_no():
    assert copy_bot.map_intent("BUY", "NO") == "ORDER_INTENT_BUY_SHORT"


def test_map_intent_sell_yes():
    assert copy_bot.map_intent("SELL", "YES") == "ORDER_INTENT_SELL_LONG"
