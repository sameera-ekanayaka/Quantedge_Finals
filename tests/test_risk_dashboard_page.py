from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from src import config
from src.data import load_returns
from src.evt import evt_var_es, select_threshold
from src.portfolio import final_weights, portfolio_returns

PAGE = Path(__file__).resolve().parent.parent / "app" / "pages" / "3_risk_dashboard.py"


def test_risk_dashboard_page_renders_cleanly():
    at = AppTest.from_file(str(PAGE), default_timeout=30)
    # Pre-populate sidebar session state values that ui.py expects
    at.session_state["confidence"] = 0.95
    at.session_state["var_method"] = "historical"
    at.session_state["backtest_range"] = (Path().resolve(),)  # Dummy placeholder
    at.run()

    assert not at.exception
    assert len(at.metric) >= 4
    # The title should be present
    assert "Risk Dashboard" in at.title[0].value


def test_dashboard_evt_row_uses_shared_threshold_and_core_metrics():
    at = AppTest.from_file(str(PAGE), default_timeout=30)
    at.session_state["confidence"] = 0.99
    at.session_state["var_method"] = "historical"
    at.session_state["backtest_range"] = (Path().resolve(),)
    at.run()

    returns = load_returns()
    weights = final_weights()
    losses = -portfolio_returns(returns, weights)
    threshold, _, _ = select_threshold(losses, target_quantile=0.90)
    expected_var, expected_es, params = evt_var_es(
        losses, alpha=0.99, threshold=threshold
    )

    comparison = at.dataframe[0].value
    evt_row = comparison.loc[
        comparison["Methodology"] == "Extreme Value Theory (EVT / GPD)"
    ].iloc[0]

    assert params["threshold"] == pytest.approx(float(losses.quantile(0.90)))
    assert evt_row["1-Day VaR (99%)"] == f"{expected_var:.2%}"
    assert (
        evt_row["1-Day VaR ($)"] == f"${expected_var * config.PORTFOLIO_VALUE_USD:,.0f}"
    )
    assert evt_row["1-Day ES (99%)"] == f"{expected_es:.2%}"
    assert (
        evt_row["1-Day ES ($)"] == f"${expected_es * config.PORTFOLIO_VALUE_USD:,.0f}"
    )
