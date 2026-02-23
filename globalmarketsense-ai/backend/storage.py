import os
import importlib
from contextlib import contextmanager
from datetime import date
from typing import Dict, List

import pandas as pd

try:
    psycopg = importlib.import_module("psycopg")
except Exception:
    psycopg = None


POSTGRES_DSN = os.getenv(
    "POSTGRES_DSN",
    "postgresql://postgres:postgres@localhost:5432/globalmarketsense",
)


@contextmanager
def get_conn():
    if psycopg is None:
        raise RuntimeError("psycopg is not installed. Install dependencies from requirements.txt")
    conn = psycopg.connect(POSTGRES_DSN)
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS raw_events (
                    id BIGSERIAL PRIMARY KEY,
                    market VARCHAR(20) NOT NULL,
                    source VARCHAR(40) NOT NULL,
                    text_content TEXT NOT NULL,
                    followers BIGINT DEFAULT 0,
                    engagement DOUBLE PRECISION DEFAULT 0,
                    source_credibility DOUBLE PRECISION DEFAULT 0,
                    event_ts TIMESTAMPTZ NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS daily_sentiment (
                    id BIGSERIAL PRIMARY KEY,
                    market VARCHAR(20) NOT NULL,
                    sentiment_date DATE NOT NULL,
                    sentiment_index DOUBLE PRECISION NOT NULL,
                    updated_at TIMESTAMPTZ DEFAULT NOW(),
                    UNIQUE (market, sentiment_date)
                );
                """
            )
        conn.commit()


def insert_raw_event(event: Dict) -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO raw_events (market, source, text_content, followers, engagement, source_credibility, event_ts)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    event.get("market", "UNKNOWN"),
                    event.get("source", "unknown"),
                    event.get("text", ""),
                    int(event.get("followers", 0) or 0),
                    float(event.get("engagement", 0.0) or 0.0),
                    float(event.get("source_credibility", 0.0) or 0.0),
                    event.get("timestamp"),
                ),
            )
        conn.commit()


def upsert_daily_sentiment(market: str, sentiment_date: date, sentiment_index: float) -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO daily_sentiment (market, sentiment_date, sentiment_index)
                VALUES (%s, %s, %s)
                ON CONFLICT (market, sentiment_date)
                DO UPDATE SET
                    sentiment_index = EXCLUDED.sentiment_index,
                    updated_at = NOW()
                """,
                (market, sentiment_date, sentiment_index),
            )
        conn.commit()


def get_latest_daily_sentiment(limit: int = 100) -> List[Dict]:
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT market, sentiment_date, sentiment_index, updated_at
                    FROM daily_sentiment
                    ORDER BY sentiment_date DESC, updated_at DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                rows = cur.fetchall()
    except Exception:
        return []

    return [
        {
            "market": row[0],
            "sentiment_date": row[1].isoformat(),
            "sentiment_index": float(row[2]),
            "updated_at": row[3].isoformat() if row[3] else None,
        }
        for row in rows
    ]


def get_sentiment_frame(days: int = 120) -> pd.DataFrame:
    try:
        with get_conn() as conn:
            query = """
                SELECT market, sentiment_date, sentiment_index
                FROM daily_sentiment
                WHERE sentiment_date >= CURRENT_DATE - (%s::INT)
                ORDER BY sentiment_date ASC
            """
            frame = pd.read_sql(query, conn, params=(days,))
    except Exception:
        return pd.DataFrame(columns=["market", "sentiment_date", "sentiment_index"])
    if frame.empty:
        return frame
    frame["sentiment_date"] = pd.to_datetime(frame["sentiment_date"])
    return frame
