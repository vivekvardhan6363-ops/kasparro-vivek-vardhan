import sys
import os
import importlib

print(f"Python executable: {sys.executable}")
print(f"Version: {sys.version}")
print(f"CWD: {os.getcwd()}")
print(f"Path: {sys.path}")

try:
    import core.db
    print(f"Successfully imported core.db: {core.db}")
    print(f"Engine in core.db: {getattr(core.db, 'engine', 'MISSING')}")
except Exception as e:
    print(f"Error importing core.db: {e}")

try:
    import psycopg2
    print(f"psycopg2 version: {psycopg2.__version__}")
except Exception as e:
    print(f"Error importing psycopg2: {e}")

try:
    from dotenv import load_dotenv
    print("dotenv available")
except Exception as e:
    print(f"Error importing dotenv: {e}")
