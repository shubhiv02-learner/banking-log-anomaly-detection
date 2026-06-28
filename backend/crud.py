from sqlalchemy import func
from sqlalchemy.orm import defer
#from backend.db_models import as db_models
from backend.db_models import Alert, WindowMetrics, Ticket


def get_alerts(
        db,
        skip: int = 0,
        limit: int = 10000 #ideally should be 50, since status not getting closed as of now
    ):
    
    alerts = (
        db.query(Alert)
        .order_by(Alert.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    print("Fetched alerts:", len(alerts))  # debug line
    return alerts



def get_recent_alerts(db, limit: int = 50):

    return (
    db.query(Alert)
    .order_by(Alert.created_at.desc())
    .limit(10000)
    .all()
)


def get_dashboard_summary(db):


    return {
        "total_alerts":
            db.query(Alert)
             .filter(Alert.status == "OPEN")
            .count(),

        "critical":
            db.query(Alert)
            .filter(Alert.priority == "Critical", Alert.status == "OPEN" )
            .count(),

        "high":
            db.query(Alert)
            .filter(Alert.priority == "High")
            .count(),

        "medium":
            db.query(Alert)
            .filter(Alert.priority == "Medium")
            .count(),
         
        "low":
            db.query(Alert)
            .filter(Alert.priority == "Low")
            .count()
}

#Low remove later as Alert is not getting generated in this case
#When Status is built than needs to be changed
def get_service_distribution(db):

    rows = (
            db.query(
             Alert.service,
            func.count(Alert.id)
)           .filter(Alert.status == "OPEN").group_by(Alert.service).all()
                )

    return [
        {
            "service": row[0],
            "count": row[1]
        }
        for row in rows
        ]


    
def get_alert_by_id(db, alert_id: int):
    return (
    db.query(Alert)
    .filter(Alert.id == alert_id)
    .first()
)

def get_window_metrics(
    db,
    skip: int = 0,
    limit: int = 10000
):

    return (
        db.query(WindowMetrics)
        .options(defer(WindowMetrics.payload_json))
        .options(defer(WindowMetrics.payload_summary))
        .order_by(WindowMetrics.window_start.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_recent_window_metrics(
    db,
    limit: int = 5000
):

    return (
        db.query(WindowMetrics)
        .options(defer(WindowMetrics.payload_json))
        .options(defer(WindowMetrics.payload_summary))
        .order_by(WindowMetrics.window_start.desc())
        .limit(limit)
        .all()
    )

def get_window_metrics_by_service(
    db,
    service: str,
    limit: int = 10000
):

    return (
        db.query(WindowMetrics)
        .options(defer(WindowMetrics.payload_json))
        .options(defer(WindowMetrics.payload_summary))
        .filter(WindowMetrics.service == service)
        .order_by(WindowMetrics.window_start.desc())
        .limit(limit)
        .all()
    )

def get_window_metric_by_id(
    db,
    metric_id: int
):

    return (
        db.query(WindowMetrics)
        .options(defer(WindowMetrics.payload_json))
        .options(defer(WindowMetrics.payload_summary))
        .filter(WindowMetrics.id == metric_id)
        .first()
    )

##############INCIDENTS#############
def get_incidents(
        db,
        skip: int = 0,
        limit: int = 10000 #ideally should be 50, since status not getting closed as of now
    ):
    
    incidents = (
        db.query(Ticket)
        .options(defer(Ticket.incident_summary))
        .order_by(Ticket.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    print("Fetched incidents:", len(incidents))  # debug line
    return incidents

def get_incidents_by_id(db, alert_id: int):
    
    incidents = (
        db.query(Ticket)
        .filter(Alert.id == alert_id)
        .options(defer(Ticket.incident_summary))
        .order_by(Ticket.created_at.desc())
        .all()
    )
    print("Fetched incidents:", len(incidents))  # debug line
    return incidents
