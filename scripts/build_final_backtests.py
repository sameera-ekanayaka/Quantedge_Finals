"""Archive all original 99% backtests on the final report's common dates."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd

from src import backtest
from src.data import load_returns
from src.portfolio import final_weights, portfolio_returns

out = Path(__file__).resolve().parents[1] / "submission/advanced"
r = portfolio_returns(load_returns(), final_weights())
rows = []
for method, label in [
    ("normal", "Parametric normal"),
    ("student_t", "Parametric Student t"),
    ("monte_carlo", "Monte Carlo (t reference)"),
]:
    result = backtest.run_backtest(r, method, 0.99).loc["2008-01-01":]
    rows.append({"Model": label, **backtest.summarise(result, 0.99)})
pd.DataFrame(rows).to_csv(out / "final_original_backtests.csv", index=False)
print(
    pd.DataFrame(rows)[["Model", "breaches", "kupiec_p", "ind_p", "cc_p"]].to_string(
        index=False
    )
)
