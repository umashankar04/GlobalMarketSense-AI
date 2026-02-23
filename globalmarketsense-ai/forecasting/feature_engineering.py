from typing import Iterable, List

import numpy as np
import pandas as pd


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / (loss.replace(0, np.nan))
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50.0)


def add_technical_features(df: pd.DataFrame) -> pd.DataFrame:
    frame = df.copy()
    frame = frame.sort_values("date")

    frame["ret"] = frame["close"].pct_change().fillna(0.0)
    frame["vol_7"] = frame["ret"].rolling(7).std().fillna(0.0)
    frame["vol_14"] = frame["ret"].rolling(14).std().fillna(0.0)
    frame["ma_7"] = frame["close"].rolling(7).mean().bfill()
    frame["ma_21"] = frame["close"].rolling(21).mean().bfill()
    frame["rsi_14"] = compute_rsi(frame["close"], 14)

    frame["sentiment_lag_1"] = frame["sentiment_index"].shift(1).fillna(0.0)
    frame["sentiment_lag_2"] = frame["sentiment_index"].shift(2).fillna(0.0)
    frame["sentiment_momentum"] = frame["sentiment_index"].diff().fillna(0.0)

    if "cross_market_sentiment" in frame.columns:
        frame["cross_market_lag_1"] = frame["cross_market_sentiment"].shift(1).fillna(0.0)
    else:
        frame["cross_market_lag_1"] = 0.0

    frame["target_next_vol"] = frame["vol_7"].shift(-1)
    return frame.dropna().reset_index(drop=True)


def select_model_features() -> List[str]:
    return [
        "sentiment_index",
        "sentiment_lag_1",
        "sentiment_lag_2",
        "sentiment_momentum",
        "cross_market_lag_1",
        "vol_7",
        "vol_14",
        "ma_7",
        "ma_21",
        "rsi_14",
        "volume",
    ]


def make_sequences(matrix: np.ndarray, target: np.ndarray, seq_len: int = 16):
    xs, ys = [], []
    for idx in range(seq_len, len(matrix)):
        xs.append(matrix[idx - seq_len:idx])
        ys.append(target[idx])
    return np.array(xs, dtype=np.float32), np.array(ys, dtype=np.float32)


def build_training_dataset(frame: pd.DataFrame, feature_cols: Iterable[str], seq_len: int = 16):
    features = np.asarray(frame[list(feature_cols)].values, dtype=np.float32)
    target = np.asarray(frame["target_next_vol"].values, dtype=np.float32)
    return make_sequences(features, target, seq_len=seq_len)
