import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER", "kasparro")
DB_PASSWORD = os.getenv("DB_PASSWORD", "kasparro123")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "coinsdb")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
