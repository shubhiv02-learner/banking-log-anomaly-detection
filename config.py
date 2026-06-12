# Window Configuration
WINDOW_SIZE_MINUTES = 0.5 #later 5

# Rolling Normalization
ROLLING_NORMALIZATION_WINDOW = 2 #temp 2, 288 × 5 min = 24 hours

# Warm-up windows before normalization becomes active
#there is no meaningful min/max range.
#This allows the system to gather enough data to establish a baseline for normalization.
NORMALIZATION_WARMUP_WINDOWS = 1   # temp 1, 10 windows × 5 min = 50 minutes of data before normalization starts

EWMA_ALERT_THRESHOLD = 100
CUSUM_ALERT_THRESHOLD = 200 
EWMA_ALPHA = 0.3
CUSUM_THRESHOLD = 100

# Ensemble Thresholds
GLOBAL_THRESHOLD = 0.70

CRITICAL_THRESHOLD = 0.90
HIGH_THRESHOLD = 0.75
MEDIUM_THRESHOLD = 0.50

# ML Weights
ML_IF_WEIGHT = 0.80
ML_OCSVM_WEIGHT = 0.20

# Statistical Weights
STAT_EWMA_WEIGHT = 0.25
STAT_CUSUM_WEIGHT = 0.25
STAT_PERSISTENCE_WEIGHT = 0.20
STAT_INCIDENT_WEIGHT = 0.30

# Final Ensemble Weights
FINAL_ML_WEIGHT = 0.60
FINAL_STAT_WEIGHT = 0.40

#Yet to be implemented
# 2. Define standard maximum thresholds per microservice/endpoint for clean sorting
BASELINE_STANDARDS = {
    ("auth-service", "/login"): {"max_latency": 80, "max_cpu": 50, "max_memory": 80, "max_queue": 5},
    ("payment-api", "/transfer"): {"max_latency": 250, "max_cpu": 120, "max_memory": 200, "max_queue": 15},
    ("payment-api", "/withdrawal"): {"max_latency": 250, "max_cpu": 120, "max_memory": 200, "max_queue": 15},
    ("trading-engine", "/trade"): {"max_latency": 15, "max_cpu": 300, "max_memory": 512, "max_queue": 2},
    ("fraud-detection", "/payment"): {"max_latency": 150, "max_cpu": 400, "max_memory": 1024, "max_queue": 10},
    ("ledger-service", "/balance_check"): {"max_latency": 30, "max_cpu": 30, "max_memory": 60, "max_queue": 5},
    ("investment-engine", "/portfolio"): {"max_latency": 300, "max_cpu": 200, "max_memory": 512, "max_queue": 30}
}

# 1. Define the severity classification lookups
SEVERITY_MAPPING = {
    "Database Failure / Timeout": "Critical",
    "Queue Overflow": "High",
    "High Memory": "High",
    "High CPU Usage": "Medium",
    "High Latency": "Low",
}

ERROR_CODE_MAPPING = {
    "Database Failure / Timeout": "ERR-501",
    "Queue Overflow": "ERR-401",
    "High Memory": "ERR-301",
    "High CPU Usage": "ERR-201",
    "High Latency": "ERR-101",
    "Success": "ERR-000",  # Default clean code for successful metrics
}

