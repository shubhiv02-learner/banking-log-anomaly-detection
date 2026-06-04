from sqlalchemy.orm import declarative_base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import String
from sqlalchemy import DateTime

Base = declarative_base()


class Alert(Base):

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)

    timestamp = Column(DateTime)

    service = Column(String)

    latency_mean = Column(Float)
    latency_max = Column(Float)

    cpu_mean = Column(Float)
    cpu_max = Column(Float)

    memory_mean = Column(Float)

    queue_lag_mean = Column(Float)
    queue_lag_max = Column(Float)

    error_count = Column(Integer)

    ml_score = Column(Float)

    statistical_score = Column(Float)

    final_score = Column(Float)

    prediction = Column(Integer)

    priority = Column(String)