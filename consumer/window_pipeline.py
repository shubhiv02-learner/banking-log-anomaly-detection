import sys
from datetime import datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logging_config import get_logger

logger = get_logger(__name__)

from src.detector import EnsembleDetector
from src.enrichment import (
    build_incident_summary,
    build_payload_details,
    enrich_incident_details,
    enrich_metrics_details,
)
from src.ensemble import EnsembleEngine
from src.feature_engineering import create_window_features

from backend.db_services import (
    load_error_mapping,
    save_alert,
    save_ticket,
    save_window_metric,
    update_window_payload,
)

_detector = None
_ensemble = None
_error_mapping = None


def get_pipeline():
    """Load detector models and error mapping once per process."""
    global _detector, _ensemble, _error_mapping
    if _detector is None:
        logger.info("Loading batch replay detector and error mapping")
        _detector = EnsembleDetector()
        _ensemble = EnsembleEngine()
        _error_mapping = load_error_mapping()
    return _detector, _ensemble, _error_mapping


def process_service_window(
    service,
    records,
    raw_records,
    window_start,
    window_end,
    detector,
    ensemble,
    error_mapping,
):
    """Score one service window and write metrics, alerts, and tickets.

    Returns counts for the window. Raises if scoring or the metric insert fails.
    A payload failure still counts the window and skips the alert.
    """
    if len(records) == 0:
        return {"window_written": 0, "alert_written": 0}

    compact_records = [
        {
            "timestamp": str(r.get("timestamp")),
            "service": r.get("service"),
            "status": r.get("status"),
            "endpoint": r.get("endpoint"),
            "error_code": r.get("error_code"),
            "latency_ms": r.get("latency_ms"),
        }
        for r in records
    ]
    logger.debug(
        "create_window_features input service=%s record_count=%s records=%s",
        service,
        len(records),
        compact_records,
    )
    window_df = create_window_features(records)
    ml_result = detector.score_window(window_df)
    ensemble_input = {
        "service": service,
        "window_start": window_start,
        "window_end": window_end,
        "record_count": len(records),
        "if_score": ml_result["if_score_raw"],
        "ocsvm_score": ml_result["ocsvm_score_raw"],
        "ewma": window_df.iloc[0]["ewma_mean"],
        "cusum": window_df.iloc[0]["cusum_max"],
        "persistence": window_df.iloc[0]["persistence_score_mean"],
        "incident_probability": window_df.iloc[0]["incident_probability_mean"],
    }
    ensemble_result = ensemble.predict(ensemble_input)
    logger.info(
        "Scored service=%s records=%s prediction=%s priority=%s final_score=%s",
        service,
        len(records),
        ensemble_result["prediction"],
        ensemble_result["priority"],
        ensemble_result["final_score"],
    )
    logger.debug(
        "Ensemble detail service=%s ml_score=%s statistical_score=%s if=%s ocsvm=%s",
        service,
        ensemble_result.get("ml_score"),
        ensemble_result.get("statistical_score"),
        ensemble_input["if_score"],
        ensemble_input["ocsvm_score"],
    )

    window_df = window_df.rename(
        columns={
            "latency_ms_mean": "latency_mean",
            "latency_ms_max": "latency_max",
            "latency_ms_std": "latency_std",
            "cpu_usage_mean": "cpu_mean",
            "cpu_usage_max": "cpu_max",
            "memory_usage_mean": "memory_mean",
            "ewma_mean": "ewma",
            "cusum_max": "cusum",
            "persistence_score_mean": "persistence_score",
            "incident_probability_mean": "incident_probability",
            "error_count_sum": "error_count",
        }
    )
    window_df["service"] = service
    window_df["ml_score"] = ensemble_result["ml_score"]
    window_df["statistical_score"] = ensemble_result["statistical_score"]
    window_df["final_score"] = ensemble_result["final_score"]
    window_df["prediction"] = np.array(ensemble_result["prediction"]).astype(int)
    window_df["priority"] = ensemble_result["priority"]
    window_df["window_start"] = window_start
    window_df["window_end"] = window_end
    window_df["record_count"] = len(records)
    window_metric_data = window_df.iloc[0].to_dict()

    metric = save_window_metric(window_metric_data)

    if not ensemble_result["prediction"]:
        return {"window_written": 1, "alert_written": 0}

    logger.info(
        "Anomaly detected service=%s priority=%s score=%s window_metric_id=%s",
        service,
        ensemble_result["priority"],
        ensemble_result["final_score"],
        metric.id,
    )
    alert_data = {
        "window_metric_id": metric.id,
        "service": service,
        "final_score": ensemble_result["final_score"],
        "priority": ensemble_result["priority"],
    }
    payload_summary, payload_json = build_payload_details(raw_records, error_mapping)
    if payload_summary is None:
        logger.error(
            "Payload build failed service=%s window_metric_id=%s — skipping alert/ticket",
            service,
            metric.id,
        )
        return {"window_written": 1, "alert_written": 0}

    raw_errors = payload_summary["top_errors"]
    top_errors = [e if str(e).startswith("ERR") else "ERR-UNK" for e in raw_errors]

    metrics_details = enrich_metrics_details(top_errors, error_mapping)
    metric_payload_summary = payload_summary
    metric_payload_summary["metrics_details"] = metrics_details
    update_window_payload(metric_payload_summary, payload_json, metric.id)

    alert = save_alert(alert_data)

    ticket_details = enrich_incident_details(top_errors, error_mapping)
    ticket_payload_summary = payload_summary
    ticket_payload_summary["metrics_details"] = ticket_details

    ticket_data = {
        "alert_id": alert.id,
        "ticket_id": f"INC-{datetime.now().strftime('%Y%m%d')}-{alert.id}",
        "service": alert.service,
        "priority": alert.priority,
        "incident_summary": ticket_payload_summary,
        "assignee": "SUPPORT",
    }
    save_ticket(ticket_data)
    logger.info(
        "Incident pipeline complete service=%s alert_id=%s ticket_id=%s",
        service,
        alert.id,
        ticket_data["ticket_id"],
    )

    if alert.priority in ["HIGH", "CRITICAL"]:
        build_incident_summary(
            service,
            alert.priority,
            payload_summary,
        )

    return {"window_written": 1, "alert_written": 1}
