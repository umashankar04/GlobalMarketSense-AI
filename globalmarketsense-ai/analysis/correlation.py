from typing import Dict

import pandas as pd


def lead_lag_correlation(series_a: pd.Series, series_b: pd.Series, max_lag: int = 5) -> Dict[int, float]:
    results: Dict[int, float] = {}
    for lag in range(-max_lag, max_lag + 1):
        shifted = series_b.shift(lag)
        corr = series_a.corr(shifted)
        results[lag] = float(corr) if corr == corr else 0.0
    return results


def cross_market_heatmap_frame(frame: pd.DataFrame, value_col: str = "sentiment_index") -> pd.DataFrame:
    pivot = frame.pivot_table(index="date", columns="market", values=value_col, aggfunc="mean")
    return pivot.corr()
