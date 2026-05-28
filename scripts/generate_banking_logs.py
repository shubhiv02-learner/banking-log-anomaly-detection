
# ============================================================
# SentinelIQ V0.2
# Banking Log Generator
# ============================================================

# This script generates realistic structured banking logs
# for anomaly detection and observability experiments.
#
# Simulated Banking Services:
# - payment-api
# - auth-service
# - trading-engine
# - fraud-detection
# - notification-service
#
# Simulated Events:
# - normal requests
# - latency spikes
# - API timeouts
# - database failures
# - queue lag
# - infrastructure saturation
#
# Output:
# data/banking_logs.json
# data/banking_logs.csv
# ============================================================


# =========================
# IMPORT LIBRARIES
# =========================

import pandas as pd
import numpy as np
import random
import json
import os
from datetime import datetime, timedelta
import io # Added this import


# =========================
# CREATE OUTPUT DIRECTORY
# =========================

os.makedirs("outputs", exist_ok=True)


# ============================================================
# CONFIGURATION
# ============================================================

TOTAL_LOGS = 15000

START_TIME = datetime(2026, 1, 1)

SERVICES = [
    "payment-api",
    "auth-service",
    "trading-engine",
    "fraud-detection",
    "notification-service",
    "portfolio-service",
    "investment-engine"
]

ENDPOINTS = [
    "/login",
    "/transfer",
    "/payment",
    "/trade",
    "/portfolio",
    "/kyc",
    "/withdrawal"
]

# Map services to their specific endpoints
SERVICE_ENDPOINTS_MAP = {
    "payment-api": ["/payment", "/transfer", "/withdrawal"],
    "auth-service": ["/login", "/kyc"],
    "trading-engine": ["/trade", "/payment", "/transfer"],
    "fraud-detection": ["/kyc", "/payment", "/transfer"],
    "notification-service": ["/login", "/transfer", "/payment"],
    "portfolio-service": ["/portfolio", "/trade"],
    "investment-engine": ["/trade", "/portfolio", "/withdrawal"]
}

# Map services to their base latencies
SERVICE_LATENCY_MAP = {
    "payment-api": 150,
    "auth-service": 80,
    "trading-engine": 100,
    "fraud-detection": 200,
    "notification-service": 70,
    "portfolio-service": 120,
    "investment-engine": 130
}

REGIONS = [
    "India",
    "Singapore",
    "USA",
    "Germany",
    "UAE"
]

STATUS_TYPES = [
    "success",
    "timeout",
    "db_failure",
    "high_latency",
    "queue_delay"
]

# ANOMALY CONFIGURATION: Inject anomalies in three specific windows
ANOMALY_WINDOWS = [
    (int(TOTAL_LOGS * 0.1), int(TOTAL_LOGS * 0.12)), # 10-12% of logs
    (int(TOTAL_LOGS * 0.4), int(TOTAL_LOGS * 0.42)), # 40-42% of logs
    (int(TOTAL_LOGS * 0.7), int(TOTAL_LOGS * 0.72))  # 70-72% of logs
]
ANOMALY_PROB_IN_WINDOW = 0.8  # High probability of anomaly within a window
ANOMALY_PROB_OUT_WINDOW = 0.001 # Low probability of anomaly outside a window

# Define anomaly types and their weights to achieve the desired distribution
anomaly_types_for_selection = ["timeout", "db_failure", "high_latency", "queue_delay"]
anomaly_weights_for_selection = [0.03, 0.01, 0.4, 0.56] # 4% critical, 96% medium

# ============================================================
# GENERATE SINGLE LOG EVENT
# ============================================================

