import numpy as np
import pandas as pd
import pytest

from src.data import stub_returns
from src.portfolio import portfolio_returns


def test_portfolio_returns_uses_simple_returns():
    returns = pd.DataFrame({"A": [np.log(1.10)], "B": [np.log(0.90)]})
    result = portfolio_returns(returns, [0.5, 0.5])
    # 0.5 * 10% + 0.5 * -10% in simple terms
    assert result.iloc[0] == pytest.approx(0.0)


def test_portfolio_returns_shape():
    returns = stub_returns(n_days=100)
    weights = np.full(returns.shape[1], 1 / returns.shape[1])
    result = portfolio_returns(returns, weights)
    assert isinstance(result, pd.Series)
    assert result.index.equals(returns.index)


def test_weights_must_sum_to_one():
    returns = pd.DataFrame({"A": [0.01], "B": [0.02]})
    with pytest.raises(ValueError):
        portfolio_returns(returns, [0.5, 0.6])
