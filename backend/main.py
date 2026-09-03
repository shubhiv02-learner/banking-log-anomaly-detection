import re
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Header, Query
from typing import Optional
from sqlalchemy.orm import Session, defer
from fastapi.middleware.cors import CORSMiddleware
from backend.notification import notify_n8n
from backend.database import SessionLocal
import backend.crud  as crud
import backend.schemas as schemas
from backend.db_models import  Ticket, UserMaster, Alert, WindowMetrics, IncidentAssignmentHistory

from rapidfuzz import process, fuzz
from backend.config import (
    N8N_ASSIGN_WEBHOOK,
    N8N_RESOLVE_WEBHOOK,
    N8N_CLOSE_WEBHOOK,
)
from backend.logging_config import get_logger, setup_logging
from backend.services.incident_actions import (
    IncidentActionError,
    apply_dashboard_incident_action,
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("SentryyIQ API starting")
    yield
    logger.info("SentryyIQ API shutting down")


app = FastAPI(
    title="SentryyIQ API",
    lifespan=lifespan,
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
try:
    users = crud.get_users(db)
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

    rows = crud.get_recent_window_metrics(db)
    return rows

@app.get(
    "/window-metrics/{metric_id}/summary",
    response_model=schemas.WindowMetricsTelemetrySummary,
)
def get_window_metric_telemetry_summary(
    metric_id: int,
    db: Session = Depends(get_db)
):
    summary = crud.get_window_metric_telemetry_summary(db, metric_id)
    if summary is None:
        raise HTTPException(
            status_code=404,
            detail="Window metric not found"
        )
    return summary

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
    service: Optional[list[str]] = Query(default=None),
    priority: Optional[list[str]] = Query(default=None),
    status: Optional[list[str]] = Query(default=None),
    assignee_scope: Optional[str] = Query(default=None),
    assignee: Optional[list[str]] = Query(default=None),
    db: Session = Depends(get_db),
):
    """
    Lists incidents by status.

    When ``status`` is omitted, defaults to OPEN only (open queue).
    Salveris sends ``status=OPEN&status=ASSIGNED`` for active / in-progress
    queries. Optional repeated ``service`` and ``priority`` prefilter the
    result (outbound authZ allow-lists).

    ``assignee_scope=mine`` with ``assignee`` names keeps OPEN/queue rows plus
    ASSIGNED rows for those names (operators). Omit or ``all`` for Ops Manager.
    """
    incidents = crud.get_agent_incidents(
        db=db,
        skip=skip,
        limit=limit,
        services=service,
        priorities=priority,
        statuses=status,
        assignee_scope=assignee_scope,
        assignees=assignee,
    )
    return incidents


@app.get(
    "/agent/incidents/details/{ind_details}",
    response_model=schemas.TicketDetRes
)
def get_agent_incident_by_id(
    ind_details: str,
    db: Session = Depends(get_db),
    x_salveris_acting_principal_id: Optional[str] = Header(
        default=None,
        alias="X-Salveris-Acting-Principal-Id",
    ),
):
    if x_salveris_acting_principal_id:
        logger.info(
            "Salveris acting principal on incident details: %s",
            x_salveris_acting_principal_id,
        )
    incident = crud.get_agent_incident_by_id(db, ind_details)
    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )
    return incident
   
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
    "/agent/error_mapping",
    response_model=schemas.ErrorMappingListResponse,
)
def list_agent_error_mapping(
    db: Session = Depends(get_db),
    x_salveris_acting_principal_id: Optional[str] = Header(
        default=None,
        alias="X-Salveris-Acting-Principal-Id",
    ),
):
    """Returns the full error_mapping catalog for Salveris list-all live fetch."""
    if x_salveris_acting_principal_id:
        logger.info(
            "Salveris acting principal on error_mapping list: %s",
            x_salveris_acting_principal_id,
        )
    return crud.list_error_mappings(db)


