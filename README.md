# Kasparro Backend ETL

## 1. Project Overview
A robust, restart-safe ETL backend for crypto data. It ingests data from multiple sources (simulated APIs, CSVs), normalizes it into a unified schema, and exposes it via a fast REST API.

## 2. Architecture Summary
- **Ingestion**: Fetches data from CoinPaprika, CoinGecko, and CSVs.
- **Normalization**: raw JSON -> Typed Schema (`normalized_coins`).
- **Storage**: PostgreSQL (Dockerized locally, Managed on Render Cloud).
- **API**: FastAPI serves data via `/data`, `/stats`, and `/health`.

## 3. How to Run Locally

**Start System:**
```bash
make up  # Starts DB and API
```

**Run Tests:**
```bash
make test # Runs pytest suite
```
*(Note: requires `make` or manually running `docker-compose up` and `pytest`)*

## 4. Cloud Deployment (Render)
We use **Render.com** for auto-deployment via Infrastructure-as-Code.
- **Config**: `render.yaml` defines the Web Service and Database.
- **CI/CD**: Every `git push` automatically builds and deploys the new version.

## 5. Live API URL
- **Base URL**: `https://kasparro-backend-2h47.onrender.com`
- **Docs**: `https://kasparro-backend-2h47.onrender.com/docs`

## 6. ETL Design
- **Checkpoints**: The system tracks the last processed ID/Timestamp to avoid duplicates.
- **Restart-Safe**: If the system crashes, it resumes exactly where it left off (Idempotency).

