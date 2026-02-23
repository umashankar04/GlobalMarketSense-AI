from typing import Dict
import warnings

import pandas as pd
from statsmodels.tsa.stattools import grangercausalitytests


def run_granger_causality(
    driver_series: pd.Series,
    target_series: pd.Series,
    max_lag: int = 5,
) -> Dict[int, Dict[str, float]]:
    joined = pd.concat([target_series, driver_series], axis=1).dropna()
    joined.columns = ["target", "driver"]

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        test_result = grangercausalitytests(joined[["target", "driver"]], maxlag=max_lag, verbose=False)
    output: Dict[int, Dict[str, float]] = {}

    for lag, lag_result in test_result.items():
        f_test = lag_result[0]["ssr_ftest"]
        output[lag] = {
            "f_stat": float(f_test[0]),
            "p_value": float(f_test[1]),
        }
    return output
