from backend.database import SessionLocal
from backend.db_models import WindowMetrics, Alert, Ticket
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from datetime import datetime
from sqlalchemy import text


def save_window_metric(window_metric_data):

    db = SessionLocal()
    print("In save window metric session created successfully")
    try:
        metric = WindowMetrics(**window_metric_data)
        print("In db services metric data copied")
        db.add(metric)
        print("In db services metric data added to db")
        db.commit()

        db.refresh(metric)

        return metric

    finally:
        print(f"In db services session closed successfully in case of exception")
        db.close()


def save_alert(alert_data):

    db = SessionLocal()

    try:
        alert = Alert(**alert_data)

        db.add(alert)

        db.commit()

        db.refresh(alert)

        return alert

    finally:
        db.close()

def save_ticket(ticket_data):

    db = SessionLocal()

    try:
        ticket = Ticket(**ticket_data)

        db.add(ticket)

        db.commit()

        db.refresh(ticket)

        return ticket

    finally:
        db.close()
        if  ticket.priority == "Critical":
            print(f"Ticket priority{ticket.priority}")
            notified =  notify_n8n(ticket)
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

    # Fixed the missing comma syntax error. 
    # Removed timeout from Request since it belongs in urlopen.
    request = Request(
        "http://localhost:5678/webhook/critical-incident",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    print(f"In notify n8n {request}")

    try:
        # Timeout is strictly enforced here during connection/read (5 seconds)
        with urlopen(request, timeout=5) as response:
            return response.read()

    # Specific catch for HTTP errors (e.g., 404, 500)
    except HTTPError as e:
        print(
            f"Failed to notify n8n: HTTP Error {e.code} - {e.reason}"
        )
        return None

    # Specific catch for network/URL issues
    except URLError as e:
        print(f"Failed to notify n8n: URL Error - {e.reason}")
        return None

    # Catch-all for any other unexpected exceptions (including timeouts)
    except Exception as ex:
        print(f"Failed to notify n8n: {ex}")
        return None
    
    return None

def update_ticket_Notified(tick_id):

    db = SessionLocal()

    try:
        #ticket = Ticket(**ticket_data)
        # Update ticket in the database based on ticket_id
        existing_record = db.query(Ticket).filter_by(ticket_id=tick_id).first()
        if existing_record:
            existing_record.notification_sent = True
            existing_record.notification_time = datetime.utcnow()
        
            # Remember to commit the changes
    
            db.commit()

            #db.refresh()

        return 

    finally:
        db.close()

def update_window_payload(payload_summary, payload_json, win_id):
    db = SessionLocal()

    try:

        # Update window in the database based on window_id, add payload details
        existing_record = db.query(WindowMetrics).filter_by(id=win_id).first()
        if existing_record:
            existing_record.payload_summary = payload_summary
            existing_record.payload_json = payload_json
        
            # Remember to commit the changes
            db.commit()
        return 

    finally:
        db.close()

def load_error_mapping():
    db = SessionLocal()
    rows = db.execute(text("""
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
    """)).fetchall()

    return {
        row.error_code: {
            "error_name": row.error_name,
            "root_cause_description": row.root_cause_description,
            "business_impact": row.business_impact,
            "customer_impact": row.customer_impact,
            "recommended_action": row.recommended_action,
            "severity_default": row.severity_default,
            "category": row.category
        }
        for row in rows
    }