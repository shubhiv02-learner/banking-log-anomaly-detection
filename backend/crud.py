from datetime import datetime
import re
from unittest import result

from sqlalchemy import func, case
from sqlalchemy.orm import defer
from db_models import Alert, WindowMetrics, Ticket, IncidentAssignmentHistory, UserMaster
import schemas as schemas

def get_alerts(
        db,
        skip: int = 0,
        limit: int = 100 #ideally should be 50, since status not getting closed as of now
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



def get_recent_alerts(db, limit: int = 5):

    return (
    db.query(Alert)
    .order_by(Alert.created_at.desc())
    .limit(limit)
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
    limit: int = 100
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
    limit: int = 10
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
    limit: int = 50
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
    metrics =  (
        db.query(WindowMetrics)
        .options(defer(WindowMetrics.payload_json))
        .options(defer(WindowMetrics.payload_summary))
        .filter(WindowMetrics.id == metric_id)
        .first()
    )
    print("No of Metrics")
    return metrics
"""
def get_window_metric_details_by_id(db, metric_id: int):
        win_details = (
        db.query(WindowMetrics)
        .options(
            load_only(
                WindowMetrics.payload_json, 
                # If your id is required to fetch, you can include it, 
                # but load_only automatically includes the primary key.
                WindowMetrics.payload_summary
            )
        )
        .filter(WindowMetrics.id == metric_id)
        .first())
        print("Fetched window detils")  # debug line
        return win_details
    
"""

def get_window_metric_details_by_id(db, metric_id: int):
    # Use the main model to target exactly what you want
    row = (
        db.query(
            WindowMetrics.id, # Include ID so your frontend can map things cleanly
            WindowMetrics.payload_json, 
            WindowMetrics.payload_summary
        )
        .filter(WindowMetrics.id == metric_id)
        .first()
    )
    
    if row:
        print("Fetched data from DB successfully!")
        # Manually return a clean Python dict. 
        # FastAPI handles serializing native dicts perfectly without crashing.
        return {
            "id": row.id,
            "payload_json": row.payload_json,
            "payload_summary": row.payload_summary
        }
    
    return None


##############INCIDENTS#############

def get_incidents(
        db,
        skip: int = 0,
        limit: int = 50 #ideally should be 50, since status not getting closed as of now
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
        .first()
    )
    print("Fetched incidents:", len(incidents))  # debug line
    return incidents


################################################################
# Methods for agent - Created as for UI sending 100+ records
# By Id, its just last 4 digit
################################################################



def get_agent_incidents(
    db,
    skip: int = 0,
    limit: int = 5
):
    
    severity_order = case(
        (func.upper(Ticket.priority) == "CRITICAL", 1),
        (func.upper(Ticket.priority) == "HIGH", 2),
        (func.upper(Ticket.priority) == "MEDIUM", 3),
        (func.upper(Ticket.priority) == "LOW", 4),
        else_=5
    )

    total = (
        db.query(func.count(Ticket.ticket_id))
        .filter(func.upper(Ticket.status) == "OPEN")
        .scalar()
    )

    incidents = (
        db.query(Ticket)
        .filter(func.upper(Ticket.status) == "OPEN")
        .order_by(
        severity_order,
        Ticket.created_at.desc()
    )
        .offset(skip)
        .limit(limit)
        .all()
    )
    print("total:", total)
    return {
        "total": total,
        "latest_count": len(incidents),
        "incidents": incidents
    }

def get_agent_incident_by_id(db, tkt_id: str):
    
    incidents = (
        db.query(Ticket)
        .filter(Ticket.ticket_id.like(f"%{tkt_id}%"))
        .order_by(Ticket.created_at.desc())
        .first()
    )
    
    return incidents

def get_assignment_history(db,ticket_id: str):
    return (
        db.query(IncidentAssignmentHistory)
        .filter(
            IncidentAssignmentHistory.ticket_id.like(f"%{ticket_id}%")
        )
        .order_by(
            IncidentAssignmentHistory.assignment_time.desc()
        )
        .all()
    )

def get_users(db):

    return (
        db.query(UserMaster)
        .filter(
            UserMaster.active == True
        )
        .order_by(
            UserMaster.name
        )
        .all()
    )

def assign_incident(
    db,
    incident,
    assigned_to,
    remarks,
    prevt_remarks,
    action: schemas.IncidentAction = schemas.IncidentAction.ASSIGNED
):
    
    prev_assignee = incident.assignee

    history = IncidentAssignmentHistory(
        ticket_id=incident.ticket_id,
        previous_assignee=prev_assignee,
        assigned_to=(assigned_to or "").upper(),
        assigned_by="OPS MANAGER",
        action=action,
        remarks=remarks
    )

    db.add(history)

    incident.assignee = (assigned_to or "").upper()
    incident.status = action
    incident.updated_at = datetime.utcnow()
    print(f"Assigning preventive remarks in crud: {prevt_remarks}", flush=True)
    if incident.status  == schemas.IncidentAction.CLOSED:
        resolution, preventive_action = get_preventive_actions(remarks)
        incident.resolution = resolution
        incident.preventive_action = preventive_action
    db.commit()

    db.refresh(history)

    return history

def get_preventive_actions(remarks: str | None) -> tuple[str | None, str | None]:
    if remarks is None:
        return None

    # Split the remarks into lines and filter out empty lines
    lines = [line.strip() for line in remarks.splitlines() if line.strip()]

    # Join the non-empty lines back together with newline characters
    lines = "\n".join(lines) if lines else None
    
    resolution_match = re.search(
        r"Closure Remark:\s*(.*?)(?:Preventive Action:|$)",
        lines,
        re.DOTALL | re.IGNORECASE
    )

    preventive_match = re.search(
        r"Preventive Action:\s*(.*)$",
        lines,
        re.DOTALL | re.IGNORECASE
    )
    resolution = resolution_match.group(1).strip() if resolution_match else None
    preventive_action = preventive_match.group(1).strip() if preventive_match else None
    print(f"Original remark {remarks} Extracted resolution: {resolution}, preventive_action: {preventive_action}", flush=True)
    return resolution, preventive_action

#*********************Alert Details for Agent
def round_float(value, places=4):
    if value is None:
        return None
    try:
        return round(float(value), places)
    except (ValueError, TypeError):
        return None
# Get details for Alert from Windows and Incident
def get_agent_alert_details_by_id(db, ticket_id: str):
    result = (
        db.query(
            Alert.id,
            Ticket.ticket_id,
            Alert.service,
            Alert.priority, 
            Alert.status,
            WindowMetrics.window_start,
            WindowMetrics.window_end,
            Alert.final_score,
            WindowMetrics.ml_score,
            WindowMetrics.statistical_score,
            WindowMetrics.ewma,
            WindowMetrics.cusum,
            WindowMetrics.persistence_score,
            WindowMetrics.incident_probability,
            WindowMetrics.record_count,
            WindowMetrics.error_count,
            WindowMetrics.latency_mean,
            WindowMetrics.latency_max,
            WindowMetrics.latency_std,
            WindowMetrics.cpu_mean,
            WindowMetrics.cpu_max,
            WindowMetrics.memory_mean,
            WindowMetrics.queue_lag_mean,
            WindowMetrics.queue_lag_max            
        )
        .join(WindowMetrics, Alert.window_metric_id == WindowMetrics.id)
        .join(Ticket, Ticket.alert_id == Alert.id)
        .filter(Alert.id == ticket_id)
        .first()
    )

    if not result:
        return None

    return {
        "alert_id": result.id,
        "ticket_id": result.ticket_id,
        "status": result.status,
        "priority": result.priority,
        "service": result.service,
        "window_start": result.window_start.strftime("%Y-%m-%d %H:%M:%S") if result.window_start else None,
        "window_end": result.window_end.strftime("%Y-%m-%d %H:%M:%S") if result.window_end else None,
        "final_score": round_float(result.final_score),
        "ml_score": round_float(result.ml_score),
        "statistical_score": round_float(result.statistical_score),
        "ewma": round_float(result.ewma),
        "cusum": round_float(result.cusum),
        "persistence_score": round_float(result.persistence_score),
        "incident_probability": round_float(result.incident_probability),
        "record_count": result.record_count,
        "latency_mean": round_float(result.latency_mean),
        "latency_max": round_float(result.latency_max),
        "latency_std": round_float(result.latency_std),
        "cpu_mean": round_float(result.cpu_mean),
        "cpu_max": round_float(result.cpu_max),
        "memory_mean": round_float(result.memory_mean),
        "queue_lag_mean": round_float(result.queue_lag_mean),
        "queue_lag_max": round_float(result.queue_lag_max),
        "error_count": round_float(result.error_count),
    }


# Get Raw telemetry,alert_id is only digits in ticket 

def get_agent_alert_payload_by_id(db, alert_id: str):
    #Keep it for future debugging
    """
    print(f"Alert id to get payload : {alert_id}", flush=True)
    print(f"alert_id={alert_id!r}, type={type(alert_id)}", flush=True)
    print(
    str(
        db.query(WindowMetrics.payload_json)
        .join(Alert, Alert.window_metric_id == WindowMetrics.id)
        .filter(Alert.id == alert_id)
        .statement.compile(compile_kwargs={"literal_binds": True})
    ),
    flush=True,
    )
    """
    record_count = (
            db.query(func.jsonb_array_length(WindowMetrics.payload_json))
            .join(Alert, Alert.window_metric_id == WindowMetrics.id)
            .filter(Alert.id == alert_id)
            .scalar()
        )

    if record_count is None:
        return None

    if record_count > 2500:
        return {
            "status": "too_large",
            "record_count": record_count
        }

    payload = (
        db.query(WindowMetrics.payload_json)
        .join(Alert, Alert.window_metric_id == WindowMetrics.id)
        .filter(Alert.id == alert_id)
        .scalar()
)

    return {
            "status": "success",
            "record_count": record_count,
            "payload_json": payload
        }
    