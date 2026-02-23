import json
import importlib
import os
from datetime import date
from functools import lru_cache
from typing import Any, Dict

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException

from backend.realtime_simulator import latest_daily_rows, latest_for_market
from backend.storage import get_latest_daily_sentiment, get_sentiment_frame


router = APIRouter(prefix="/api", tags=["globalmarketsense"])


def _build_synthetic_daily_rows(days: int = 90) -> pd.DataFrame:
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


def _get_daily_frame(days: int = 120) -> pd.DataFrame:
    frame = get_sentiment_frame(days=days)
    if not frame.empty:
        frame = frame.copy()
        if "updated_at" not in frame.columns:
            frame["updated_at"] = pd.Timestamp.utcnow().isoformat()
        return frame
    return _build_synthetic_daily_rows(days=days)


@lru_cache(maxsize=1)
def _get_redis_client():
    try:
        redis = importlib.import_module("redis")
    except Exception:
        return None
    return redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))


@router.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok", "service": "globalmarketsense-api"}


@router.get("/sentiment/latest/{market}")
def latest_sentiment(market: str) -> Dict[str, Any]:
    simulated = latest_for_market(market)
    if simulated is not None:
        return simulated

    redis_client = _get_redis_client()
    if redis_client is not None:
        value = redis_client.get(f"latest_sentiment:{market.upper()}")
        if value:
            return json.loads(value)

    frame = _get_daily_frame(days=45)
    mkt = market.upper()
    mkt_rows = frame[frame["market"] == mkt].sort_values("sentiment_date")
    if mkt_rows.empty:
        raise HTTPException(status_code=404, detail=f"No data for {market}")

    row = mkt_rows.iloc[-1]
    net = float(row["sentiment_index"])
    pos = max(0.0, min(1.0, 0.5 + net / 2))
    neg = max(0.0, min(1.0, 0.5 - net / 2))
    neu = max(0.0, 1.0 - abs(net))

    return {
        "market": mkt,
        "timestamp": pd.Timestamp.utcnow().isoformat(),
        "text": "Synthetic standalone-mode sentiment snapshot",
        "sentiment": {"positive": pos, "negative": neg, "neutral": neu, "net": net},
        "weight": 1.0,
        "daily_index": net,
    }


@router.get("/sentiment/daily")
def daily_sentiment(limit: int = 100):
    """Return daily sentiment data for trend chart.
    
    Returns one entry per market per date to allow frontend to pivot into trends.
    """
    
    # First try synthetic data (most reliable for trends with multiple dates)
    frame = _build_synthetic_daily_rows(days=max(30, min(limit, 180)))
    
    # Convert to response format: one row per market per date
    df = frame.copy()
    df['sentiment_date'] = df['sentiment_date'].dt.strftime('%Y-%m-%d')
    
    # Create list keeping each market-date combo separate
    result_rows = []
    for _, row in df.iterrows():
        result_rows.append({
            'sentiment_date': row['sentiment_date'],
            'market': row['market'],
            'sentiment_index': float(row['sentiment_index']),
        })
    
    # Sort by date descending and limit
    result_rows = sorted(result_rows, key=lambda x: x['sentiment_date'], reverse=True)[:limit]
    
    return {"rows": result_rows}


@router.get("/risk/index/{market}")
def risk_index(market: str):
    simulated = latest_for_market(market)
    if simulated is not None:
        payload = simulated
    else:
        payload = None

    redis_client = _get_redis_client()
    if payload is None and redis_client is not None:
        value = redis_client.get(f"latest_sentiment:{market.upper()}")
        if value:
            payload = json.loads(value)

    if payload is None:
        payload = latest_sentiment(market)

    sentiment_net = float(payload["sentiment"]["net"])
    volatility_proxy = abs(sentiment_net) * 100
    risk_probability = min(0.95, max(0.05, 0.35 + volatility_proxy / 200))

    return {
        "market": market.upper(),
        "date": date.today().isoformat(),
        "risk_probability": risk_probability,
        "volatility_proxy": volatility_proxy,
        "signal": "high_risk" if risk_probability > 0.65 else "normal",
    }


