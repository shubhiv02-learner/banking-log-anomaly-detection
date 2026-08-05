# Kafka Message
#      |
# StreamMetrics.update()
#     |
# Buffer
#     |
# 5-minute window complete?
#     |
# create_window_features()
#     |
# detector.score_window()
#     |
# ensemble score
#     |
# save to PostgreSQL - window_metrics → increasing every window
#                    alerts → increasing only when anomaly detected

import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from kafka import KafkaConsumer

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logging_config import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)

from config import WINDOW_SIZE_MINUTES
from src.detector import EnsembleDetector
from src.enrichment import (
    build_incident_summary,
    build_payload_details,
    enrich_incident_details,
    enrich_metrics_details,
)
from src.ensemble import EnsembleEngine
from src.feature_engineering import create_window_features
from src.stream_metrics import StreamMetrics

from backend.db_services import (
    load_error_mapping,
    save_alert,
    save_ticket,
    save_window_metric,
    update_window_payload,
)

metrics_engine = StreamMetrics()
detector = EnsembleDetector()
ensemble = EnsembleEngine()

logger.info("Loading error_mapping master data")
ERROR_MAPPING = load_error_mapping()
logger.info(
    "Consumer components initialized (window_size_minutes=%s)",
    WINDOW_SIZE_MINUTES,
)

service_buffers = defaultdict(list)
raw_record_buffer = defaultdict(list)

consumer = KafkaConsumer(
    "banking_logs",
    bootstrap_servers=["host.docker.internal:9092"],
    auto_offset_reset="earliest",
    enable_auto_commit=False,
    group_id=None,
)

logger.info(
    "Kafka consumer connected topic=banking_logs bootstrap=host.docker.internal:9092"
)

current_time = datetime.now(timezone.utc)
window_start = current_time
window_end = window_start + timedelta(minutes=WINDOW_SIZE_MINUTES)

try:
    for message in consumer:
        try:
            current_time = datetime.now(timezone.utc)
            if message is None:
                logger.debug("Poll returned no message")
                continue
            try:
                raw_value = message.value.decode("utf-8")
                record = json.loads(raw_value)
                record["timestamp"] = pd.to_datetime(
                    record["timestamp"], format="mixed", dayfirst=True
                )
            except (UnicodeDecodeError, json.JSONDecodeError, TypeError, KeyError) as e:
                logger.error("Skipping malformed Kafka message: %s", e)
                continue

            raw_record_buffer[record["service"]].append(record)
            record = metrics_engine.update(record)
            service = record["service"]
            service_buffers[service].append(record)

            if current_time > window_end:
                service_counts = {k: len(v) for k, v in service_buffers.items()}
                logger.info(
                    "Window closed %s -> %s services=%s records=%s",
                    window_start.isoformat(),
                    window_end.isoformat(),
                    list(service_counts.keys()),
                    service_counts,
                )

                for service, records in list(service_buffers.items()):
                    if len(records) == 0:
                        continue

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
                        "incident_probability": window_df.iloc[0][
                            "incident_probability_mean"
                        ],
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
                    window_df["prediction"] = np.array(
                        ensemble_result["prediction"]
                    ).astype(int)
                    window_df["priority"] = ensemble_result["priority"]
                    window_df["window_start"] = window_start
                    window_df["window_end"] = window_end
                    window_df["record_count"] = len(records)
                    window_metric_data = window_df.iloc[0].to_dict()

                    metric = save_window_metric(window_metric_data)

                    if ensemble_result["prediction"]:
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
                        records_list = raw_record_buffer[service]
                        payload_summary, payload_json = build_payload_details(
                            records_list, ERROR_MAPPING
                        )
                        if payload_summary is None:
                            logger.error(
                                "Payload build failed service=%s window_metric_id=%s — skipping alert/ticket",
                                service,
                                metric.id,
                            )
                            continue

                        raw_errors = payload_summary["top_errors"]
                        top_errors = [
                            e if str(e).startswith("ERR") else "ERR-UNK"
                            for e in raw_errors
                        ]

                        metrics_details = enrich_metrics_details(
                            top_errors, ERROR_MAPPING
                        )
                        metric_payload_summary = payload_summary
                        metric_payload_summary["metrics_details"] = metrics_details
                        update_window_payload(
                            metric_payload_summary, payload_json, metric.id
                        )

                        alert = save_alert(alert_data)

                        ticket_details = enrich_incident_details(
                            top_errors, ERROR_MAPPING
                        )
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

                service_buffers.clear()
                raw_record_buffer.clear()
                window_start = datetime.now(timezone.utc)
                window_end = window_start + timedelta(minutes=WINDOW_SIZE_MINUTES)
                logger.info(
                    "Window buffers cleared; next window %s -> %s",
                    window_start.isoformat(),
                    window_end.isoformat(),
                )

        except Exception as e:
            logger.exception("Error processing Kafka message: %s", e)
            continue

except KeyboardInterrupt:
    logger.info("Consumer interrupted — shutting down")
    consumer.close()

except Exception:
    logger.exception("Fatal consumer error — closing Kafka connection")
    consumer.close()
