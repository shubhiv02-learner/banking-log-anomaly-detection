# backend/test_connection.py
# Used for Asyn testing - Not needed for synchronous testing
import asyncio
from sqlalchemy import text

# Import the engine engine asset from your database.py file
from database import engine
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path

# 2. Fetch the specific database URL variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Safety check: Stop the application immediately if the variable is missing
if not DATABASE_URL:
    raise ValueError("CRITICAL ERROR: DATABASE_URL is not set in the .env file.")

# 3. Create your asynchronous SQLAlchemy engine
engine = create_async_engine(DATABASE_URL, echo=True)

# ... (Keep all your existing BASE_DIR, load_dotenv, and engine setup code here) ...

async def test_connection():
    print("\n--- Starting Database Connection Test ---")
    try:
        # 1. Establish an async connection from the engine
        async with engine.connect() as conn:
            # 2. Execute a simple, harmless test query
            result = await conn.execute(text("SELECT 1"))
            # 3. Fetch the result to confirm data successfully traveled back
            val = result.scalar()
            
            if val == 1:
                print("✅ SUCCESS: Successfully connected to the 'sentineliq' database!")
            else:
                print("⚠️ WARNING: Connected, but unexpected query response.")
                
    except Exception as e:
        print("❌ CONNECTION FAILED! See error details below:")
        print(f"Error: {e}")
    finally:
        # 4. Cleanly close database background communication pools
        await engine.dispose()
        print("--- Connection Test Finished ---\n")

# Run the async test script
if __name__ == "__main__":
    asyncio.run(test_connection())
