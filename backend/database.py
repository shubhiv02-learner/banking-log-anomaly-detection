# backend/database.py

import os
from dotenv import load_dotenv

from pathlib import Path

from backend.logging_config import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)

# 1. Load the variables from the .env file into system memory
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

venv_env_path = BASE_DIR / ".venv" / ".env"
load_dotenv(dotenv_path=venv_env_path)

logger.debug(
    "Env file path=%s exists=%s",
    venv_env_path.resolve(),
    venv_env_path.exists(),
)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logger.error("DATABASE_URL is not set")
    raise ValueError("CRITICAL ERROR: DATABASE_URL is not set in the .env file.")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
)
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)
logger.info("Database engine and session factory ready")
