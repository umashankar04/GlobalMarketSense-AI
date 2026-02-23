from fastapi import FastAPI

from backend.realtime_simulator import ensure_started
from backend.routes import router
from backend.storage import init_db
from backend.web_routes import web_router


app = FastAPI(
    title="GlobalMarketSense AI API",
    version="1.0.0",
    description="Multi-Market Sentiment & Volatility Intelligence Engine",
)


@app.on_event("startup")
def startup_event() -> None:
    ensure_started()
    try:
        init_db()
    except Exception as exc:
        print(f"[startup] Database initialization skipped: {exc}")


app.include_router(router)
app.include_router(web_router)
