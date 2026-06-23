import os
import sys
import random
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import numpy as np
import pandas as pd
import json

# 1. Dynamically calculate the path to the root folder
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))
from config import(BASELINE_STANDARDS, ERROR_CODE_MAPPING)

load_dotenv()
input_path_csv = Path(os.getenv("INPUT_DATA_LOG_PATH_CSV"))
output_path_json = Path(os.getenv("OUTPUT_DATA_LOG_PATH_JSON"))
output_path_csv = Path(os.getenv("OUTPUT_DATA_LOG_PATH_CSV"))

df = pd.read_csv(input_path_csv)
print("File loaded successfully")

# Convert baseline dictionary into a lookup table
standards_df = pd.DataFrame.from_dict(BASELINE_STANDARDS, orient="index")
standards_df.index.names = ["service", "endpoint"]
standards_df = standards_df.reset_index()

# Merge with thresholds
merged_df = pd.merge(df, standards_df, on=["service", "endpoint"], how="inner")
#merged_df = df

# Convert string metrics to integers
merged_df["latency_ms"] = merged_df["latency_ms"].astype(str).str.replace("ms","",regex=False).astype(int)
merged_df["cpu_usage"] = merged_df["cpu_usage"].astype(str).str.replace("m","",regex=False).astype(int)
merged_df["memory_usage"] = merged_df["memory_usage"].astype(str).str.replace("MiB","",regex=False).astype(int)
merged_df["queue_lag"] = merged_df["queue_lag"].astype(str).str.replace("ms","",regex=False).astype(int)
'''
# Threshold checks (optional analytical layer)
cond_latency = merged_df["latency_ms"] > merged_df["max_latency"]
cond_cpu = merged_df["cpu_usage"] > merged_df["max_cpu"]
cond_memory = merged_df["memory_usage"] > merged_df["max_memory"]
cond_queue = merged_df["queue_lag"] > merged_df["max_queue"]
cond_dbfailure = cond_latency & cond_queue

conditions = [cond_dbfailure, cond_latency, cond_cpu, cond_memory, cond_queue]
choices = ["Database Failure / Timeout","High Latency","High CPU Usage","High Memory","Queue Overflow"]
merged_df["breached_rule"] = np.select(conditions, choices, default="Success")

# Keep anomaly flag/status as generated
merged_df["is_anomaly"] = (merged_df["status"] == "Failed").astype(int)
'''
# Severity scoring (optional analytical layer)
has_limits = merged_df[["max_latency","max_cpu","max_memory","max_queue"]].notna().all(axis=1)

merged_df.loc[has_limits, "resource_stress_score"] = (
    merged_df.loc[has_limits, "latency_ms"] / merged_df.loc[has_limits, "max_latency"] +
    merged_df.loc[has_limits, "cpu_usage"] / merged_df.loc[has_limits, "max_cpu"] +
    merged_df.loc[has_limits, "memory_usage"] / merged_df.loc[has_limits, "max_memory"] +
    merged_df.loc[has_limits, "queue_lag"] / merged_df.loc[has_limits, "max_queue"]
).round(4)

merged_df.loc[~has_limits, "resource_stress_score"] = np.nan
# Map error codes based on breached rule (optional)
#merged_df["error_code"] = merged_df["breached_rule"].map(ERROR_CODE_MAPPING).fillna(merged_df["error_code"])

# Output
output_cols = [
    "timestamp","service","endpoint","region",
    "latency_ms","cpu_usage","memory_usage","queue_lag",
    "amount","error_code","severity","status",
    "error_count","anomaly_probability_%", "is_anomaly","client_id","machine_id", "resource_stress_score"
]

final_processed_df = merged_df[output_cols]
final_processed_df.to_csv(output_path_csv, index=False)

with open(output_path_json,"w") as f:
    json.dump(final_processed_df.to_dict(orient="records"), f, indent=2)

print(f"Master file saved to: {output_path_json}")
input("enter to continue .. ")
