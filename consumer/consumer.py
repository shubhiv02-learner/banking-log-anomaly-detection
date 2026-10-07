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

import pandas as pd
from kafka import KafkaConsumer

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logging_config import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)

from config import WINDOW_SIZE_MINUTES
from consumer.window_pipeline import process_service_window
from src.detector import EnsembleDetector
from src.ensemble import EnsembleEngine
from src.stream_metrics import StreamMetrics

from backend.db_services import load_error_mapping

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

            record = metrics_engine.update(record)
            service = record["service"]
            raw_record_buffer[service].append(record)
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
                    process_service_window(
                        service=service,
                        records=records,
                        raw_records=raw_record_buffer[service],
                        window_start=window_start,
                        window_end=window_end,
                        detector=detector,
                        ensemble=ensemble,
                        error_mapping=ERROR_MAPPING,
                    )

                service_buffers.clear()
                raw_record_buffer.clear()
                window_start = datetime.now(timezone.utc)
                window_end = window_start + timedelta(minutes=WINDOW_SIZE_MINUTES)
                logger.info(
                    "New window starting window_start=%s window_end=%s",
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