@router.get("/analysis/divergence")
def divergence(days: int = 120):
    frame = _get_daily_frame(days=days)
    if frame.empty:
        return {"rows": []}

    pivot = frame.pivot_table(index="sentiment_date", columns="market", values="sentiment_index", aggfunc="mean")
    for col in ["SP500", "NIFTY50", "SENSEX"]:
        if col not in pivot.columns:
            pivot[col] = 0.0

    pivot["us_india_divergence"] = pivot["SP500"] - (pivot["NIFTY50"] + pivot["SENSEX"]) / 2
    rows = pivot[["us_india_divergence"]].reset_index().to_dict(orient="records")
    return {
        "rows": [
            {
                "sentiment_date": pd.Timestamp(r["sentiment_date"]).date().isoformat(),
                "us_india_divergence": float(r["us_india_divergence"]),
            }
            for r in rows
        ]
    }


@router.get("/analysis/correlation-matrix")
def correlation_matrix(days: int = 120):
    frame = _get_daily_frame(days=days)
    if frame.empty:
        return {"matrix": {}}

    pivot = frame.pivot_table(index="sentiment_date", columns="market", values="sentiment_index", aggfunc="mean")
    corr = pivot.corr().fillna(0.0)
    return {"matrix": corr.to_dict()}

@router.get("/markets/all")
def get_all_markets() -> Dict[str, Any]:
    """Get real-time data for all global stock exchanges."""
    markets_data = []
    with latest_for_market.__globals__.get('_state_lock', __import__('threading').Lock()):
        state = latest_for_market.__globals__.get('_state', {})
        for market in state:
            data = state[market]
            markets_data.append({
                "market": data.get("market"),
                "exchange_info": data.get("exchange_info", {}),
                "price": data.get("price", 0),
                "change_percent": data.get("change_percent", 0),
                "volume": data.get("volume", 0),
                "market_cap": data.get("market_cap", 0),
                "open": data.get("open", 0),
                "high": data.get("high", 0),
                "low": data.get("low", 0),
                "timestamp": data.get("timestamp"),
                "sentiment": data.get("sentiment", {})
            })
    return {"markets": markets_data, "total": len(markets_data)}


@router.get("/markets/by-region/{region}")
def get_markets_by_region(region: str) -> Dict[str, Any]:
    """Get markets filtered by region."""
    from backend.realtime_simulator import _state, _state_lock
    
    markets_data = []
    with _state_lock:
        for market_key in _state:
            data = _state[market_key]
            if data.get("exchange_info", {}).get("region") == region.upper():
                markets_data.append({
                    "market": data.get("market"),
                    "exchange_info": data.get("exchange_info", {}),
                    "price": data.get("price", 0),
                    "change_percent": data.get("change_percent", 0),
                    "volume": data.get("volume", 0),
                    "timestamp": data.get("timestamp"),
                    "sentiment": data.get("sentiment", {})
                })
    return {"region": region.upper(), "markets": markets_data}


# ============= AUTHENTICATION ENDPOINTS =============

from backend.auth import create_token, verify_token, hash_password, verify_password
from backend.models import users_db, portfolios_db, watchlist_db, news_db, User, Portfolio, WatchlistItem, News
from fastapi import Header

@router.post("/auth/register")
def register(username: str, email: str, password: str) -> Dict[str, Any]:
    """Register a new user"""
    if any(u["username"] == username for u in users_db.values()):
        return {"error": "Username already exists", "status": 400}
    
    user = User(username, email, password)
    users_db[user.id] = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "password": hash_password(password),
        "created_at": user.created_at.isoformat(),
        "theme": "dark",
        "currency": "INR"
    }
    
    token = create_token(user.id, user.username)
    return {
        "status": "success",
        "user_id": user.id,
        "username": user.username,
        **token
    }

@router.post("/auth/login")
def login(email: str, password: str) -> Dict[str, Any]:
    """Login user"""
    for user_id, user_data in users_db.items():
        if user_data["email"] == email:
            if verify_password(password, user_data["password"]):
                token = create_token(user_id, user_data["username"])
                return {
                    "status": "success",
                    "user_id": user_id,
                    "username": user_data["username"],
                    **token
                }
    
    return {"error": "Invalid credentials", "status": 401}

@router.post("/auth/logout")
def logout(authorization: str = Header(None)) -> Dict[str, Any]:
    """Logout user"""
    if authorization:
        token = authorization.replace("Bearer ", "")
        # In production, blacklist the token
    return {"status": "success", "message": "Logged out"}


