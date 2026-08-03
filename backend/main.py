import re
from fastapi import FastAPI, Depends, HTTPException, logger
from sqlalchemy.orm import Session, defer
from fastapi.middleware.cors import CORSMiddleware
from notification import notify_n8n
from database import SessionLocal
import crud  as crud
import schemas as schemas
from db_models import  Ticket, UserMaster
from notification import notify_n8n
from rapidfuzz import process, fuzz
from config import (
    N8N_ASSIGN_WEBHOOK,
    N8N_RESOLVE_WEBHOOK,
    N8N_CLOSE_WEBHOOK,
)

app = FastAPI(
    title="SentryyIQ API"
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

db = SessionLocal()
users = crud.get_users(db)

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

    rows = crud.get_recent_window_metrics(db)
    # #region agent log
    try:
        import json as _json, time as _time, os as _os
        sample = rows[0] if rows else None
        # Accessing deferred attrs would lazy-load; only log column keys present without forcing payload load.
        payload = {
            "sessionId": "f2332d",
            "runId": "post-fix-exclude-payload",
            "hypothesisId": "EXCLUDE",
            "location": "main.py:recent_window_metrics",
            "message": "list response excludes payload fields from schema",
            "data": {
                "row_count": len(rows),
                "response_model_has_payload_json": "payload_json" in schemas.WindowMetricResponse.model_fields,
                "sample_id": getattr(sample, "id", None),
            },
            "timestamp": int(_time.time() * 1000),
        }
        print(f"[agent-dbg] {payload}")
        for _path in (
            "C:/Shubhi/banking-log-anomaly-detection/.cursor/debug-f2332d.log",
            ".cursor/debug-f2332d.log",
            "debug-f2332d.log",
        ):
            try:
                _os.makedirs(_os.path.dirname(_path) or ".", exist_ok=True)
                with open(_path, "a", encoding="utf-8") as _f:
                    _f.write(_json.dumps(payload) + "\n")
                break
            except Exception:
                continue
    except Exception:
        pass
    # #endregion
    return rows

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
    response_model=schemas.TicketListResponse
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
    print(incidents)
    return incidents


@app.get(
    "/agent/incidents/details/{ind_details}",
    response_model=schemas.TicketDetRes
)
def get_agent_incident_by_id(
    ind_details: str,
    db: Session = Depends(get_db)
):
    # Extract the last number mentioned
    match = re.findall(r"\d+", ind_details)

    if match:
        incident_no = match[-1]
        incident = crud.get_agent_incident_by_id(
        db,
        incident_no
    )

        if incident is None:
            raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

        return incident

    else:
        raise HTTPException(
            status_code=400,
            detail="Incident number not found."
        )
   
#Get User details for agent 
@app.get(
    "/agent/users",
    response_model=list[schemas.UserMasterResponse]
)
def get_users(
    db: Session = Depends(get_db)
):
    users = crud.get_users(db=db)
    return users


@app.get(
    "/agent/incidents/assignments/{assignment_details}",
    response_model=list[schemas.IncidentAssignmentHistoryResponse]
)
def get_assignment_history(
    assignment_details: str,
    db: Session = Depends(get_db)
):
    # Extract the last number mentioned
    match = re.findall(r"\d+", assignment_details)

    if not match:
        raise HTTPException(
            status_code=400,
            detail="No incident number found."
        )
    
    incident_no = match[-1]
    print(f"Extracted incident number from input to get assignment history: {incident_no}", flush=True)
    assignments = crud.get_assignment_history(
        db=db,
        ticket_id=incident_no
    )

    if not assignments:
        raise HTTPException(
            status_code=404,
            detail="Assignment history not found."
        )

    return assignments

@app.post("/agent/incidents/assign")
def assign_incident(
    request: schemas.IncidentAssignmentRequest,
    db: Session = Depends(get_db)
):
    print(request, flush=True) #Check the request object
    # Extract the last number mentioned
    match = re.findall(r"\d+", request.ticket_details)

    if not match:
        raise HTTPException(
            status_code=400,
            detail="No incident number found."
        )

    incident_no = match[-1]
    incident = (
        db.query(Ticket)
        .filter(
            Ticket.ticket_id.like(f"%{incident_no}%")
        )
        .options(defer(Ticket.incident_summary))
        .order_by(Ticket.created_at.desc())
        .first()
    )
    print(f"Incident found: {incident}", flush=True)

    if request.action == schemas.IncidentAction.ASSIGNED and request.assigned_to == "SYSTEM":
        return {
            "status":"failed",
            "message": "assigned_to is required for ASSIGNED action."
        }
    if incident is None:
        print("Incident not found.", flush=True)
        return {
            "status": "failed",
            "message": "Incident not found, recheck the ticket number"
        }
    result = get_assignee(request.assigned_to, users)
    print(f"Assignee resolution result: {result}", flush=True)
    if result["status"] not in ("system", "found"):
        return {
            "status": result["status"],
            "message": result["message"],
            "candidates": result["candidates"]
            }
    user_assignee = result["assignee"].upper() if result["assignee"] else None
    assignee_email = result["email"]
    print(f"Resolved assignee: {user_assignee}, email: {assignee_email},incident assignee: {incident.assignee}, action {request.action}", flush=True)
    
    if incident.assignee == user_assignee and request.action == schemas.IncidentAction.ASSIGNED:
        return {
            "status": "already_assigned",
            "message": f"Incident is already assigned to {user_assignee}."
        }
    if request.action == schemas.IncidentAction.RESOLVED and incident.status == "RESOLVED" :
    
            return {
                "status": "already_resolved",
                "message": f"Incident is already resolved"
            }
       
    if incident.status == "CLOSED" :
    
            return {
                "status": "already_closed",
                "message": f"Incident is already closed, cannot change status"
            }
    
    if request.action == schemas.IncidentAction.CLOSED and incident.status != "RESOLVED":
        return {
           "status": "failed",
            "reason": "INVALID_STATE",
            "message": "Incident must be resolved before it can be closed."
            }
    
    if request.action == schemas.IncidentAction.RESOLVED or request.action == schemas.IncidentAction.CLOSED:
        if request.remarks is None or request.remarks.strip() == "":
         return {
                "status" : "failed",
                "message": "Remarks are mandatory to provide for RESOLVED or CLOSED actions."
         }
        
    print(f"Proceeding to assign incident {incident.ticket_id} to {user_assignee} with action {request.action} and preventive action: {request.prevt_remarks}", flush=True)
    
    assignment = crud.assign_incident(
        db=db,
        incident=incident,
        assigned_to=user_assignee,
        remarks=request.remarks,
        prevt_remarks=request.prevt_remarks,
        action=request.action
    )

    if assignment is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found."
        )

    if request.action == schemas.IncidentAction.ASSIGNED:
        payload = {
            "ticket_id": incident.ticket_id,
            "service": incident.service,
            "priority": incident.priority,
            "status": incident.status,
            "assignee": user_assignee.title() if user_assignee else None,
            "email": assignee_email,
            "remarks": request.remarks
        }

        try:
            print("=" * 60)
            print("Calling n8n webhook", flush=True)
            print("URL:", N8N_ASSIGN_WEBHOOK)
            print("Payload:", payload)
            notify_n8n(N8N_ASSIGN_WEBHOOK, payload)
        except Exception as ex:
            print(f"Failed to notify n8n: {ex}", flush=True)
            logger.exception("Failed to notify n8n")
        return {
            "action": "ASSIGNED",
            "message": f"Incident {incident.ticket_id} assigned successfully to {user_assignee}."
            }

    elif request.action == schemas.IncidentAction.RESOLVED:
        return {
        "action": "RESOLVED",
        "message": f"Incident {incident.ticket_id} resolved successfully."
    }

    elif request.action == schemas.IncidentAction.CLOSED:
        return {
        "action": "CLOSED",
        "message": f"Incident {incident.ticket_id} closed successfully."
    }
