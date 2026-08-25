from datetime import datetime
from enum import Enum
import json
from pydantic import BaseModel, field_validator

from typing import Dict, Any, List, Union, Optional


def _parse_json_field(value: Any) -> Any:
    """Decode JSONB values that were stored as (possibly double-encoded) JSON strings."""
    if value is None or isinstance(value, (dict, list)):
        return value
    if isinstance(value, (bytes, bytearray)):
        value = value.decode("utf-8")
    # JSONB string columns often need more than one loads() pass.
    for _ in range(3):
        if not isinstance(value, str):
            break
        text = value.strip()
        if not text:
            return None
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            return value
    return value 

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
    # Intentionally omit payload_json / payload_summary here.
    # List endpoints defer those columns; DB often stores them as JSON strings,
    # which breaks response_model=Union[dict, list] validation (Swagger 500).
    # Fetch payloads via GET /window-metrics/details/{id}.
    created_at: datetime

    class Config:
        from_attributes = True
        

class WindowMetricsDetail(BaseModel):
    id: int
    # Any: values are normalized to dict/list in crud before response validation.
    payload_json: Optional[Any] = None
    payload_summary: Optional[Any] = None

    class Config:
        from_attributes = True


class WindowMetricsTelemetrySummary(BaseModel):
    window_metric_id: int
    window_start: Optional[str] = None
    window_end: Optional[str] = None
    payload_summary: Optional[Any] = None
    sql_rollup: Dict[str, Any]
    alert_id: Optional[int] = None
    service: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None

      
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

class TicketListResponse(BaseModel):
    total: int
    latest_count: int
    incidents: list[TicketListRes]

#incident_summary : Optional[Union[Dict[str, Any], List[Any]]] = None
class TicketDetRes(BaseModel):
    ticket_id: str
    alert_id: int | None = None
    service:str
    priority: str
    status: str
    assignee: str | None = None
    notification_time : Optional[datetime] = None
    incident_summary: dict | None = None
    resolution: str | None = None
    preventive_action: str | None = None
    class Config:
        from_attributes = True



class UserMasterResponse(BaseModel):

    user_id: int
    name: str
    email: str
    role: str
    active: bool

    class Config:
        from_attributes = True


class AuthUser(BaseModel):

    user_id: int
    name: str
    email: str
    role: str | None = None

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):

    email: str
    password: str


class LoginResponse(BaseModel):

    access_token: str
    token_type: str = "bearer"
    user: AuthUser


class IncidentAssignmentHistoryResponse(BaseModel):

    assignment_id: int
    action: str
    ticket_id: str
    previous_assignee: str | None = None
    assigned_to: str
    assigned_by: str
    assignment_time: datetime
    remarks: str | None = None

    class Config:
        from_attributes = True

class IncidentAction(str, Enum):
    ASSIGNED = "ASSIGNED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    @field_validator("action", mode="before")
    @classmethod
    def normalize_action(cls, v):
        if isinstance(v, str):
            return v.strip().upper()
        return v
    
class IncidentAssignmentRequest(BaseModel):

    ticket_details: str
    assigned_to: str = "SYSTEM"
    remarks: str | None = None
    action: IncidentAction = IncidentAction.ASSIGNED
    prevt_remarks: str | None = None


class DashboardUser(BaseModel):

    user_id: int
    name: str
    email: str
    role: str | None = None

    class Config:
        from_attributes = True


class DashboardIncidentActionRequest(BaseModel):

    ticket_id: str
    action: IncidentAction
    assigned_to: str | None = None
    remarks: str | None = None
    closure_remark: str | None = None
    preventive_action: str | None = None

    @field_validator("ticket_id")
    @classmethod
    def ticket_id_required(cls, value: str) -> str:
        text = (value or "").strip()
        if not text:
            raise ValueError("ticket_id is required")
        return text

    @field_validator("action", mode="before")
    @classmethod
    def action_required(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().upper()
        return value

    @field_validator("assigned_to")
    @classmethod
    def assigned_to_strip(cls, value: str | None) -> str | None:
        if value is None:
            return None
        text = value.strip()
        return text or None


class DashboardIncidentActionResponse(BaseModel):

    action: IncidentAction
    message: str
    ticket_id: str
    status: str
    assignee: str | None = None


class ErrorMappingResponse(BaseModel):
    """Single row from the operational error_mapping catalog."""

    error_code: str
    error_name: str
    description: str | None = None
    business_impact: str | None = None
    customer_impact: str | None = None
    recommended_action: str | None = None
    severity_default: str | None = None
    category: str | None = None


class ErrorMappingListResponse(BaseModel):
    """Full error_mapping catalog for Salveris list-all live fetch."""

    total: int
    errors: list[ErrorMappingResponse]