@app.get(
    "/agent/error_mapping/{error_code}",
    response_model=schemas.ErrorMappingResponse,
)
def get_agent_error_mapping(
    error_code: str,
    db: Session = Depends(get_db),
    x_salveris_acting_principal_id: Optional[str] = Header(
        default=None,
        alias="X-Salveris-Acting-Principal-Id",
    ),
):
    """Returns one operational error_mapping catalog row for Salveris live fetch."""
    if x_salveris_acting_principal_id:
        logger.info(
            "Salveris acting principal on error_mapping: %s code=%s",
            x_salveris_acting_principal_id,
            error_code,
        )
    mapping = crud.get_error_mapping_by_code(db, error_code)
    if mapping is None:
        raise HTTPException(status_code=404, detail="Error mapping not found")
    return mapping


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
    logger.debug("Assignment history requested incident_no=%s", incident_no)
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
    logger.info(
        "Incident assign request ticket=%s action=%s assigned_to=%s",
        request.ticket_details,
        request.action,
        request.assigned_to,
    )
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

    if request.action == schemas.IncidentAction.ASSIGNED and request.assigned_to == "SYSTEM":
        return {
            "status":"failed",
            "message": "assigned_to is required for ASSIGNED action."
        }
    if incident is None:
        logger.error("Assign failed — incident not found incident_no=%s", incident_no)
        return {
            "status": "failed",
            "message": "Incident not found, recheck the ticket number"
        }
    result = get_assignee(request.assigned_to, users)
    if result["status"] not in ("system", "found"):
        return {
            "status": result["status"],
            "message": result["message"],
            "candidates": result["candidates"]
            }
    user_assignee = result["assignee"].upper() if result["assignee"] else None
    assignee_email = result["email"]
    
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
        
    logger.info(
        "Applying incident update ticket_id=%s assignee=%s action=%s",
        incident.ticket_id,
        user_assignee,
        request.action,
    )
    
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
            logger.info(
                "Calling n8n assign webhook ticket_id=%s url=%s",
                incident.ticket_id,
                N8N_ASSIGN_WEBHOOK,
            )
            notify_n8n(N8N_ASSIGN_WEBHOOK, payload)
        except Exception:
            logger.exception("Failed to notify n8n assign webhook")
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

    if match:
        ticket_id = match[-1]
        alert_details = crud.get_agent_alert_details_by_id(
            db, ticket_id
        )
        if alert_details is None:
            raise HTTPException(
                status_code=404,
                detail="Alert details not found.",
            )
        return alert_details

    raise HTTPException(
        status_code=400,
        detail="Alert details not found.",
    )

##################Payload Details - Raw telemetry data for alert ###################

@app.get(
    "/agent/alerts/telemetry_summary/{ind_details}",
    response_model=schemas.WindowMetricsTelemetrySummary,
)
def get_agent_alert_telemetry_summary(
    ind_details: str,
    db: Session = Depends(get_db),
    x_salveris_acting_principal_id: Optional[str] = Header(
        default=None,
        alias="X-Salveris-Acting-Principal-Id",
    ),
):
    if x_salveris_acting_principal_id:
        logger.info(
            "Salveris acting principal on telemetry summary: %s",
            x_salveris_acting_principal_id,
        )
    match = re.findall(r"\d+", ind_details)
    if not match:
        raise HTTPException(
            status_code=400,
            detail="Alert details not found."
        )
    summary = crud.get_alert_telemetry_summary(db, match[-1])
    if summary is None:
        raise HTTPException(
            status_code=404,
            detail="Alert details not found."
        )
    return summary

@app.get(
    "/agent/alerts/raw_data/{ind_details}"
)
def get_agent_alert_payload_by_id(
    ind_details: str,
    skip: int = 0,
    limit: int | None = None,
    time_from: str | None = None,
    time_to: str | None = None,
    db: Session = Depends(get_db)
):
    # Extract the last number mentioned
    match = re.findall(r"\d+", ind_details)

    if match:
        ticket_id = match[-1]
        if ticket_id is None:
            raise HTTPException(
            status_code=404,
            detail="Alert details not found."
        )
        json_payload = crud.get_agent_alert_payload_by_id(
            db,
            ticket_id,
            skip=skip,
            limit=limit,
            time_from=time_from,
            time_to=time_to,
        )
        if json_payload is None:
            raise HTTPException(
                status_code=404,
                detail="Alert details not found.",
            )
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
# Copilot — Salveris knowledge (UI never calls Salveris directly)
##################################################################

from backend.integrations.salveris.exceptions import (
    SalverisAuthError,
    SalverisConfigError,
    SalverisError,
    SalverisUnavailable,
)
from backend.integrations.salveris.models import (
    CopilotAskRequest,
    CopilotAskResponse,
    CopilotSearchRequest,
    CopilotSearchResponse,
)
from backend.integrations.salveris.salveris_client import (
    CAPABILITY_KNOWLEDGE_ANSWER,
    CAPABILITY_KNOWLEDGE_SEARCH,
)
from backend.services.acting_principal import ActingPrincipalMissing
from backend.services.auth_service import (
    AuthConfigError,
    authenticate,
    create_access_token,
    decode_access_token,
    get_user_by_id,
)
from backend.services.copilot_service import copilot_service


