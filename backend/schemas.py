from datetime import datetime
from pydantic import BaseModel
#from sqlalchemy.dialects.postgresql import JSONB
# Replace JSONB with standard Python type annotations
from typing import Dict, Any, List, Union, Optional 

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
    payload_json: Optional[Union[Dict[str, Any], List[Any]]] = None
    payload_summary: Optional[Union[Dict[str, Any], List[Any]]] = None

    #  FIX: Changed from JSONB to primitive Python types
    # (Using Union allows your JSON to be either an object/dictionary or an array/list)
    #payload_json: Optional[Union[Dict[str, Any], List[Any]]] = None
    #payload_summary: Optional[Union[Dict[str, Any], List[Any]]] = None
    created_at: datetime


    class Config:
        from_attributes = True
        

class WindowMetricsDetail(BaseModel):
    id: int
    payload_json: Optional[Union[Dict[str, Any], List[Any]]] = None
    payload_summary: Optional[Union[Dict[str, Any], List[Any]]] = None
    # This configuration is required for Pydantic v2 to map SQLAlchemy outputs safely
    #model_config = ConfigDict(from_attributes=True) 
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
    notification_time : Optional[datetime] = None
    incident_summary : Optional[Union[Dict[str, Any], List[Any]]] = None
    preventive_action : Optional[str] = None
    resolution : Optional[str] = None
    class Config:
        from_attributes = True

class TicketListRes(BaseModel):
   
    ticket_id: str
    service:str
    assignee : str
    priority: str
    status: str
    class Config:
        from_attributes = True

#incident_summary : Optional[Union[Dict[str, Any], List[Any]]] = None
class TicketDetRes(BaseModel):
    ticket_id: str
    service:str
    priority: str
    status: str
    assignee: str | None = None
    notification_time : Optional[datetime] = None
    incident_summary: dict | None = None
    class Config:
        from_attributes = True

