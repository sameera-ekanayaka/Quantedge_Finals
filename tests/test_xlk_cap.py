import numpy as np
import pytest

from src.data import load_returns, load_risk_free
from src.portfolio import BOUNDS, annual_risk_free, final_weights, xlk_cap_test

CAPS = (0.15, 0.12, 0.10, 0.08, 0.05)


@pytest.fixture(scope="module")
def table():
    returns = load_returns()
    rf = annual_risk_free(load_risk_free(), returns.index)
    return xlk_cap_test(returns, rf, CAPS)


def test_table_has_one_row_per_cap(table):
    assert list(table.index) == ["15%", "12%", "10%", "8%", "5%"]
    assert table.shape == (5, 5)


def test_xlk_weight_respects_each_cap(table):
    assert (table["XLK weight"].to_numpy() <= np.array(CAPS) + 1e-6).all()


def test_first_row_matches_the_final_portfolio(table):
    assert np.isclose(table.loc["15%", "XLK weight"], final_weights()["XLK"], atol=1e-3)
    assert round(table.loc["15%", "Annual return"], 3) == 0.074


def test_mandate_is_restored_after_the_test(table):
    assert BOUNDS["XLK"] == (0.0, 0.15)