def generate_log_event(index):

    """
    Generates one structured banking log event.

    Simulates:
    - infrastructure metrics
    - service health
    - latency behavior
    - operational failures
    """

    # --------------------------------------------------------
    # Generate timestamp
    # --------------------------------------------------------

    timestamp = START_TIME + timedelta(
        seconds=index * 30
    )

    # --------------------------------------------------------
    # Randomly select banking service and its associated endpoint
    # --------------------------------------------------------

    service = random.choice(SERVICES)
    possible_endpoints = SERVICE_ENDPOINTS_MAP.get(service, ENDPOINTS) # Default to all endpoints if service not in map
    endpoint = random.choice(possible_endpoints)

    region = random.choice(REGIONS)

    # --------------------------------------------------------
    # Generate normal operational metrics with service-specific latency
    # --------------------------------------------------------

    base_latency = SERVICE_LATENCY_MAP.get(service, 120) # Default to 120 if service not in map
    latency_ms = int(
        np.random.normal(base_latency, 20) # Randomize around the base_latency
    )
    cpu_usage = round(np.random.normal(55, 8),2)
    memory_usage = round(np.random.normal(60, 10),2)
    queue_lag = max(0,int(np.random.normal(5, 2)))
    error_code = None
    status = "success"
    severity = "low"
    error_count = 0 # Initialize error_count
    is_anomaly = 0 # Initialize is_anomaly
    # --------------------------------------------------------
    # Inject anomalies probabilistically based on defined windows
    # --------------------------------------------------------

    in_anomaly_window = False
    for start, end in ANOMALY_WINDOWS:
        if start <= index <= end:
            in_anomaly_window = True
            break

    anomaly_roll = random.random()

    # Determine anomaly probability based on whether the current index is in an anomaly window
    current_anomaly_probability = ANOMALY_PROB_IN_WINDOW if in_anomaly_window else ANOMALY_PROB_OUT_WINDOW

    if anomaly_roll < current_anomaly_probability:
        is_anomaly = 1
        # Select anomaly type based on defined weights
        anomaly_type = random.choices(anomaly_types_for_selection, weights=anomaly_weights_for_selection, k=1)[0]

        # =========================================
        # TIMEOUT EVENT
        # =========================================

        if anomaly_type == "timeout":
            
            latency_ms =max(base_latency+10,int(np.random.normal(base_latency, 100))) # Randomize around the base_latency
            cpu_usage += random.randint(10, 30)
            queue_lag += random.randint(10, 40)
            error_code = "TIMEOUT_ERROR"
            status = "timeout"
            severity = "critical"
            error_count = random.randint(5, 10) # Assign a numerical error count

        # =========================================
        # DATABASE FAILURE
        # =========================================

        elif anomaly_type == "db_failure":

            latency_ms =max(base_latency+10,int(np.random.normal(base_latency, 80))) # Randomize around the base_latency
            cpu_usage += random.randint(5, 20)
            memory_usage += random.randint(10, 20)
            error_code = "DB_CONNECTION_FAILURE"
            status = "db_failure"
            severity = "critical"
            error_count = random.randint(5, 10) # Assign a numerical error count
            
        # =========================================
        # HIGH LATENCY EVENT
        # =========================================

        elif anomaly_type == "high_latency":
            latency_ms =max(base_latency+30,int(np.random.normal(base_latency, 80))) # Randomize around the base_latency
            queue_lag += random.randint(5, 15)
            error_code = "LATENCY_SPIKE"
            status = "high_latency"
            severity = "medium"
            error_count = random.randint(2, 5) # Assign a numerical error count
            
        # =========================================
        # QUEUE DELAY EVENT
        # =========================================

        elif anomaly_type == "queue_delay":

            latency_ms =max(base_latency+20,int(np.random.normal(base_latency, 50))) # Randomize around the base_latenc
            queue_lag += random.randint(20, 60)
            error_code = "QUEUE_BACKPRESSURE"
            status = "queue_delay"
            severity = "medium"
            error_count = random.randint(2, 5) # Assign a numerical error count
            
    # --------------------------------------------------------
    # Create structured log event
    # --------------------------------------------------------
    latency_ms = abs(latency_ms)

    log_event = {

        "timestamp": timestamp.isoformat(),
        "service": service,
        "endpoint": endpoint,
        "region": region,
        "latency_ms": latency_ms,
        "cpu_usage": round(cpu_usage, 2),
        "memory_usage": round(memory_usage, 2),
        "queue_lag": queue_lag,
        "status": status,
        "error_code": error_code,
        "severity": severity,
        "error_count": error_count, # Add error_count to the log event
         "is_anomaly": is_anomaly # Add is_anamoly to the log event
    }

    return log_event


# ============================================================
# GENERATE COMPLETE DATASET
# ============================================================

def generate_banking_logs(total_logs):

    """
    Generates complete banking observability dataset.
    """

    logs = []

    for i in range(total_logs):

        log = generate_log_event(i)

        logs.append(log)

    return logs


# ============================================================
# SAVE LOGS
# ============================================================

def save_logs(logs):

    """
    Saves logs in:
    - JSON format
    - CSV format
    """

    # --------------------------------------------------------
    # Save JSON logs
    # --------------------------------------------------------

    with open(
        "data/banking_logs.json",
        "w"
    ) as f:

        json.dump(
            logs,
            f,
            indent=4
        )

    # --------------------------------------------------------
    # Save CSV logs
    # --------------------------------------------------------

    df = pd.DataFrame(logs)

    df.to_csv(
        "data/banking_logs.csv",
        index=False
    )

    # Capture the statistics output string
    stats_string = display_statistics(df)

    # Define the output file path
    output_file_path = 'outputs/logsStatistics.txt'

    # Ensure the 'outputs' directory exists
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    # Write the captured output to the file
    with open(output_file_path, 'w') as f:
        f.write(stats_string)

    print(f"Log statistics saved to '{output_file_path}'") # Print confirmation here

    return df


# ============================================================
# DISPLAY SAMPLE STATISTICS
# ============================================================

def display_statistics(df):

    """
    Displays dataset overview and anomaly distribution.
    Returns the statistics as a string.
    """
    output_string = io.StringIO()

    output_string.write("\n================================================")
    output_string.write("\n SENTINELIQ LOG GENERATION COMPLETED ")
    output_string.write("\n================================================\n")
    output_string.write(f"\nTotal Logs Generated : {len(df)}\n")
    output_string.write("\nServices Monitored:")
    output_string.write(df['service'].value_counts().to_string())
    output_string.write("\n\nStatus Distribution:")
    output_string.write(df['status'].value_counts().to_string())
    output_string.write("\n\nSeverity Distribution:")
    output_string.write(df['severity'].value_counts().to_string())
    output_string.write("\n\nSample Logs:")
    output_string.write(df.head().to_string())

    # Print to stdout as well for immediate display
    print(output_string.getvalue())
    print("printed sample logs")
    return output_string.getvalue()


# ============================================================
# MAIN DATA GENERATION EXECUTION PIPELINE
# ============================================================

def main():

    print("\nGenerating banking observability logs...\n")

    logs = generate_banking_logs(TOTAL_LOGS)

    df = save_logs(logs)


    print("\nFiles Saved:\n")
    print(f"Banking logs in json saved to outputs/banking_logs.json ")
    print(f"Banking logs in csv format saved to outputs/banking_logs.csv ")
    print(f"Log statistics saved to outputs/logsStatistics.txt")
    print("\nLog generation completed successfully.\n")
    return df
