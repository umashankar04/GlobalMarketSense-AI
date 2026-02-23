# GlobalMarketSense AI

Multi-Market Sentiment & Volatility Intelligence Engine for US, India, and Crypto market intelligence.

## Supported Markets

- S&P 500 (`SP500`)
- NIFTY 50 (`NIFTY50`)
- BSE SENSEX (`SENSEX`)
- Bitcoin (`BTC`)
- NASDAQ Composite (`NASDAQ`)

## Core Capabilities

- Real-time stream ingestion with Kafka (`sentiment_stream` topic)
- FinBERT sentiment scoring for news and social data
- Weighted sentiment index aggregation
- PostgreSQL persistence for raw events + daily sentiment index
- Redis real-time cache for latest sentiment snapshots
- Transformer-based volatility forecasting pipeline
- Cross-market analysis: lead-lag, divergence, and causality utilities
- FastAPI backend + localhost web dashboard
- Dockerized deployment

## Project Structure

```text
globalmarketsense-ai/
├── data_pipeline/
│   ├── kafka_producer.py
│   ├── kafka_consumer.py
│   └── collectors.py
├── nlp_engine/
│   ├── sentiment_model.py
│   └── aggregator.py
├── forecasting/
│   ├── transformer_model.py
│   ├── feature_engineering.py
│   └── train_pipeline.py
├── analysis/
│   ├── correlation.py
│   ├── granger_test.py
│   └── experiments.py
├── backend/
│   ├── main.py
│   ├── routes.py
│   ├── storage.py
│   └── web_routes.py
├── docker/
│   ├── Dockerfile.api
│   ├── Dockerfile.worker
│   └── docker-compose.yml
├── requirements.txt
└── README.md
```

## Quick Start (Docker)

```bash
cd globalmarketsense-ai/docker
docker compose up --build
```

Services:

- API: `http://localhost:8000`
- Dashboard: `http://localhost:8000/`

## Local Run (without Docker)

```bash
cd globalmarketsense-ai
pip install -r requirements.txt

# terminal 1
uvicorn backend.main:app --reload

# terminal 2
python data_pipeline/kafka_consumer.py

# terminal 3
python data_pipeline/kafka_producer.py

# dashboard
open http://localhost:8000/
```

## API Endpoints

- `GET /api/health`
- `GET /api/sentiment/latest/{market}`
- `GET /api/sentiment/daily?limit=100`
- `GET /api/risk/index/{market}`
- `GET /api/analysis/divergence?days=120`
- `GET /api/analysis/correlation-matrix?days=120`

## Research Experiment Hooks

1. **LSTM vs Transformer**
   - Add baseline in `forecasting/` and compare with `transformer_model.py` metrics.
2. **With Sentiment vs Without Sentiment**
   - Exclude sentiment features in `feature_engineering.select_model_features` and retrain.
3. **Cross-Market Causality**
   - Use `analysis/granger_test.py` and `analysis/experiments.py`.
4. **Crypto Impact Analysis**
   - Compare BTC sentiment streams against NASDAQ volatility target series.

## Notes

- `kafka_producer.py` currently provides demo stream events for immediate testing.
- Replace demo feed with News API + X/Twitter API ingestion in production.
- `collectors.py` already includes starter integrations for NewsAPI and Yahoo Finance.
- If Kafka/Redis/PostgreSQL are unavailable, API endpoints automatically serve synthetic standalone data so dashboard and analysis remain runnable.
