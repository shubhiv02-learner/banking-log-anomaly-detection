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