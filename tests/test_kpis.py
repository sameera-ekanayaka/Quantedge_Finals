"""Tests for src/kpis.py."""

import numpy as np
import pandas as pd

from src.kpis import (
    annual_return,
    capm_beta_alpha,
    information_ratio,
    kpi_table,
    max_drawdown,
)


def test_max_drawdown_known_value():
    r = pd.Series([0.10, -0.50, 0.20])
    assert np.isclose(max_drawdown(r), -0.5)


def test_annual_return_constant_growth():
    r = pd.Series([0.001] * 252)
    assert np.isclose(annual_return(r), 1.001**252 - 1)


def test_beta_of_double_market_is_two():
    rng = np.random.default_rng(1)
    market = pd.Series(rng.normal(0.0004, 0.01, 500))
    beta, alpha = capm_beta_alpha(2 * market, market, 0.0)
    assert np.isclose(beta, 2.0)
    assert np.isclose(alpha, 0.0)


def test_information_ratio_of_benchmark_is_nan():
    rng = np.random.default_rng(2)
    market = pd.Series(rng.normal(0.0004, 0.01, 500))
    assert np.isnan(information_ratio(market, market))


def test_kpi_table_has_all_labels():
    rng = np.random.default_rng(3)
    spy = pd.Series(rng.normal(0.0004, 0.01, 500))
    port = 0.6 * spy + pd.Series(rng.normal(0.0002, 0.004, 500))
    table = kpi_table(port, spy, 0.02)
    assert len(table) == 10
    assert not table.isna().any()
