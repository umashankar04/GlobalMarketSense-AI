import argparse

import numpy as np
import pandas as pd

from analysis.correlation import lead_lag_correlation
from analysis.granger_test import run_granger_causality


def run_experiment(days: int = 240):
    rng = np.random.default_rng(42)
    dates = pd.date_range(end=pd.Timestamp.today(), periods=days, freq="D")

    us_sent = pd.Series(rng.normal(0, 0.25, size=days), index=dates)
    india_vol = us_sent.shift(1).fillna(0) * 0.35 + pd.Series(rng.normal(0, 0.2, size=days), index=dates)

    lead_lag = lead_lag_correlation(us_sent, india_vol, max_lag=5)
    granger = run_granger_causality(driver_series=us_sent, target_series=india_vol, max_lag=5)

    return {
        "lead_lag": lead_lag,
        "granger": granger,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=240)
    args = parser.parse_args()
    print(run_experiment(days=args.days))
