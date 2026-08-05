from backend.database import SessionLocal
from backend.db_models import WindowMetrics, Alert, Ticket
from backend.logging_config import get_logger
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from datetime import datetime
from sqlalchemy import text

logger = get_logger(__name__)


def save_window_metric(window_metric_data):
    db = SessionLocal()
    service = window_metric_data.get("service")
    try:
        metric = WindowMetrics(**window_metric_data)
        db.add(metric)
        db.commit()
        db.refresh(metric)
        logger.info(
            "Inserted window_metric id=%s service=%s prediction=%s priority=%s",
            metric.id,
            service,
            window_metric_data.get("prediction"),
            window_metric_data.get("priority"),
        )
        return metric
    except Exception:
        db.rollback()
        logger.exception(
            "Failed to insert window_metric for service=%s",
            service,
        )
        raise
    finally:
        db.close()


def save_alert(alert_data):
    db = SessionLocal()
    try:
        alert = Alert(**alert_data)
        db.add(alert)
        db.commit()
        db.refresh(alert)
        logger.info(
            "Inserted alert id=%s service=%s priority=%s window_metric_id=%s",
            alert.id,
            alert.service,
            alert.priority,
            alert.window_metric_id,
        )
        return alert
    except Exception:
        db.rollback()
        logger.exception(
            "Failed to insert alert for service=%s",
            alert_data.get("service"),
        )
        raise
    finally:
        db.close()


def save_ticket(ticket_data):
    db = SessionLocal()
    ticket = None
    try:
        ticket = Ticket(**ticket_data)
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        logger.info(
            "Inserted ticket ticket_id=%s alert_id=%s priority=%s",
            ticket.ticket_id,
            ticket.alert_id,
            ticket.priority,
        )
        return ticket
    except Exception:
        db.rollback()
        logger.exception(
            "Failed to insert ticket alert_id=%s",
            ticket_data.get("alert_id"),
        )
        raise
    finally:
        db.close()
        if ticket is not None and ticket.priority == "Critical":
            logger.info(
                "Critical ticket %s — notifying n8n",
                ticket.ticket_id,
            )
            notified = notify_n8n(ticket)
            if notified is not None:
                update_ticket_Notified(ticket.ticket_id)


def notify_n8n(incident):
    payload = json.dumps(
        {
            "ticket_id": incident.ticket_id,
            "service": incident.service,
            "priority": incident.priority,
            "status": incident.status,
        }
    ).encode("utf-8")

    request = Request(
        "http://localhost:5678/webhook/critical-incident",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=5) as response:
            body = response.read()
            logger.info(
                "n8n critical-incident webhook succeeded ticket_id=%s",
                incident.ticket_id,
            )
            return body
    except HTTPError as e:
        logger.error(
            "n8n webhook HTTP error ticket_id=%s code=%s reason=%s",
            incident.ticket_id,
            e.code,
            e.reason,
        )
        return None
    except URLError as e:
        logger.error(
            "n8n webhook URL error ticket_id=%s reason=%s",
            incident.ticket_id,
            e.reason,
        )
        return None
    except Exception:
        logger.exception(
            "n8n webhook failed ticket_id=%s",
            incident.ticket_id,
        )
        return None


def update_ticket_Notified(tick_id):
    db = SessionLocal()
    try:
        existing_record = db.query(Ticket).filter_by(ticket_id=tick_id).first()
        if existing_record:
            existing_record.notification_sent = True
            existing_record.notification_time = datetime.utcnow()
            db.commit()
            logger.info("Updated ticket notification_sent ticket_id=%s", tick_id)
        else:
            logger.error(
                "Cannot update notification flag — ticket not found ticket_id=%s",
                tick_id,
            )
    except Exception:
        db.rollback()
        logger.exception(
            "Failed to update notification_sent ticket_id=%s",
            tick_id,
        )
        raise
    finally:
        db.close()


def update_window_payload(payload_summary, payload_json, win_id):
    db = SessionLocal()
    try:
        existing_record = db.query(WindowMetrics).filter_by(id=win_id).first()
        if existing_record:
            existing_record.payload_summary = payload_summary
            existing_record.payload_json = payload_json
            db.commit()
            logger.info(
                "Updated window_metric payload window_metric_id=%s record_count=%s",
                win_id,
                payload_summary.get("record_count") if isinstance(payload_summary, dict) else None,
            )
        else:
            logger.error(
                "Cannot update payload — window_metric not found id=%s",
                win_id,
            )
    except Exception:
        db.rollback()
        logger.exception(
            "Failed to update window_metric payload id=%s",
            win_id,
        )
        raise
    finally:
        db.close()


def load_error_mapping():
    db = SessionLocal()
    try:
        rows = db.execute(
            text(
                """
    SELECT
        error_code,
        error_name,
        description AS root_cause_description,
        business_impact,
        customer_impact,
        recommended_action,
        severity_default,
        category
    FROM error_mapping
    """
            )
        ).fetchall()

        mapping = {
            row.error_code: {
                "error_name": row.error_name,
                "root_cause_description": row.root_cause_description,
                "business_impact": row.business_impact,
                "customer_impact": row.customer_impact,
                "recommended_action": row.recommended_action,
                "severity_default": row.severity_default,
                "category": row.category,
            }
            for row in rows
        }
        logger.info("Loaded error_mapping entries=%s", len(mapping))
        return mapping
    except Exception:
        logger.exception("Failed to load error_mapping from database")
        raise
    finally:
        db.close()
