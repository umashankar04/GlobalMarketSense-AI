import json
import importlib
import os
from datetime import date, datetime, timezone
from typing import Dict

from backend.storage import init_db, insert_raw_event, upsert_daily_sentiment
from nlp_engine.aggregator import DailySentimentAggregator, compute_weight
from nlp_engine.sentiment_model import FinBERTSentimentEngine


KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC_NAME = os.getenv("KAFKA_TOPIC", "sentiment_stream")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


class SentimentStreamConsumer:
    def __init__(self):
        init_db()
        kafka_module = importlib.import_module("kafka")
        kafka_consumer_cls = getattr(kafka_module, "KafkaConsumer")
        redis_module = importlib.import_module("redis")

        self.consumer = kafka_consumer_cls(
            TOPIC_NAME,
            bootstrap_servers=KAFKA_BOOTSTRAP,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset="latest",
            enable_auto_commit=True,
            group_id="globalmarketsense-sentiment-workers",
        )
        self.sentiment_engine = FinBERTSentimentEngine()
        self.aggregator = DailySentimentAggregator()
        self.redis_client = redis_module.from_url(REDIS_URL)

    def process_event(self, event: Dict) -> Dict:
        sentiment = self.sentiment_engine.score_text(event.get("text", ""))
        weight = compute_weight(
            source_credibility=event.get("source_credibility", 0.5),
            followers=event.get("followers", 0),
            engagement=event.get("engagement", 0.0),
        )
        market = event.get("market", "UNKNOWN")
        insert_raw_event(event)

        self.aggregator.add_record(
            market=market,
            event_date=date.today(),
            sentiment_value=sentiment["net"],
            weight=weight,
        )
        daily_index = self.aggregator.get_daily_index(market, date.today())
        upsert_daily_sentiment(market=market, sentiment_date=date.today(), sentiment_index=daily_index)

        latest = {
            "market": market,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "text": event.get("text", ""),
            "sentiment": sentiment,
            "weight": weight,
            "daily_index": daily_index,
        }
        self.redis_client.set(f"latest_sentiment:{market}", json.dumps(latest), ex=3600)
        return latest

    def run(self) -> None:
        print("Kafka sentiment consumer started...")
        for msg in self.consumer:
            result = self.process_event(msg.value)
            print(f"Processed {result['market']} -> index={result['daily_index']:.4f}")


if __name__ == "__main__":
    SentimentStreamConsumer().run()
