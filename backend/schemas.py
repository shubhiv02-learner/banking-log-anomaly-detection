from pydantic import BaseModel
from datetime import datetime


class AlertResponse(BaseModel):
    id: int
    timestamp: datetime
    service: str

    ml_score: float
    statistical_score: float
    final_score: float

    prediction: int
    priority: str

    class Config:
        from_attributes = True