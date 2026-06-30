from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import Column, Boolean, Integer, Float, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
Base = declarative_base()


class Alert(Base):

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    window_metric_id = Column(Integer)
    service = Column(String)
    final_score = Column(Float)
    priority = Column(String)
    
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
        )
 # Open, Acknowledged, Resolved
    status = Column(
        String,
        default="OPEN"
    )
class WindowMetrics(Base):

    __tablename__ = "window_metrics"

    id = Column(Integer, primary_key=True)

    window_start = Column(DateTime)
    window_end = Column(DateTime)

    service = Column(String)

    record_count = Column(Integer)

    latency_mean = Column(Float)
    latency_max = Column(Float)
    latency_std = Column(Float)

    cpu_mean = Column(Float)
    cpu_max = Column(Float)

    memory_mean = Column(Float)

    queue_lag_mean = Column(Float)
    queue_lag_max = Column(Float)

    error_count = Column(Integer)

    ewma = Column(Float)
    cusum = Column(Float)

    persistence_score = Column(Float)

    incident_probability = Column(Float)

    ml_score = Column(Float)

    statistical_score = Column(Float)

    final_score = Column(Float)

    prediction = Column(Integer)

    priority = Column(String)
    payload_summary = Column(JSONB, nullable=True)
    payload_json = Column(JSONB, nullable=True)
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
        )

"""
##Source of truth will remain same, so new class not required, handle in schema 
## Pydantic Response Schema (schemas.py) — Create new schemas here what UI or Agent need
class WindowMetricsDetails(Base):
    __tablename__ = "window_metrics"
    payload_summary = Column(JSONB, nullable=True)
    payload_json = Column(JSONB, nullable=True)


    # No __tablename__ needed here! It inherits it from WindowMetrics.
    
    # You must use use_existing_column=True because these columns 
    # already exist on the parent WindowMetrics class table map.
    payload_summary: Mapped[str] = mapped_column(
        use_existing_column=True,
        deferred=False  # Force it to load immediately on this specific subclass
    )

    payload_json: Mapped[dict] = mapped_column(
        use_existing_column=True,
        deferred=False  # Force it to load immediately on this specific subclass
    )
"""

class Ticket(Base):

    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True)
    alert_id = Column(Integer)
    ticket_id = Column(String)
    service = Column(String)
    priority = Column(String)
    assignee = Column(String)
    notification_sent = Column(Boolean, default =False)
    notification_time = Column(DateTime, server_default=func.now())
    incident_summary = Column(JSONB, nullable=True)
    resolution = Column(String)
    preventive_action = Column(String)
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
        )
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
        )
 # Open, Acknowledged, Resolved
    status = Column(
        String,
        default="OPEN")

