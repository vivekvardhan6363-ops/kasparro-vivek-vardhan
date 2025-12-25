import csv
from core.db import SessionLocal
from schemas.models import RawCSV

def load_csv_data():
    print("Reading CSV...")

    db = SessionLocal()

    try:
        with open("data/crypto_sample.csv", mode="r") as file:
            reader = csv.DictReader(file)
            rows = list(reader)

            record = RawCSV(data=rows)
            db.add(record)
            db.commit()

        print("CSV data stored successfully")

    except Exception as e:
        db.rollback()
        print("CSV ingestion failed")
        print(e)

    finally:
        db.close()