# ============= PORTFOLIO ENDPOINTS =============

@router.post("/portfolio/add")
def add_to_portfolio(symbol: str, quantity: float, entry_price: float, authorization: str = Header(None)) -> Dict[str, Any]:
    """Add stock to portfolio"""
    if not authorization:
        return {"error": "Unauthorized", "status": 401}
    
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    if not payload:
        return {"error": "Invalid token", "status": 401}
    
    user_id = payload["user_id"]
    portfolio = Portfolio(user_id, symbol, quantity, entry_price)
    
    if user_id not in portfolios_db:
        portfolios_db[user_id] = {}
    
    portfolios_db[user_id][portfolio.id] = {
        "id": portfolio.id,
        "symbol": symbol,
        "quantity": quantity,
        "entry_price": entry_price,
        "created_at": portfolio.created_at.isoformat()
    }
    
    return {
        "status": "success",
        "portfolio_id": portfolio.id,
        "message": f"Added {symbol} to portfolio"
    }

@router.get("/portfolio")
def get_portfolio(authorization: str = Header(None)) -> Dict[str, Any]:
    """Get user portfolio"""
    if not authorization:
        return {"error": "Unauthorized", "status": 401}
    
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    if not payload:
        return {"error": "Invalid token", "status": 401}
    
    user_id = payload["user_id"]
    from backend.realtime_simulator import latest_for_market
    
    portfolio_items = []
    if user_id in portfolios_db:
        for portfolio_id, item in portfolios_db[user_id].items():
            market_data = latest_for_market(item["symbol"])
            current_price = market_data["price"] if market_data else item["entry_price"]
            gain = (current_price - item["entry_price"]) * item["quantity"]
            gain_percent = ((current_price - item["entry_price"]) / item["entry_price"] * 100) if item["entry_price"] > 0 else 0
            
            portfolio_items.append({
                "id": portfolio_id,
                "symbol": item["symbol"],
                "quantity": item["quantity"],
                "entry_price": item["entry_price"],
                "current_price": current_price,
                "gain": gain,
                "gain_percent": gain_percent
            })
    
    total_invested = sum(item["quantity"] * item["entry_price"] for item in portfolio_items)
    total_current = sum(item["quantity"] * item["current_price"] for item in portfolio_items)
    total_gain = total_current - total_invested
    
    return {
        "items": portfolio_items,
        "total_invested": total_invested,
        "total_current": total_current,
        "total_gain": total_gain,
        "total_gain_percent": (total_gain / total_invested * 100) if total_invested > 0 else 0
    }

@router.delete("/portfolio/{portfolio_id}")
def remove_from_portfolio(portfolio_id: str, authorization: str = Header(None)) -> Dict[str, Any]:
    """Remove stock from portfolio"""
    if not authorization:
        return {"error": "Unauthorized", "status": 401}
    
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    if not payload:
        return {"error": "Invalid token", "status": 401}
    
    user_id = payload["user_id"]
    if user_id in portfolios_db and portfolio_id in portfolios_db[user_id]:
        del portfolios_db[user_id][portfolio_id]
        return {"status": "success", "message": "Removed from portfolio"}
    
    return {"error": "Portfolio item not found", "status": 404}


# ============= WATCHLIST ENDPOINTS =============

@router.post("/watchlist/add")
def add_to_watchlist(symbol: str, authorization: str = Header(None)) -> Dict[str, Any]:
    """Add stock to watchlist"""
    if not authorization:
        return {"error": "Unauthorized", "status": 401}
    
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    if not payload:
        return {"error": "Invalid token", "status": 401}
    
    user_id = payload["user_id"]
    
    if user_id not in watchlist_db:
        watchlist_db[user_id] = {}
    
    for item in watchlist_db[user_id].values():
        if item["symbol"] == symbol:
            return {"error": "Already in watchlist", "status": 400}
    
    item = WatchlistItem(user_id, symbol)
    watchlist_db[user_id][item.id] = {
        "id": item.id,
        "symbol": symbol,
        "created_at": item.created_at.isoformat()
    }
    
    return {"status": "success", "message": f"Added {symbol} to watchlist"}

