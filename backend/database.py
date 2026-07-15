# backend/database.py

import os
from dotenv import load_dotenv

from pathlib import Path

# 1. Load the variables from the .env file into system memory
load_dotenv()

# 1. Point explicitly to the file inside the .venv folder
# 1. Get the directory where database.py actually lives
BASE_DIR = Path(__file__).resolve().parent.parent  
# This should point to the root of your project

# 2. Point directly to the .env file hidden inside the .venv folder
venv_env_path = BASE_DIR / ".venv" / ".env"  
load_dotenv(dotenv_path=venv_env_path)

# --- DEBUG LINES START ---
print(f"DEBUG: Looking for file at absolute path: {venv_env_path.resolve()}")
print(f"DEBUG: Does the file physically exist? {venv_env_path.exists()}")
# --- DEBUG LINES END ---

# 2. Fetch the specific database URL variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Safety check: Stop the application immediately if the variable is missing
if not DATABASE_URL:
    raise ValueError("CRITICAL ERROR: DATABASE_URL is not set in the .env file.")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy import create_engine

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
)
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)
print("Session created successfully", flush=True)
