from backend.database import SessionLocal
from backend.db_models import WindowMetrics, Alert, Ticket
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


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
        notify_n8n(ticket)


def notify_n8n(incident):
    payload = json.dumps({
        "ticket_id": incident.ticket_id,
        "service": incident.service,
        "priority": incident.priority,
        "status": incident.status
    }).encode("utf-8")

    request = Request(
        "http://localhost:5678/webhook/critical-incident",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urlopen(request, timeout=5) as response:
            return response.read()
    except (HTTPError, URLError):
        return None