from fastapi import FastAPI
from sqlalchemy import select, func
from fastapi.middleware.cors import CORSMiddleware

from backend.database import async_session_pool
from backend.db_models import Alert

app = FastAPI(
    title="SentinelIQ API"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():

    return {
        "status": "running"
    }


@app.get("/alerts")
async def get_alerts():

    async with async_session_pool() as session:

        result = await session.execute(
            select(Alert)
        )

        alerts = result.scalars().all()

        return alerts
    
@app.get("/dashboard/summary")
async def dashboard_summary():

    async with async_session_pool() as session:

        total_alerts = await session.scalar(
            select(func.count(Alert.id))
        )

        critical = await session.scalar(
            select(func.count(Alert.id))
            .where(Alert.priority == "Critical")
        )

        high = await session.scalar(
            select(func.count(Alert.id))
            .where(Alert.priority == "High")
        )

        medium = await session.scalar(
            select(func.count(Alert.id))
            .where(Alert.priority == "Medium")
        )

        low = await session.scalar(
            select(func.count(Alert.id))
            .where(Alert.priority == "Low")
        )

        return {
            "total_alerts": total_alerts,
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low
        }

@app.get("/alerts/recent")
async def recent_alerts():

    async with async_session_pool() as session:

        result = await session.execute(
            select(Alert)
            .order_by(Alert.timestamp.desc())
            .limit(50)
        )

        alerts = result.scalars().all()

        return alerts
@app.get("/analytics/services")
async def service_distribution():

    async with async_session_pool() as session:

        result = await session.execute(
            select(
                Alert.service,
                func.count(Alert.id)
            )
            .group_by(Alert.service)
        )

        rows = result.all()

        return [
            {
                "service": row[0],
                "count": row[1]
            }
            for row in rows
        ]

@app.get("/health")
async def health():

    return {
        "status": "healthy"
    }
    
