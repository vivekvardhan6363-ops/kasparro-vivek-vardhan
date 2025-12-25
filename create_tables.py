from core.db import engine
from schemas.models import Base

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully 🎯")
