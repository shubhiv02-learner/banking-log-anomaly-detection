from datetime import datetime
from pydantic import BaseModel


class AlertResponse(BaseModel):

    id: int
    window_metric_id: int
    service: str
    final_score: float
    priority: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardSummary(BaseModel):

    total_alerts: int

    critical: int
    high: int
    medium: int
    low: int


class ServiceDistribution(BaseModel):

    service: str
    count: int

class WindowMetricResponse(BaseModel):

    id: int

    service: str

    window_start: datetime
    window_end: datetime

    record_count: int

    latency_mean: float
    latency_max: float

    cpu_mean: float
    cpu_max: float

    memory_mean: float

    queue_lag_mean: float
    queue_lag_max: float

    error_count: int

    ml_score: float
    statistical_score: float

    final_score: float

    prediction: int

    priority: str

    ewma : float
    cusum : float
    persistence_score : float
    incident_probability : float

    created_at: datetime


    class Config:
        from_attributes = True  

class TicketResponse(BaseModel):

    id: int
    alert_id: int
    ticket_id: str
    service:str
    assignee : str
    priority: str
    status: str
    created_at: datetime
    updated_at: datetime
    notification_sent : bool
    notification_time : datetime
    class Config:
        from_attributes = True
