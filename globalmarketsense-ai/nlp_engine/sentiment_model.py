import importlib
from functools import lru_cache
from typing import Dict

try:
    torch = importlib.import_module("torch")
except Exception:
    torch = None

try:
    transformers = importlib.import_module("transformers")
    AutoModelForSequenceClassification = getattr(transformers, "AutoModelForSequenceClassification")
    AutoTokenizer = getattr(transformers, "AutoTokenizer")
except Exception:
    AutoModelForSequenceClassification = None
    AutoTokenizer = None


MODEL_NAME = "ProsusAI/finbert"


class FinBERTSentimentEngine:
    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name
        self.use_transformers = bool(torch and AutoTokenizer and AutoModelForSequenceClassification)
        self.tokenizer = None
        self.model = None

        if self.use_transformers and AutoTokenizer is not None and AutoModelForSequenceClassification is not None:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.model.eval()

    def score_text(self, text: str) -> Dict[str, float]:
        if not text:
            return {"positive": 0.0, "negative": 0.0, "neutral": 1.0, "net": 0.0}

        if not self.use_transformers:
            return self._fallback_score(text)

        if self.tokenizer is None or self.model is None:
            return self._fallback_score(text)

        if torch is not None:
            with torch.inference_mode():
                encoded = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
                logits = self.model(**encoded).logits
                probs = torch.softmax(logits, dim=-1).squeeze(0)
        else:
            return self._fallback_score(text)

        # FinBERT label order: 0=negative, 1=neutral, 2=positive
        negative = probs[0].item()
        neutral = probs[1].item()
        positive = probs[2].item()

        return {
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "net": positive - negative,
        }

    def _fallback_score(self, text: str) -> Dict[str, float]:
        lowered = text.lower()
        positive_terms = ["rally", "beats", "gain", "growth", "optimism", "bull"]
        negative_terms = ["fear", "drop", "fall", "crash", "risk", "bear"]

        pos_hits = sum(1 for term in positive_terms if term in lowered)
        neg_hits = sum(1 for term in negative_terms if term in lowered)

        total = max(pos_hits + neg_hits, 1)
        positive = pos_hits / total
        negative = neg_hits / total
        neutral = 1.0 - min(1.0, positive + negative)

        return {
            "positive": float(positive),
            "negative": float(negative),
            "neutral": float(neutral),
            "net": float(positive - negative),
        }


@lru_cache(maxsize=1)
def get_sentiment_engine() -> FinBERTSentimentEngine:
    return FinBERTSentimentEngine()
