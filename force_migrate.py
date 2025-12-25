import sys
import os
print(f"Current working directory: {os.getcwd()}")
print(f"sys.path: {sys.path}")

try:
    from core.db import engine
    print("Successfully imported core.db")
except ImportError as e:
    print(f"Failed to import core.db: {e}")
    sys.exit(1)

try:
    from sqlalchemy import text
    from schemas.models import ETLCheckpoint, NormalizedCoin, Base
    print("Successfully imported schemas.models")
    print("Successfully imported schemas.models")
except ImportError as e:
    print(f"Failed to import schemas.models: {e}")
    sys.exit(1)

def migrate():
    print("WARNING: This will drop `etl_checkpoint` and `normalized_coins` tables.")
    try:
        with engine.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS etl_checkpoint CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS normalized_coins CASCADE"))
            print("Dropped tables.")
    except Exception as e:
        print(f"Error dropping tables: {e}")

    # Recreate all tables (existing ones won't be touched, dropped ones will be created)
    Base.metadata.create_all(bind=engine)
    print("Recreated tables with new schema.")

if __name__ == "__main__":
    migrate()
