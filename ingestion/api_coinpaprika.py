import requests
from core.db import SessionLocal
from schemas.models import RawCoinPaprika

COINPAPRIKA_URL = "https://api.coinpaprika.com/v1/coins"

def fetch_coinpaprika():
    print("Fetching data from CoinPaprika...")

    response = requests.get(COINPAPRIKA_URL)
    response.raise_for_status()

    data = response.json()

    db = SessionLocal()
    try:
        record = RawCoinPaprika(data=data)
        db.add(record)
        db.commit()
        print("CoinPaprika data saved successfully")
    except Exception as e:
        db.rollback()
        print("Failed to save CoinPaprika data")
        print(e)
    finally:
        db.close()
