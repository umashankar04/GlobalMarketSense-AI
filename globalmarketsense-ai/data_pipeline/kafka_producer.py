import json
import importlib
import os
import random
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Iterable, List

try:
    tweepy = importlib.import_module("tweepy")
except Exception:
    tweepy = None


TOPIC_NAME = os.getenv("KAFKA_TOPIC", "sentiment_stream")
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")


@dataclass
class StreamEvent:
    market: str
    source: str
    text: str
    followers: int = 0
    engagement: float = 0.0
    source_credibility: float = 0.5

    def to_dict(self) -> Dict:
        return {
            "market": self.market,
            "source": self.source,
            "text": self.text,
            "followers": self.followers,
            "engagement": self.engagement,
            "source_credibility": self.source_credibility,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


class SentimentStreamProducer:
    def __init__(self, bootstrap_servers: str = KAFKA_BOOTSTRAP, topic: str = TOPIC_NAME):
        self.topic = topic
        kafka_module = importlib.import_module("kafka")
        kafka_producer_cls = getattr(kafka_module, "KafkaProducer")
        self.producer = kafka_producer_cls(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: str(k).encode("utf-8"),
        )

    def send_event(self, event: StreamEvent) -> None:
        payload = event.to_dict()
        self.producer.send(self.topic, key=payload["market"], value=payload)

    def flush(self) -> None:
        self.producer.flush()


def demo_event_feed() -> Iterable[StreamEvent]:
    samples: List[StreamEvent] = [
        StreamEvent("SP500", "news", "US manufacturing data beats expectations", source_credibility=0.9),
        StreamEvent("NIFTY50", "news", "India inflation cools for second month", source_credibility=0.85),
        StreamEvent("SENSEX", "news", "Banking stocks rally on policy optimism", source_credibility=0.8),
        StreamEvent("BTC", "twitter", "Bitcoin fear is rising before macro event", followers=220000, engagement=0.08),
        StreamEvent("NASDAQ", "twitter", "Tech earnings guidance triggers risk-off mood", followers=145000, engagement=0.05),
    ]
    while True:
        yield random.choice(samples)


def run_demo_stream(interval_seconds: float = 1.0) -> None:
    producer = SentimentStreamProducer()
    for event in demo_event_feed():
        producer.send_event(event)
        print(f"Produced event for {event.market}: {event.text}")
        time.sleep(interval_seconds)


class XKafkaStreamingClient:
    def __init__(self, producer: SentimentStreamProducer):
        if tweepy is None:
            raise RuntimeError("tweepy is not installed. Install it to use X streaming mode.")
        self._tweepy = tweepy

        bearer_token = os.getenv("X_BEARER_TOKEN", "")
        if not bearer_token:
            raise RuntimeError("X_BEARER_TOKEN not configured")

        self.producer = producer
        self.client = self._tweepy.StreamingClient(bearer_token=bearer_token, wait_on_rate_limit=True)
        self.client.on_tweet = self.on_tweet

    def on_tweet(self, tweet):
        text = getattr(tweet, "text", "")
        market = "BTC" if "bitcoin" in text.lower() or "btc" in text.lower() else "NASDAQ"
        event = StreamEvent(
            market=market,
            source="twitter",
            text=text,
            followers=0,
            engagement=0.01,
            source_credibility=0.5,
        )
        self.producer.send_event(event)

    def add_default_rules(self):
        rules = [
            "bitcoin OR btc OR crypto lang:en",
            "nasdaq OR tech stocks OR sp500 lang:en",
            "nifty OR sensex OR india market lang:en",
        ]
        existing = self.client.get_rules().data or []
        if existing:
            self.client.delete_rules([rule.id for rule in existing])
        self.client.add_rules([self._tweepy.StreamRule(r) for r in rules])

    def run(self):
        self.add_default_rules()
        self.client.filter(tweet_fields=["created_at", "lang"])


if __name__ == "__main__":
    mode = os.getenv("STREAM_MODE", "demo").lower()
    if mode == "x":
        producer = SentimentStreamProducer()
        XKafkaStreamingClient(producer).run()
    else:
        run_demo_stream()
