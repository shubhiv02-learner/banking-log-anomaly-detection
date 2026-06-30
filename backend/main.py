from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

#from backend.database import async_session_pool
from backend.database import SessionLocal
from backend.db_models import Alert
import backend.crud  as crud
import backend.schemas as schemas

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

#Database dependency
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

#Root

@app.get("/")
def root():

    return {
        "status": "running"
    }

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }

#Alerts Paginated
@app.get(
    "/alerts",
    response_model=list[schemas.AlertResponse]
    )
def get_alerts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
    ):

    return crud.get_alerts(
        db=db,
        skip=skip,
        limit=limit
    )

#Recent Alerts
@app.get(
    "/alerts/recent",
    response_model=list[schemas.AlertResponse]
    )
def recent_alerts(
    db: Session = Depends(get_db)
    ):

    return crud.get_recent_alerts(db)

#Service Distribution
@app.get(
    "/analytics/services",
    response_model=list[schemas.ServiceDistribution]
    )
def service_distribution(
    db: Session = Depends(get_db)
    ):

    return crud.get_service_distribution(db)

#Alert by id
@app.get(
"/alerts/{alert_id}",
response_model=schemas.AlertResponse
)
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db)
    ):

    alert = crud.get_alert_by_id(
        db,
        alert_id
    )

    if alert is None:
        raise HTTPException(
            status_code=404,
            detail=f"Alert {alert_id} not found"
        )

    return alert


#Dashboard Summary
@app.get(
"/dashboard/summary",
response_model=schemas.DashboardSummary
    )
def dashboard_summary(
    db: Session = Depends(get_db)
    ):

    return crud.get_dashboard_summary(db)

@app.get(
    "/window-metrics",
    response_model=list[schemas.WindowMetricResponse]
)
def get_window_metrics_api(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):

    return crud.get_window_metrics(
        db=db,
        skip=skip,
        limit=limit
    )


@app.get(
    "/window-metrics/service/{service}",
    response_model=list[schemas.WindowMetricResponse]
)
def service_window_metrics(
    service: str,
    db: Session = Depends(get_db)
):

    return crud.get_window_metrics_by_service(
        db,
        service
    )

@app.get(
    "/window-metrics/recent",
    response_model=list[schemas.WindowMetricResponse]
)
def recent_window_metrics(
    db: Session = Depends(get_db)
):

    return crud.get_recent_window_metrics(db)

@app.get(
    "/window-metrics/{metric_id}",
    response_model=schemas.WindowMetricResponse
)
def get_window_metric(
    metric_id: int,
    db: Session = Depends(get_db)
):

    metric = crud.get_window_metric_by_id(
        db,
        metric_id
    )

    if metric is None:
        raise HTTPException(
            status_code=404,
            detail="Window metric not found"
        )

    return metric

@app.get(
    "/window-metrics/details/{metric_id}",
    response_model=schemas.WindowMetricsDetail
)
def get_window_metric_details_by_id(
    metric_id: int,
    db: Session = Depends(get_db)
):

    metric = crud.get_window_metric_details_by_id(
        db,
        metric_id
    )

    if metric is None:
        raise HTTPException(
            status_code=404,
            detail="Window metric not found"
        )

    return metric



##################INCIDENTS END POINTS For dashboard #################
#Alerts Paginated
@app.get(
    "/tickets",
    response_model=list[schemas.TicketResponse]
    )
def get_incidents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
    ):
    incidents = crud.get_incidents(
                    db=db,
                    skip=skip,
                    limit=limit
                 )
    print (incidents.__len__ )
    return incidents


##########################################################################
##  Add endpoint for sentinel Agent
##########################################################################

##For Incident List and details

@app.get(
    "/agent/incidents",
    response_model=list[schemas.TicketListRes]
    )
def get_agent_incidents(
    skip: int = 0,
    limit: int = 5,
    db: Session = Depends(get_db)
    ):
    incidents = crud.get_agent_incidents(
                    db=db,
                    skip=skip,
                    limit=limit
                 )
    print (incidents.__len__ )
    return incidents


@app.get(
    "/agent/incidents/details/{incident_id}",
    response_model=schemas.TicketDetRes
)
def get_agent_incident_by_id(
    incident_id: int,
    db: Session = Depends(get_db)
):

    incident = crud.get_agent_incident_by_id(
        db,
        incident_id
    )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    return incident
################## End API agent  ##############################3


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
