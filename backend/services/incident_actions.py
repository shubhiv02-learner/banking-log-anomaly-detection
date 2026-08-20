"""Dashboard assign/resolve/close. Telegram keeps POST /agent/incidents/assign."""

from __future__ import annotations

from sqlalchemy.orm import Session, defer

from backend.config import N8N_ASSIGN_WEBHOOK
from backend.db_models import Ticket, UserMaster
from backend.logging_config import get_logger
from backend.notification import notify_n8n
import backend.crud as crud
import backend.schemas as schemas

_logger = get_logger(__name__)

MIN_REMARKS_LEN = 5
ALLOWED_TRANSITIONS: dict[schemas.IncidentAction, set[str]] = {
    schemas.IncidentAction.ASSIGNED: {"OPEN"},
    schemas.IncidentAction.RESOLVED: {"ASSIGNED"},
    schemas.IncidentAction.CLOSED: {"RESOLVED"},
}
_BLOCKED_ASSIGNEES = {"SYSTEM", "OPS MANAGER", "SUPPORT"}


class IncidentActionError(Exception):
    """User-facing dashboard incident action failure."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _normalize_name(name: str) -> str:
    return " ".join((name or "").strip().upper().split())


def _require_text(value: str | None, field: str) -> str:
    text = (value or "").strip()
    if len(text) < MIN_REMARKS_LEN:
        raise IncidentActionError(
            f"{field} must be at least {MIN_REMARKS_LEN} characters."
        )
    return text


def _find_ticket(db: Session, ticket_id: str) -> Ticket:
    incident = (
        db.query(Ticket)
        .filter(Ticket.ticket_id == ticket_id)
        .options(defer(Ticket.incident_summary))
        .first()
    )
    if incident is None:
        _logger.info("Dashboard incident action failed (reason='not_found')")
        raise IncidentActionError("Incident not found.", status_code=404)
    return incident


def _match_assignee(db: Session, assigned_to: str | None) -> UserMaster:
    wanted = _normalize_name(assigned_to or "")
    if not wanted or wanted in _BLOCKED_ASSIGNEES:
        raise IncidentActionError("Select an active assignee.")
    for user in crud.get_users(db):
        if _normalize_name(user.name) == wanted:
            return user
    raise IncidentActionError("Assignee was not found among active users.")


def _compose_close_remarks(closure_remark: str | None, preventive_action: str | None) -> str:
    closure = _require_text(closure_remark, "Closure remark")
    preventive = _require_text(preventive_action, "Preventive action")
    return f"Closure Remark: {closure}\nPreventive Action: {preventive}"


def apply_dashboard_incident_action(
    db: Session,
    request: schemas.DashboardIncidentActionRequest,
    actor: UserMaster,
) -> schemas.DashboardIncidentActionResponse:
    incident = _find_ticket(db, request.ticket_id)
    current_status = (incident.status or "").strip().upper()
    allowed = ALLOWED_TRANSITIONS.get(request.action, set())

    if current_status == "CLOSED":
        raise IncidentActionError("Incident is already closed, cannot change status.")
    if current_status not in allowed:
        raise IncidentActionError(
            f"Cannot {request.action.value.lower()} an incident in {current_status or 'unknown'} status."
        )

    assignee_name = incident.assignee
    assignee_email = None

    if request.action == schemas.IncidentAction.ASSIGNED:
        user = _match_assignee(db, request.assigned_to)
        assignee_name = (user.name or "").upper()
        assignee_email = user.email
        if _normalize_name(incident.assignee or "") == _normalize_name(assignee_name):
            raise IncidentActionError(
                f"Incident is already assigned to {assignee_name}."
            )
        remarks = (request.remarks or "").strip() or None
    elif request.action == schemas.IncidentAction.RESOLVED:
        remarks = _require_text(request.remarks, "Resolution remarks")
        if not (incident.assignee or "").strip():
            raise IncidentActionError("Incident must have an assignee before it can be resolved.")
        assignee_name = incident.assignee
    else:
        remarks = _compose_close_remarks(
            request.closure_remark,
            request.preventive_action,
        )
        assignee_name = incident.assignee

    _logger.info(
        "Dashboard incident update started (ticket_id='%s', action='%s', user_id=%s)",
        incident.ticket_id,
        request.action.value,
        actor.user_id,
    )

    assignment = crud.assign_incident(
        db=db,
        incident=incident,
        assigned_to=assignee_name,
        remarks=remarks,
        prevt_remarks=None,
        action=request.action,
        assigned_by=actor.name or "OPS MANAGER",
    )
    if assignment is None:
        raise IncidentActionError("Incident not found.", status_code=404)

    if request.action == schemas.IncidentAction.ASSIGNED:
        payload = {
            "ticket_id": incident.ticket_id,
            "service": incident.service,
            "priority": incident.priority,
            "status": incident.status,
            "assignee": assignee_name.title() if assignee_name else None,
            "email": assignee_email,
            "remarks": remarks,
        }
        try:
            _logger.info(
                "Calling n8n assign webhook ticket_id=%s",
                incident.ticket_id,
            )
            notify_n8n(N8N_ASSIGN_WEBHOOK, payload)
        except Exception:
            _logger.exception("Failed to notify n8n assign webhook")
        message = (
            f"Incident {incident.ticket_id} assigned successfully to {assignee_name}."
        )
    elif request.action == schemas.IncidentAction.RESOLVED:
        message = f"Incident {incident.ticket_id} resolved successfully."
    else:
        message = f"Incident {incident.ticket_id} closed successfully."

    _logger.info(
        "Dashboard incident update completed (ticket_id='%s', action='%s')",
        incident.ticket_id,
        request.action.value,
    )
    return schemas.DashboardIncidentActionResponse(
        action=request.action,
        message=message,
        ticket_id=incident.ticket_id,
        status=incident.status,
        assignee=incident.assignee,
    )
