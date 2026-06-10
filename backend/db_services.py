from backend.database import SessionLocal
from backend.db_models import WindowMetrics, Alert


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