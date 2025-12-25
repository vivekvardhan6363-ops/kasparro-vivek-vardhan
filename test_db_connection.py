from sqlalchemy import text
from core.db import engine

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1;"))
        print("Database connected successfully 🎉")
except Exception as e:
    print("Database connection failed ❌")
    print(e)
