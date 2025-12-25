from schemas.models import RawCoinGecko
from datetime import datetime
from sqlalchemy import desc
from schemas.models import ETLRun
from core.db import SessionLocal
from schemas.models import ETLCheckpoint, RawCoinPaprika, RawCSV, NormalizedCoin

def normalize_data():
    db = SessionLocal()
    start_time = datetime.utcnow()
    total_records = 0
    
    # 1. Mark ETL as RUNNING
    # We create a new checkpoint indicating this run started
    running_checkpoint = ETLCheckpoint(
        source="all",
        last_run_time=start_time,
        status="running"
    )
    db.add(running_checkpoint)
    db.commit()

    try:
        print("Normalizing data incrementally...")

        # 2. Get last SUCCESSFUL checkpoint
        # We only want to resume from a point we know was good.
        last_successful_checkpoint = db.query(ETLCheckpoint)\
            .filter(ETLCheckpoint.source == "all")\
            .filter(ETLCheckpoint.status == "success")\
            .order_by(desc(ETLCheckpoint.id))\
            .first()

        last_time = last_successful_checkpoint.last_success_time if last_successful_checkpoint else None
        print(f"Resuming from: {last_time}")

        # Helper function to safe insert (Idempotency)
        def safe_add_coin(coin_data):
            # Check if exists
            exists = db.query(NormalizedCoin).filter_by(
                source=coin_data["source"],
                coin_id=coin_data["coin_id"]
            ).first()
            
            if not exists:
                db.add(NormalizedCoin(**coin_data))
                return True
            return False

        # CoinPaprika
        paprika_records = db.query(RawCoinPaprika).all()
        for record in paprika_records:
            if not last_time or record.fetched_at > last_time:
                for coin in record.data:
                    added = safe_add_coin({
                        "source": "coinpaprika",
                        "coin_id": coin.get("id"),
                        "name": coin.get("name"),
                        "symbol": coin.get("symbol"),
                        "market_cap": None
                    })
                    if added: total_records += 1

        # CSV
        csv_records = db.query(RawCSV).all()
        for record in csv_records:
            if not last_time or record.fetched_at > last_time:
                for row in record.data:
                    # CSV rows are dicts
                    added = safe_add_coin({
                        "source": "csv",
                        "coin_id": row.get("id"),
                        "name": row.get("name"),
                        "symbol": row.get("symbol"),
                        "market_cap": row.get("market_cap")
                    })
                    if added: total_records += 1

        # CoinGecko
        gecko_records = db.query(RawCoinGecko).all()
        for record in gecko_records:
            if not last_time or record.fetched_at > last_time:
                for coin in record.data:
                    added = safe_add_coin({
                        "source": "coingecko",
                        "coin_id": coin.get("id"),
                        "name": coin.get("name"),
                        "symbol": coin.get("symbol"),
                        "market_cap": None
                    })
                    if added: total_records += 1

        # 3. Update checkpoint to SUCCESS
        running_checkpoint.status = "success"
        running_checkpoint.last_success_time = datetime.utcnow()
        
        # Log successful run
        db.add(ETLRun(
            started_at=start_time,
            finished_at=datetime.utcnow(),
            status="success",
            records_processed=total_records
        ))

        db.commit()
        print("Incremental normalization completed")

    except Exception as e:
        db.rollback()
        
        # 4. Mark checkpoint as FAILED
        # We need a new session or to handle the rollback carefully to update checking
        # But here 'running_checkpoint' is already added.
        # However, rollback() undid the 'add(running_checkpoint)' if it wasn't committed? 
        # Wait, I committed running_checkpoint at the top! So it IS in DB.
        # But subsequent adds are rolled back. 
        # I need to update the status of that existing checkpoint record.
        
        try:
            # Re-fetch or merge? 
            # Since session was rolled back, objects are expired.
            # Start a fresh transaction for the failure log
            fail_db = SessionLocal()
            
            # Update the checkpoint we created earlier
            cp = fail_db.query(ETLCheckpoint).filter_by(id=running_checkpoint.id).first()
            if cp:
                cp.status = "failed"
            
            fail_db.add(ETLRun(
                started_at=start_time,
                finished_at=datetime.utcnow(),
                status="failed",
                records_processed=total_records
            ))
            fail_db.commit()
            fail_db.close()
        except Exception as update_err:
            print(f"Critcal error updating failure status: {update_err}")

        print("Normalization failed")
        print(e)

    finally:
        db.close()
