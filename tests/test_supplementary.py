import numpy as np
import pandas as pd

from src import supplementary
from src.portfolio import TICKERS, final_weights


def test_walk_forward_never_trains_on_evaluation_year(monkeypatch):
    dates = pd.bdate_range("2004-01-01", "2011-12-30")
    rng = np.random.default_rng(42)
    returns = pd.DataFrame(
        rng.normal(0.0001, 0.01, (len(dates), 7)), index=dates, columns=TICKERS
    )
    rf = pd.Series(0.02 / 252, index=dates)
    training_ends = []
    original_stats = supplementary.asset_stats

    def record_stats(train):
        training_ends.append(train.index.max())
        return original_stats(train)

    monkeypatch.setattr(supplementary, "asset_stats", record_stats)
    monkeypatch.setattr(supplementary, "max_sharpe", lambda *args: final_weights())
    monkeypatch.setattr(supplementary, "min_variance", lambda *args: final_weights())
    summary, decisions = supplementary.walk_forward(returns, rf)
    assert [d.year for d in training_ends] == [2009, 2010]
    assert all(
        pd.Timestamp(row["Training end"]).year < row["Year"]
        for _, row in decisions.iterrows()
    )
    assert summary["Sharpe"].nunique() == 1
    assert summary["Start"].nunique() == 1
    assert summary["End"].nunique() == 1


def test_threshold_sensitivity_does_not_extrapolate_into_body():
    losses = pd.Series(np.random.default_rng(42).exponential(0.01, 2000))
    result = supplementary.threshold_sensitivity(losses, alpha=0.90)
    outside = result[result["Threshold quantile"] > 0.90]
    assert outside["VaR"].isna().all()
    assert outside["Status"].eq("Outside fitted tail").all()
    valid = result[result["Threshold quantile"] < 0.90]
    assert (valid["ES"] >= valid["VaR"]).all()
