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
from apscheduler.schedulers.background import BackgroundScheduler

from ingestion.api_coinpaprika import fetch_coinpaprika
from ingestion.api_coingecko import fetch_coingecko
from ingestion.csv_loader import load_csv_data
from services.etl_runner import normalize_data
from schemas.data_response import DataResponse
def run_scheduled_etl():
    print("🔥 Scheduled ETL Started")

    try:
        fetch_coinpaprika()
        fetch_coingecko()
        load_csv_data()
        normalize_data()
        print("✅ Scheduled ETL Completed")

    except Exception as e:
        print("❌ Scheduled ETL Failed:", e)


app = FastAPI()
scheduler = BackgroundScheduler()
scheduler.add_job(run_scheduled_etl, "interval", hours=1)  # change to minutes=1 for testing
scheduler.start()


def run_scheduled_etl():
    print("🔥 Scheduled ETL Started")

    try:
        fetch_coinpaprika()
        fetch_coingecko()
        load_csv_data()
        normalize_data()
        print("✅ Scheduled ETL Completed")

    except Exception as e:
        print("❌ Scheduled ETL Failed:", e)



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
@app.get("/health")
def health(db: Session = Depends(get_db)):
    db_status = "down"
    etl_status = "unknown"

    try:
        # Check DB connectivity
        db.execute(text("SELECT 1"))
        db_status = "up"

        # Check last ETL run status
        result = db.execute(
            text("""
                SELECT status
                FROM etl_runs
                ORDER BY started_at DESC
                LIMIT 1
            """)
        ).fetchone()

        if result:
            etl_status = result[0]

    except Exception:
        db_status = "down"

    return {
        "status": "ok",
        "database": db_status,
        "etl_last_run": etl_status
    }


@app.get("/data", response_model=DataResponse)
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
        "metadata": {
            "request_id": request_id,
            "api_latency_ms": latency,
            "page": page,
            "limit": limit,
            "total_records": total
        },
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
@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
