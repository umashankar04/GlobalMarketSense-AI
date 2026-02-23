from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Dict, Tuple


def compute_weight(source_credibility: float, followers: int, engagement: float) -> float:
    follower_component = min((followers / 1000000), 1.0)
    engagement_component = min(engagement, 1.0)
    source_component = min(max(source_credibility, 0.0), 1.0)
    return 0.5 * source_component + 0.3 * follower_component + 0.2 * engagement_component


@dataclass
class AggregateState:
    weighted_sum: float = 0.0
    weight_total: float = 0.0


class DailySentimentAggregator:
    def __init__(self):
        self._store: Dict[Tuple[str, date], AggregateState] = defaultdict(AggregateState)

    def add_record(self, market: str, event_date: date, sentiment_value: float, weight: float) -> None:
        key = (market, event_date)
        state = self._store[key]
        state.weighted_sum += sentiment_value * max(weight, 1e-6)
        state.weight_total += max(weight, 1e-6)

    def get_daily_index(self, market: str, event_date: date) -> float:
        state = self._store[(market, event_date)]
        if state.weight_total == 0:
            return 0.0
        return state.weighted_sum / state.weight_total

    def snapshot_for_date(self, event_date: date) -> Dict[str, float]:
        result: Dict[str, float] = {}
        for (market, day), state in self._store.items():
            if day == event_date and state.weight_total > 0:
                result[market] = state.weighted_sum / state.weight_total
        return result