#***************************************************************
# Alert APIs for agent , call get_agent_alert_details_by_id
# *************************************************************** 
@app.get(
    "/agent/alerts/details/{ind_details}"
)
def get_agent_alert_details_by_id(
    ind_details: str, db: Session = Depends(get_db)
):
    # Extract the last number mentioned
    match = re.findall(r"\d+", ind_details)
    print(f"Extracted ticket ID from input: {match}", flush=True)

    if match:
        ticket_id = match[-1]
        alert_details = crud.get_agent_alert_details_by_id(
            db,ticket_id
        )

        if ticket_id is None:
            raise HTTPException(
            status_code=404,
            detail="Alert details not found."
        )

        return alert_details

    else:
        raise HTTPException(
            status_code=400,
            detail="Alert details not found."
        )

##################Payload Details - Raw telemetry data for alert ###################

@app.get(
    "/agent/alerts/raw_data/{ind_details}"
)
def get_agent_alert_payload_by_id(
    ind_details: str, db: Session = Depends(get_db)
):
    # Extract the last number mentioned
    match = re.findall(r"\d+", ind_details)
    print(f"Extracted ticket ID from input: {match}, in raw data", flush=True)

    if match:
        ticket_id = match[-1]
        if ticket_id is None:
            raise HTTPException(
            status_code=404,
            detail="Alert details not found."
        )
        print("Calling crud to get payload")
        json_payload = crud.get_agent_alert_payload_by_id(
            db,ticket_id
        )
        print("After payload extraction")
        

        return json_payload

    else:
        raise HTTPException(
            status_code=400,
            detail="Alert details not found."
        )


