"""Tests for the mandate rules in src/portfolio.py."""

import pandas as pd

from src.portfolio import TICKERS, check_weights, get_bounds


def test_valid_weights_pass():
    w = pd.Series([0.25, 0.10, 0.05, 0.40, 0.10, 0.03, 0.07], index=TICKERS)
    assert check_weights(w)


def test_equal_weight_breaks_the_mandate():
    w = pd.Series(1 / 7, index=TICKERS)
    assert not check_weights(w)


def test_weights_not_summing_to_one_fail():
    w = pd.Series([0.25, 0.10, 0.05, 0.40, 0.10, 0.03, 0.10], index=TICKERS)
    assert not check_weights(w)


def test_bounds_length():
    assert len(get_bounds()) == 7
