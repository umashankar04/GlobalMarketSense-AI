import argparse

import numpy as np
from sklearn.model_selection import train_test_split

from data_pipeline.collectors import fetch_price_history
from forecasting.feature_engineering import add_technical_features, build_training_dataset, select_model_features
from forecasting.transformer_model import TrainConfig, train_model


def run_training(symbol: str = "^GSPC"):
    prices = fetch_price_history(symbol=symbol, period="2y")
    if prices.empty:
        raise RuntimeError(f"No price history found for {symbol}")

    prices["sentiment_index"] = np.random.normal(0.0, 0.2, size=len(prices))
    prices["cross_market_sentiment"] = np.random.normal(0.0, 0.2, size=len(prices))

    frame = add_technical_features(prices)
    feature_cols = select_model_features()
    x, y = build_training_dataset(frame, feature_cols, seq_len=16)

    x_train, x_val, y_train, y_val = train_test_split(x, y, test_size=0.2, shuffle=False)
    _, metrics = train_model(x_train, y_train, x_val, y_val, TrainConfig())
    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="^GSPC")
    args = parser.parse_args()

    metrics = run_training(symbol=args.symbol)
    print(metrics)
