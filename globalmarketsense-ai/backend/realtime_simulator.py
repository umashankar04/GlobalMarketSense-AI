import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

import numpy as np


# Major global stock exchanges and cryptocurrencies
_MARKETS = [
    # US Markets
    "SP500", "NASDAQ", "DJI",
    # European Markets
    "DAX", "CAC40", "FTSE100",
    # Asian Markets
    "NIFTY50", "SENSEX", "HSI", "N225", "KOSPI", "ASX200", "STI",
    # Cryptocurrency
    "BTC", "ETH",
    # Middle East & Other
    "TADAWUL"
]

_EXCHANGE_INFO = {
    "SP500": {"name": "S&P 500", "region": "US", "currency": "USD", "open": "09:30", "close": "16:00"},
    "NASDAQ": {"name": "NASDAQ", "region": "US", "currency": "USD", "open": "09:30", "close": "16:00"},
    "DJI": {"name": "Dow Jones", "region": "US", "currency": "USD", "open": "09:30", "close": "16:00"},
    "DAX": {"name": "DAX", "region": "EU", "currency": "EUR", "open": "08:00", "close": "22:00"},
    "CAC40": {"name": "CAC 40", "region": "EU", "currency": "EUR", "open": "08:00", "close": "22:00"},
    "FTSE100": {"name": "FTSE 100", "region": "EU", "currency": "GBP", "open": "08:00", "close": "16:30"},
    "NIFTY50": {"name": "NIFTY 50", "region": "IN", "currency": "INR", "open": "09:15", "close": "15:30"},
    "SENSEX": {"name": "BSE SENSEX", "region": "IN", "currency": "INR", "open": "09:15", "close": "15:30"},
    "HSI": {"name": "Hang Seng", "region": "HK", "currency": "HKD", "open": "09:30", "close": "16:00"},
    "N225": {"name": "Nikkei 225", "region": "JP", "currency": "JPY", "open": "08:00", "close": "15:00"},
    "KOSPI": {"name": "KOSPI", "region": "KR", "currency": "KRW", "open": "09:00", "close": "15:30"},
    "ASX200": {"name": "ASX 200", "region": "AU", "currency": "AUD", "open": "10:00", "close": "16:00"},
    "STI": {"name": "Straits Times", "region": "SG", "currency": "SGD", "open": "08:00", "close": "17:00"},
    "BTC": {"name": "Bitcoin", "region": "Crypto", "currency": "USD", "open": "00:00", "close": "23:59"},
    "ETH": {"name": "Ethereum", "region": "Crypto", "currency": "USD", "open": "00:00", "close": "23:59"},
    "TADAWUL": {"name": "Tadawul", "region": "SA", "currency": "SAR", "open": "10:00", "close": "15:00"},
}

_state_lock = threading.Lock()
_state: Dict[str, Dict[str, Any]] = {}
_history: List[Dict[str, Any]] = []
_started = False


def _seed_state() -> None:
    rng = np.random.default_rng(123)
    with _state_lock:
        # Seed 30 days of historical data for trend visualization
        base_date = datetime.now(timezone.utc).date()
        for days_back in range(30, -1, -1):  # Include day 0 (today)
            hist_date = (base_date - timedelta(days=days_back)).isoformat()
            for market in _MARKETS:
                # Generate smoothly varying sentiment over 30 days
                trend = -0.3 + (days_back / 30.0) * 0.6  # Trend from -0.3 to +0.3
                noise = float(rng.normal(0, 0.12))
                sentiment_value = float(np.clip(trend + noise, -1.0, 1.0))
                
                _history.append({
                    "market": market,
                    "sentiment_date": hist_date,
                    "sentiment_index": sentiment_value,
                    "price": float(rng.uniform(15000, 85000)),
                    "change_percent": float(rng.normal(0.5, 2.5)),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                })
        
        # Initialize current state
        for market in _MARKETS:
            net = float(rng.normal(0, 0.08))
            price_base = rng.uniform(15000, 85000)  # Index price range
            if market in ["BTC", "ETH"]:
                price_base = rng.uniform(25000, 95000) if market == "BTC" else rng.uniform(1500, 8000)
            
            change = float(rng.normal(0.5, 2.5))  # % change
            volume = int(rng.uniform(50000000, 500000000))  # Trading volume
            
            _state[market] = {
                "market": market,
                "exchange_info": _EXCHANGE_INFO.get(market, {}),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "price": float(price_base),
                "change_percent": float(change),
                "volume": volume,
                "market_cap": float(price_base * volume / 1000),
                "open": float(price_base * (1 - abs(change) / 100)),
                "high": float(price_base * 1.02),
                "low": float(price_base * 0.98),
                "sentiment": {
                    "positive": max(0.0, min(1.0, 0.5 + net / 2)),
                    "negative": max(0.0, min(1.0, 0.5 - net / 2)),
                    "neutral": max(0.0, 1.0 - abs(net)),
                    "net": net,
                },
                "weight": 1.0,
                "daily_index": net,
            }


def _tick() -> None:
    rng = np.random.default_rng(999)
    while True:
        ts = datetime.now(timezone.utc).isoformat()
        with _state_lock:
            for market in _MARKETS:
                current = _state.get(market)
                if not current:
                    continue

                prev_net = float(current["sentiment"]["net"])
                noise = float(rng.normal(0, 0.004))
                next_net = float(np.clip((0.96 * prev_net) + noise, -1.0, 1.0))
                
                # Update price and market data
                price_change = float(rng.normal(0, 0.15))  # % price change per tick
                new_price = float(current["price"] * (1 + price_change / 100))
                new_change_percent = float(current["change_percent"] + price_change)
                new_volume = int(current["volume"] * (1 + rng.normal(0, 0.1)))

                payload = {
                    "market": market,
                    "exchange_info": _EXCHANGE_INFO.get(market, {}),
                    "timestamp": ts,
                    "price": float(np.clip(new_price, current["low"], current["high"])),
                    "change_percent": float(new_change_percent),
                    "volume": new_volume,
                    "market_cap": float(new_price * new_volume / 1000),
                    "open": float(current["open"]),
                    "high": float(max(current["high"], new_price)),
                    "low": float(min(current["low"], new_price)),
                    "sentiment": {
                        "positive": max(0.0, min(1.0, 0.5 + next_net / 2)),
                        "negative": max(0.0, min(1.0, 0.5 - next_net / 2)),
                        "neutral": max(0.0, 1.0 - abs(next_net)),
                        "net": next_net,
                    },
                    "weight": 1.0,
                    "daily_index": next_net,
                }
                _state[market] = payload
                _history.append(
                    {
                        "market": market,
                        "sentiment_date": datetime.now(timezone.utc).date().isoformat(),
                        "sentiment_index": next_net,
                        "price": float(new_price),
                        "change_percent": float(new_change_percent),
                        "updated_at": ts,
                    }
                )
                if len(_history) > 5000:
                    _history.pop(0)

        time.sleep(5)


def ensure_started() -> None:
    global _started
    if _started:
        return
    _seed_state()
    worker = threading.Thread(target=_tick, daemon=True)
    worker.start()
    _started = True


def latest_for_market(market: str) -> Dict[str, Any] | None:
    with _state_lock:
        return _state.get(market.upper())


def latest_daily_rows(limit: int = 100) -> List[Dict[str, Any]]:
    with _state_lock:
        if not _history:
            return []
        return list(reversed(_history[-limit:]))