def _map_salveris_http(exc: SalverisError) -> HTTPException:
    if isinstance(exc, SalverisConfigError):
        return HTTPException(status_code=503, detail=str(exc))
    if isinstance(exc, SalverisAuthError):
        return HTTPException(status_code=502, detail="Salveris authentication failed")
    if isinstance(exc, SalverisUnavailable):
        return HTTPException(status_code=502, detail="Salveris unavailable")
    status = exc.status_code if exc.status_code and 400 <= exc.status_code < 500 else 502
    return HTTPException(status_code=status, detail=str(exc))


def _auth_user_payload(user: UserMaster) -> schemas.AuthUser:
    return schemas.AuthUser(
        user_id=user.user_id,
        name=user.name,
        email=user.email,
        role=user.role,
    )


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> UserMaster:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        user_id = decode_access_token(token)
    except AuthConfigError:
        raise HTTPException(status_code=503, detail="Authentication is not configured") from None
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from None
    user = get_user_by_id(db, user_id)
    if user is None or not user.active:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


@app.get("/users", response_model=list[schemas.DashboardUser])
def list_dashboard_users(
    current_user: UserMaster = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logger.info("Dashboard users listed (user_id=%s)", current_user.user_id)
    return crud.get_users(db=db)


@app.post(
    "/tickets/assign",
    response_model=schemas.DashboardIncidentActionResponse,
)
def dashboard_incident_action(
    body: schemas.DashboardIncidentActionRequest,
    current_user: UserMaster = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return apply_dashboard_incident_action(db, body, current_user)
    except IncidentActionError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@app.post("/auth/login", response_model=schemas.LoginResponse)
def auth_login(body: schemas.LoginRequest, db: Session = Depends(get_db)):
    try:
        user = authenticate(db, body.email, body.password)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        token = create_access_token(user)
    except AuthConfigError:
        logger.error("Login failed because JWT_SECRET is not configured")
        raise HTTPException(status_code=503, detail="Authentication is not configured") from None
    return schemas.LoginResponse(
        access_token=token,
        token_type="bearer",
        user=_auth_user_payload(user),
    )


@app.get("/auth/me", response_model=schemas.AuthUser)
def auth_me(current_user: UserMaster = Depends(get_current_user)):
    return _auth_user_payload(current_user)


@app.post("/copilot/search", response_model=CopilotSearchResponse)
def copilot_search(
    request: CopilotSearchRequest,
    current_user: UserMaster = Depends(get_current_user),
):
    logger.info(
        "Copilot search started (capability='%s', user_id=%s)",
        CAPABILITY_KNOWLEDGE_SEARCH,
        current_user.user_id,
    )
    logger.debug(
        "Copilot search request (question_len=%d, has_context=%s)",
        len(request.question),
        request.context is not None,
    )
    try:
        result = copilot_service.search(
            request.question,
            context=request.context,
            user=current_user,
        )
        logger.info("Copilot search completed (%d hit(s))", len(result.hits))
        return result
    except ActingPrincipalMissing as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except SalverisError as exc:
        logger.error("Copilot search failed", exc_info=True)
        raise _map_salveris_http(exc) from exc


@app.post("/copilot/ask", response_model=CopilotAskResponse)
def copilot_ask(
    request: CopilotAskRequest,
    current_user: UserMaster = Depends(get_current_user),
):
    logger.info(
        "Copilot ask started (capability='%s', user_id=%s)",
        CAPABILITY_KNOWLEDGE_ANSWER,
        current_user.user_id,
    )
    logger.debug(
        "Copilot ask request (question_len=%d, has_context=%s)",
        len(request.question),
        request.context is not None,
    )
    try:
        result = copilot_service.ask(
            request.question,
            context=request.context,
            user=current_user,
        )
        logger.info(
            "Copilot ask completed (%d source(s))",
            len(result.sources),
        )
        return result
    except ActingPrincipalMissing as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except SalverisError as exc:
        logger.error("Copilot ask failed", exc_info=True)
        raise _map_salveris_http(exc) from exc


##################################################################
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
