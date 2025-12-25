import requests
from core.db import SessionLocal
from schemas.models import RawCoinGecko

COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/list"

def fetch_coingecko():
    print("Fetching data from CoinGecko...")

    try:
        response = requests.get(COINGECKO_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print("⚠️ Could not fetch CoinGecko data")
        print(e)
        return

    db = SessionLocal()
    try:
        record = RawCoinGecko(data=data)
        db.add(record)
        db.commit()
        print("CoinGecko data saved successfully")
    except Exception as e:
        db.rollback()
        print("CoinGecko save failed")
        print(e)
    finally:
        db.close()