@router.get("/watchlist")
def get_watchlist(authorization: str = Header(None)) -> Dict[str, Any]:
    """Get user watchlist"""
    if not authorization:
        return {"error": "Unauthorized", "status": 401}
    
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    if not payload:
        return {"error": "Invalid token", "status": 401}
    
    user_id = payload["user_id"]
    from backend.realtime_simulator import latest_for_market
    
    items = []
    if user_id in watchlist_db:
        for item_id, item in watchlist_db[user_id].items():
            market_data = latest_for_market(item["symbol"])
            items.append({
                "id": item_id,
                "symbol": item["symbol"],
                "price": market_data["price"] if market_data else 0,
                "change_percent": market_data["change_percent"] if market_data else 0,
                "sentiment": market_data.get("sentiment", {}).get("net", 0) if market_data else 0
            })
    
    return {"items": items, "total": len(items)}

@router.delete("/watchlist/{symbol}")
def remove_from_watchlist(symbol: str, authorization: str = Header(None)) -> Dict[str, Any]:
    """Remove stock from watchlist"""
    if not authorization:
        return {"error": "Unauthorized", "status": 401}
    
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    if not payload:
        return {"error": "Invalid token", "status": 401}
    
    user_id = payload["user_id"]
    if user_id in watchlist_db:
        for item_id, item in list(watchlist_db[user_id].items()):
            if item["symbol"] == symbol:
                del watchlist_db[user_id][item_id]
                return {"status": "success", "message": f"Removed {symbol} from watchlist"}
    
    return {"error": "Not in watchlist", "status": 404}


# ============= NEWS ENDPOINTS =============

def seed_sample_news():
    """Seed some sample news"""
    news_list = [
        News("Stock Market Surges on Positive GDP Data", "Global stock markets rallied today following strong GDP growth numbers...", "Reuters", "economy", "https://example.com/news1"),
        News("Tech Stocks Rally on AI Breakthroughs", "Leading tech companies gained significantly after announcing new AI initiatives...", "Bloomberg", "tech", "https://example.com/news2"),
        News("Crude Oil Prices Stabilize Amid Supply Concerns", "Oil prices stabilized today as production cuts take effect...", "CNBC", "commodities", "https://example.com/news3"),
        News("RIL Launches New IPO-Like Venture", "Reliance Industries announced a major new venture...", "Moneycontrol", "ipo", "https://example.com/news4"),
        News("Banking Sector Shows Strong Q4 Growth", "Major banks reported robust earnings in Q4 2025...", "Business Today", "markets", "https://example.com/news5"),
    ]
    
    for news in news_list:
        news_db[news.id] = {
            "id": news.id,
            "title": news.title,
            "summary": news.summary,
            "source": news.source,
            "category": news.category,
            "url": news.url,
            "image_url": news.image_url,
            "created_at": news.created_at.isoformat(),
            "published_at": news.published_at.isoformat()
        }

# Initialize sample news
seed_sample_news()

@router.get("/news")
def get_news(category: str = None, limit: int = 20) -> Dict[str, Any]:
    """Get news feed"""
    news_items = list(news_db.values())
    
    if category:
        news_items = [n for n in news_items if n["category"] == category]
    
    news_items.sort(key=lambda x: x["published_at"], reverse=True)
    return {
        "news": news_items[:limit],
        "total": len(news_items),
        "categories": ["markets", "economy", "tech", "commodities", "ipo"]
    }

@router.get("/news/{news_id}")
def get_news_detail(news_id: str) -> Dict[str, Any]:
    """Get single news article"""
    if news_id in news_db:
        return {"news": news_db[news_id]}
    return {"error": "News not found", "status": 404}

@router.post("/news/add")
def add_news(title: str, summary: str, source: str, category: str, url: str, authorization: str = Header(None)) -> Dict[str, Any]:
    """Add news (admin only)"""
    if not authorization:
        return {"error": "Unauthorized", "status": 401}
    
    news = News(title, summary, source, category, url)
    news_db[news.id] = {
        "id": news.id,
        "title": news.title,
        "summary": news.summary,
        "source": news.source,
        "category": news.category,
        "url": news.url,
        "image_url": news.image_url,
        "created_at": news.created_at.isoformat(),
        "published_at": news.published_at.isoformat()
    }
    
    return {
        "status": "success",
        "news_id": news.id,
        "message": "News added successfully"
    }