# backend/test_insert.py

import asyncio
from datetime import datetime

from database import async_session_pool
from db_models import Alert


async def insert_test():

    async with async_session_pool() as session:

        alert = Alert(
            timestamp=datetime.now(),
            service="payment",

            latency_mean=120,
            latency_max=250,

            cpu_mean=45,
            cpu_max=80,

            memory_mean=60,

            queue_lag_mean=3,
            queue_lag_max=7,

            error_count=2,

            ml_score=0.81,

            statistical_score=0.77,

            final_score=0.79,

            prediction=1,

            priority="High"
        )

        session.add(alert)

        await session.commit()

        print("Alert inserted")


if __name__ == "__main__":
    asyncio.run(insert_test())