#!/usr/bin/env python3
"""Test the fallback synthetic data"""
import pandas as pd
from datetime import date, timedelta
import numpy as np

def _build_synthetic_daily_rows(days: int = 90) -> pd.DataFrame:
    """Replicate the synthetic builder"""
    markets = ["SP500", "NIFTY50", "SENSEX", "BTC", "NASDAQ"]
    rng = np.random.default_rng(42)
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=days, freq="D")

    rows = []
    for market in markets:
        base = rng.normal(0.0, 0.08, size=days).cumsum() / 8
        season = 0.08 * np.sin(np.linspace(0, 3 * np.pi, days))
        noise = rng.normal(0, 0.03, size=days)
        sentiment = np.clip(base + season + noise, -1.0, 1.0)

        for idx, dt in enumerate(dates):
            rows.append(
                {
                    "market": market,
                    "sentiment_date": pd.Timestamp(dt),
                    "sentiment_index": float(sentiment[idx]),
                    "updated_at": pd.Timestamp(dt).isoformat(),
                }
            )

    return pd.DataFrame(rows)

# Build synthetic
frame = _build_synthetic_daily_rows(days=30)

# Check what's in it
print("Synthetic data summary:")
print(f"Total rows: {len(frame)}")

by_date = frame.groupby('sentiment_date').size()
print(f"\nUnique dates: {len(by_date)}")
print("\nDate range:")
print(f"  From: {frame['sentiment_date'].min()}")
print(f"  To: {frame['sentiment_date'].max()}")

print(f"\nDates present:")
for date in sorted(frame['sentiment_date'].unique(), reverse=True)[:5]:
    count = len(frame[frame['sentiment_date'] == date])
    print(f"  {date}: {count} entries")
