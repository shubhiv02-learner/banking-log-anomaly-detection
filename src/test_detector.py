import pandas as pd
#import detector as detector
from detector import EnsembleDetector

detector = EnsembleDetector()

print(detector)

sample = pd.DataFrame([
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

        "error_count_sum": 5
    }
])

print(
    detector.score_window(sample)
)