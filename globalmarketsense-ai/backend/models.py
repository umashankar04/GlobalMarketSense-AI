"""
Enhanced backend models for MoneyControl-like app
"""
from datetime import datetime, timedelta
from typing import Optional
import secrets

# User model
class User:
    def __init__(self, username: str, email: str, password: str):
        self.id = secrets.token_urlsafe(16)
        self.username = username
        self.email = email
        self.password = password  # In production: hash this
        self.created_at = datetime.now()
        self.theme = "dark"
        self.currency = "INR"
        self.timezone = "Asia/Kolkata"

# Portfolio model
class Portfolio:
    def __init__(self, user_id: str, symbol: str, quantity: float, entry_price: float):
        self.id = secrets.token_urlsafe(16)
        self.user_id = user_id
        self.symbol = symbol
        self.quantity = quantity
        self.entry_price = entry_price
        self.created_at = datetime.now()

# Watchlist model
class WatchlistItem:
    def __init__(self, user_id: str, symbol: str):
        self.id = secrets.token_urlsafe(16)
        self.user_id = user_id
        self.symbol = symbol
        self.created_at = datetime.now()

# News model
class News:
    def __init__(self, title: str, summary: str, source: str, category: str, url: str, image_url: str = None):
        self.id = secrets.token_urlsafe(16)
        self.title = title
        self.summary = summary
        self.source = source
        self.category = category  # markets, economy, tech, commodities, ipo
        self.url = url
        self.image_url = image_url
        self.created_at = datetime.now()
        self.published_at = datetime.now()

# In-memory storage
users_db: dict = {}
portfolios_db: dict = {}
watchlist_db: dict = {}
news_db: dict = {}
sessions_db: dict = {}  # token -> user_id mapping
