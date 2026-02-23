import os
import importlib
from datetime import datetime
from typing import Dict, List

import numpy as np
import pandas as pd
import requests

try:
    yf = importlib.import_module("yfinance")
except Exception:
    yf = None


NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
NEWS_API_URL = "https://newsapi.org/v2/everything"


def fetch_market_news(query: str, language: str = "en", page_size: int = 50) -> List[Dict]:
    if not NEWS_API_KEY:
        return []

    params = {
        "q": query,
        "language": language,
        "sortBy": "publishedAt",
        "pageSize": page_size,
        "apiKey": NEWS_API_KEY,
    }
    response = requests.get(NEWS_API_URL, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()

    items = []
    for article in payload.get("articles", []):
        items.append(
            {
                "source": article.get("source", {}).get("name", "unknown"),
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "published_at": article.get("publishedAt", datetime.utcnow().isoformat()),
                "url": article.get("url", ""),
            }
        )
    return items


def fetch_price_history(symbol: str, period: str = "2y") -> pd.DataFrame:
    if yf is None:
        return _synthetic_price_history()

    ticker = yf.Ticker(symbol)
    try:
        hist = ticker.history(period=period)
    except Exception:
        return _synthetic_price_history()

    if hist.empty:
        return _synthetic_price_history()

    frame = hist.reset_index()[["Date", "Open", "High", "Low", "Close", "Volume"]]
    frame.columns = ["date", "open", "high", "low", "close", "volume"]
    frame["date"] = pd.to_datetime(frame["date"]).dt.date
    return frame


def _synthetic_price_history(days: int = 520) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    dates = pd.date_range(end=pd.Timestamp.today(), periods=days, freq="B")
    returns = rng.normal(0.0003, 0.012, size=len(dates))
    close = 100 * np.cumprod(1 + returns)
    volume = rng.integers(1_000_000, 8_000_000, size=len(dates))

    frame = pd.DataFrame(
        {
            "date": dates.date,
            "open": close * (1 + rng.normal(0, 0.002, size=len(dates))),
            "high": close * (1 + np.abs(rng.normal(0.003, 0.004, size=len(dates)))),
            "low": close * (1 - np.abs(rng.normal(0.003, 0.004, size=len(dates)))),
            "close": close,
            "volume": volume,
        }
    )
    return frame
