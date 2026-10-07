import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logging_config import get_logger

logger = get_logger(__name__)

from config import KAFKA_ENABLED, WINDOW_SIZE_MINUTES
from consumer.window_pipeline import get_pipeline, process_service_window
from src.generate_banking_logs_metrics import (
    apply_bayesian_prioritization,
    apply_cusum_detection,
    apply_ewma_detection,
    calculate_persistence_score,
)

_REQUIRED_COLUMNS = (
    "timestamp",
    "service",
    "latency_ms",
    "cpu_usage",
    "memory_usage",
    "queue_lag",
    "error_count",
)


def _plain_value(value):
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return None if np.isnan(value) else float(value)
    if isinstance(value, float) and np.isnan(value):
        return None
    if isinstance(value, np.bool_):
        return bool(value)
    return value


def _plain_records(frame):
    rows = frame.to_dict(orient="records")
    return [{key: _plain_value(value) for key, value in row.items()} for row in rows]


def kafka_enabled():
    return bool(KAFKA_ENABLED)


def replay_csv():
    """Read the producer CSV, run batch metrics, and save each timestamp window."""
    raw_path = os.getenv("OUTPUT_DATA_LOG_PATH_CSV")
    if not raw_path:
        logger.error("OUTPUT_DATA_LOG_PATH_CSV is not set")
        raise ValueError("OUTPUT_DATA_LOG_PATH_CSV is not set")

    csv_path = Path(raw_path)
    if not csv_path.is_file():
        logger.error("Batch replay CSV not found path=%s", csv_path)
        raise FileNotFoundError("CSV file not found")

    logger.info(
        "Batch replay started path=%s window_size_minutes=%s",
        csv_path,
        WINDOW_SIZE_MINUTES,
    )
    df = pd.read_csv(csv_path)
    missing = [name for name in _REQUIRED_COLUMNS if name not in df.columns]
    if missing:
        logger.error("Batch replay CSV missing columns=%s", missing)
        raise ValueError("CSV is missing required columns: " + ", ".join(missing))

    df["timestamp"] = pd.to_datetime(df["timestamp"], format="mixed", dayfirst=True, utc=True)
    df = df.dropna(subset=["timestamp"]).sort_values("timestamp")
    for column in ("latency_ms", "cpu_usage", "memory_usage", "queue_lag", "error_count"):
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)

    if df.empty:
        logger.info("Batch replay finished rows=0 windows=0")
        return {
            "windows_written": 0,
            "alerts_written": 0,
            "services": [],
            "rows": 0,
            "failures": 0,
        }

    df, _threshold = apply_ewma_detection(df)
    df = apply_cusum_detection(df)
    df = calculate_persistence_score(df)
    df = apply_bayesian_prioritization(df)
    df["ewma"] = pd.to_numeric(df["ewma_latency"], errors="coerce").fillna(0)
    df["incident_probability"] = (
        pd.to_numeric(df["incident_probability"], errors="coerce")
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0)
    )
    df["cusum"] = pd.to_numeric(df["cusum"], errors="coerce").fillna(0)
    df["persistence_score"] = pd.to_numeric(df["persistence_score"], errors="coerce").fillna(0)

    df["window_start"] = df["timestamp"].dt.floor(f"{WINDOW_SIZE_MINUTES}min")
    detector, ensemble, error_mapping = get_pipeline()

    windows_written = 0
    alerts_written = 0
    failures = 0
    services = sorted(df["service"].dropna().astype(str).unique().tolist())

    for (service, window_start), group in df.groupby(["service", "window_start"], sort=True):
        start = window_start.to_pydatetime()
        end = start + timedelta(minutes=WINDOW_SIZE_MINUTES)
        records = _plain_records(group.drop(columns=["window_start"]))
        try:
            result = process_service_window(
                service=str(service),
                records=records,
                raw_records=records,
                window_start=start,
                window_end=end,
                detector=detector,
                ensemble=ensemble,
                error_mapping=error_mapping,
            )
        except Exception:
            failures += 1
            logger.exception(
                "Batch window failed service=%s window_start=%s",
                service,
                start.isoformat(),
            )
            continue
        windows_written += result["window_written"]
        alerts_written += result["alert_written"]

    logger.info(
        "Batch replay finished rows=%s windows=%s alerts=%s failures=%s services=%s",
        len(df),
        windows_written,
        alerts_written,
        failures,
        services,
    )
    return {
        "windows_written": windows_written,
        "alerts_written": alerts_written,
        "services": services,
        "rows": int(len(df)),
        "failures": failures,
    }
