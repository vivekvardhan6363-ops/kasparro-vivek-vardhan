from core.db import engine
from schemas.models import Base

import time
from sqlalchemy.exc import OperationalError

def create_all_tables():
    retries = 10
    for i in range(retries):
        try:
            Base.metadata.create_all(bind=engine)
            print("Tables created in database")
            return
        except OperationalError as e:
            print(f"DB not ready yet, retrying... ({i+1}/{retries})")
            time.sleep(3)
    print("Could not connect to DB after multiple retries.")
    exit(1)

if __name__ == "__main__":
    create_all_tables()
