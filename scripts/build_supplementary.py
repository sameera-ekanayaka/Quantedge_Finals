"""Reproduce supplementary analysis without modifying the submitted report."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data import load_returns, load_risk_free
from src.portfolio import final_weights, portfolio_returns
from src.supplementary import threshold_sensitivity, walk_forward

out = Path(__file__).resolve().parents[1] / "submission" / "supplementary"
out.mkdir(parents=True, exist_ok=True)
r = load_returns()
summary, decisions = walk_forward(r, load_risk_free())
summary.to_csv(out / "walk_forward.csv", index=False)
decisions.to_csv(out / "annual_weights.csv", index=False)
threshold_sensitivity(-portfolio_returns(r, final_weights())).to_csv(
    out / "evt_sensitivity.csv", index=False
)
print(summary.to_string(index=False))