#******************************** End Alert API agent  *******************************
################## End API agent  ##############################3


SYSTEM_ASSIGNEES = {
    "SYSTEM",
    "OPS MANAGER",
    "SUPPORT"
}

# User validation
def normalize_name(name: str) -> str:
    """Normalize names for matching."""
    return " ".join((name or "").strip().upper().split())


def get_assignee( assigned_to: str, users: list[UserMaster]):
    """
    Resolve assignee from database.

    Returns:
    {
        status:
            system
            found
            suggest
            multiple
            not_found

        assignee:
        user_id:
        email:
        user:
        candidates:
        message:
    }
    """

    assigned_to = normalize_name(assigned_to)

    if not assigned_to:
        return {
            "status": "not_found",
            "message": "Assignee not provided.",
            "assignee": None,
            "user_id": None,
            "email": None,
            "user": None,
            "candidates": []
        }

    # ----------------------------------------------------
    # Built-in assignees
    # ----------------------------------------------------

    if assigned_to in SYSTEM_ASSIGNEES:

        return {
            "status": "system",
            "message": "System assignee.",
            "assignee": assigned_to,
            "user_id": None,
            "email": None,
            "user": None,
            "candidates": []
        }

    # ----------------------------------------------------
    # Load active users
    # ----------------------------------------------------

    if not users:

        return {
            "status": "not_found",
            "message": "No active users configured.",
            "assignee": None,
            "user_id": None,
            "email": None,
            "user": None,
            "candidates": []
        }

    # ----------------------------------------------------
    # Exact Match
    # ----------------------------------------------------

    for user in users:

        if normalize_name(user.name) == assigned_to:

            return {
                "status": "found",
                "message": "Exact match found.",
                "assignee": user.name,
                "user_id": user.user_id,
                "email": user.email,
                "user": user,
                "candidates": []
            }

    # ----------------------------------------------------
    # Partial Match (Preferred for names)
    # ----------------------------------------------------

    partial_matches = []

    for user in users:

        full_name = normalize_name(user.name)

        tokens = full_name.split()

        if assigned_to == full_name or assigned_to in tokens:
            partial_matches.append(user)

            # Only one partial match -> Auto assign

            if len(partial_matches) == 1:

                user = partial_matches[0]

            return {
                "status": "found",
                "message": "Partial name matched.",
                "assignee": user.name,
                "user_id": user.user_id,
                "email": user.email,
                "user": user,
                "candidates": []
            }

    # Multiple partial matches -> Ask user

    if len(partial_matches) > 1:

        candidates = []

        for user in partial_matches:

            candidates.append({
                "id": user.user_id,
                "name": user.name,
                "email": user.email,
                "score": 100
            })

        return {
            "status": "multiple",
            "message": "Multiple users match the provided name.",
            "assignee": None,
            "user_id": None,
            "email": None,
            "user": None,
            "candidates": candidates
        }

    # ----------------------------------------------------
    # Fuzzy Match (Handles typos)
    # ----------------------------------------------------

    name_map = {
        normalize_name(user.name): user
        for user in users
    }

    matches = process.extract(
        assigned_to,
        name_map.keys(),
        scorer=fuzz.token_set_ratio,
        limit=5
    )

    # Score >= 90 -> Auto assign

    if matches and matches[0][1] >= 90:

        matched_name = matches[0][0]
        user = name_map[matched_name]

        return {
            "status": "found",
            "message": "Closest matching user selected.",
            "assignee": user.name,
            "user_id": user.user_id,
            "email": user.email,
            "user": user,
            "candidates": []
        }

    # Score 75-89 -> Confirmation required

    candidates = []

    for name, score, _ in matches:

        if score >= 75:

            user = name_map[name]

            candidates.append({
                "id": user.user_id,
                "name": user.name,
                "email": user.email,
                "score": round(score, 1)
            })

    if len(candidates) == 1:

        user = name_map[normalize_name(candidates[0]["name"])]

        return {
            "status": "suggest",
            "message": f'Did you mean "{user.name}"?',
            "assignee": user.name,
            "user_id": user.user_id,
            "email": user.email,
            "user": user,
            "candidates": candidates
        }

    if len(candidates) > 1:

        return {
            "status": "multiple",
            "message": "Multiple similar users found.",
            "assignee": None,
            "user_id": None,
            "email": None,
            "user": None,
            "candidates": candidates
        }

    # ----------------------------------------------------
    # No Match
    # ----------------------------------------------------

    nearest = []

    for name, score, _ in matches:

        user = name_map[name]

        nearest.append({
            "id": user.user_id,
            "name": user.name,
            "email": user.email,
            "score": round(score, 1)
        })

        return {
        "status": "not_found",
        "message": "No matching user found.",
        "assignee": None,
        "user_id": None,
        "email": None,
        "user": None,
        "candidates": nearest
    }

##################################################################
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
