from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from core.db import get_db
from schemas.models import NormalizedCoin
from schemas.models import ETLRun
from sqlalchemy import desc
import time
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Kasparro Backend API is running 🚀",
        "endpoints": {
            "health": "/health",
            "data": "/data",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


@app.get("/data")
def get_data(
    page: int = 1,
    limit: int = 10,
    source: str | None = None,
    db: Session = Depends(get_db)
):
    start_time = time.time()
    request_id = str(uuid.uuid4())

    query = db.query(NormalizedCoin)

    if source:
        query = query.filter(NormalizedCoin.source == source)

    total = query.count()
    data = query.offset((page - 1) * limit).limit(limit).all()

    latency = round((time.time() - start_time) * 1000, 2)

    return {
        "request_id": request_id,
        "api_latency_ms": latency,
        "page": page,
        "limit": limit,
        "total_records": total,
        "data": [
            {
                "id": c.id,
                "source": c.source,
                "coin_id": c.coin_id,
                "name": c.name,
                "symbol": c.symbol,
                "market_cap": c.market_cap
            }
            for c in data
        ]
    }


@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    runs = db.query(ETLRun).order_by(desc(ETLRun.id)).all()

    total_runs = len(runs)
    total_processed = sum(r.records_processed for r in runs)

    last_success = next((r for r in runs if r.status == "success"), None)
    last_failure = next((r for r in runs if r.status == "failed"), None)

    return {
        "total_runs": total_runs,
        "total_records_processed": total_processed,
        "last_success": {
            "at": last_success.finished_at if last_success else None,
            "records": last_success.records_processed if last_success else None
        },
        "last_failure": {
            "at": last_failure.finished_at if last_failure else None
        }
    }
