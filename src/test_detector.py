import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logging_config import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)

import pandas as pd
from detector import EnsembleDetector

detector = EnsembleDetector()
logger.info("EnsembleDetector loaded")

sample = pd.DataFrame(
    [
        {
            "service": "payment-service",
            "latency_ms_mean": 220,
            "latency_ms_max": 450,
            "latency_ms_std": 50,
            "cpu_usage_mean": 60,
            "cpu_usage_max": 85,
            "memory_usage_mean": 72,
            "queue_lag_mean": 10,
            "queue_lag_max": 30,
            "error_count_sum": 5,
        }
    ]
)

result = detector.score_window(sample)
logger.info("Sample window score result=%s", result)
