# backend/database.py

import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
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

# 3. Create your asynchronous SQLAlchemy engine
engine = create_async_engine(DATABASE_URL, echo=True)
print(f"DEBUG: Successfully created async engine with URL: {DATABASE_URL}")

# 4. Create a session pool factory for your API endpoints
async_session_pool = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)
print("DEBUG: Async session pool factory created successfully.")

# 5. Dependency helper function to provide a database session to FastAPI
async def get_db_session():
    async with async_session_pool() as session:
        yield session
