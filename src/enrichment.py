import json
import pandas as pd
import json
from collections import OrderedDict

def build_payload_details(raw_window, ERROR_MAPPING):
    try:
        # --- 1. Extract records safely ---
        if isinstance(raw_window, dict):
            if "records" in raw_window:
                records = raw_window["records"]
            elif "data" in raw_window:
                records = raw_window["data"]
            else:
                records = [raw_window]
        elif hasattr(raw_window, "records"):
            records = raw_window.records
        else:
            records = raw_window

        # --- 2. Create DataFrame ---
        raw_window_df = pd.DataFrame(records)
        if "timestamp" in raw_window_df.columns:
            raw_window_df["timestamp"] = pd.to_datetime(
                raw_window_df["timestamp"], format="mixed", dayfirst=True
            )
            raw_window_df["timestamp"] = raw_window_df["timestamp"].dt.strftime('%Y-%m-%d %H:%M:%S')
        raw_window_df = raw_window_df.where(pd.notnull(raw_window_df), "0")

        # --- 3. Build payload_json ---
        payload_json = raw_window_df.to_dict(orient="records")

        # --- 4. Normalize top error codes ---
        raw_errors = (
            raw_window_df["error_code"]
            .value_counts()
            .head(5)
            .index
            .tolist()
        )
        errors = [e if str(e).startswith("ERR") else "ERR-000" for e in raw_errors]
        """
        # --- 5. Enrich top_errors with metadata ---
        error_details = []
        for code in errors:
            info = ERROR_MAPPING.get(code, {
                "error_name": "Unknown Error",
                "root_cause_description": "No details available",
                "recommended_action": "Investigate further",
                "severity_default": "LOW",
                "category": "GENERAL"
            })
            error_details.append({
                "error_code": code,
                "error_name": info["error_name"],
                "category": info["category"],
                "root_cause_description": info["root_cause_description"],
                "recommended_action": info["recommended_action"],
                "severity_default": info["severity_default"]
            })
        """
        # --- 6. Build enriched summary ---
        payload_summary = OrderedDict([
            ("top_errors", errors),
            ("regions", list(raw_window_df["region"].dropna().unique())),
            ("affected_clients", raw_window_df["client_id"].nunique()),
            ("affected_hosts", raw_window_df["machine_id"].nunique()),
            ("top_clients", raw_window_df["client_id"].value_counts().head(5).index.tolist()),
            ("top_hosts", raw_window_df["machine_id"].value_counts().head(5).index.tolist()),
            ("top_endpoints", raw_window_df["endpoint"].value_counts().head(5).index.tolist()),
            ("transaction_value", float(raw_window_df["amount"].sum())),
            ("record_count", len(raw_window_df)),
                  ])

        return payload_summary, payload_json

    except Exception as e:
        print(f"Error {e}")
        input("Error in save payload: ")
        return

def enrich_incident_details(error_codes, ERROR_MAPPING):
    incident_details = []
    for code in error_codes:
        info = ERROR_MAPPING.get(code, {
            "error_name": "Unknown Error",
            "root_cause_description": "No details available",
            "business_impact": "Unknown",
            "customer_impact": "Unknown",
            "recommended_action": "Investigate further",
            "category": "GENERAL"
        })
        incident_details.append({
            "error_code": code,
            "description": info["error_name"],
            "category": info["category"],
            "business_impact": info["business_impact"],
            "customer_impact": info.get("customer_impact", "Unknown"),  # optional field
            "root_cause": info["root_cause_description"],
            "recommended_action": info["recommended_action"]
        })
    return incident_details


def enrich_metrics_details(error_codes, ERROR_MAPPING):
    metrics_details = []
    for code in error_codes:
        info = ERROR_MAPPING.get(code, {
            "error_name": "Unknown Error",
            "category": "GENERAL"
        })
        metrics_details.append({
            "error_code": code,
            "error_name": info["error_name"],
            "category": info["category"]
        })
    return metrics_details

"""
def build_payload_details(raw_window):
    try:
        # --- FIX: Inspect and extract the data safely ---
        # --- 1. EXTRACT THE CLEAN DATA ---
        # Look at the end of your printout: "}]})". 
        # This checks if your data is wrapped inside a dictionary or object.
        #print(f"Raw window: {raw_window}")
        if isinstance(raw_window, dict):
            # If it's a dict holding a list under a key like 'records' or 'data'
            if "records" in raw_window:
                records = raw_window["records"]
                #print("In records")
            elif "data" in raw_window:
                records = raw_window["data"]
                #print("In data")
            else:
                # If it's a flat dictionary (single record), wrap it in a list
                records = [raw_window]
                #print("In single record")
        elif hasattr(raw_window, "records"):
            records = raw_window.records
            #print("In records 2")
        else:
            # If it's already a clean list/tuple of dictionaries
            records = raw_window
            #print("In else clean list")

        # --- 2. CREATE THE DATAFRAME DIRECTLY ---
        # Feeding a list of dicts directly to pd.DataFrame fixes the length mismatch
        raw_window_df = pd.DataFrame(records) 
        print("Dataframe done")
        if "timestamp" in raw_window_df.columns:
            # Convert pandas Timestamp objects to standard ISO string format (YYYY-MM-DD HH:MM:SS)
            raw_window_df["timestamp"] = pd.to_datetime(raw_window_df["timestamp"], format="mixed", dayfirst=True)
            raw_window_df["timestamp"] = raw_window_df["timestamp"].dt.strftime('%Y-%m-%d %H:%M:%S')
        raw_window_df = raw_window_df.where(pd.notnull(raw_window_df), "0")
        # Generate the JSON records from the cleaned DataFrame
        payload_json = raw_window_df.to_dict(orient="records")        
       
        #top_errors = error_details(top_error_codes)
        payload_summary = {
            "regions": list(raw_window_df["region"].dropna().unique()),
            "top_errors":(
                raw_window_df["error_code"]
                .value_counts()
                .head(5)
                .index
                .tolist()
            ),
            "affected_clients": raw_window_df["client_id"].nunique(),
            "top_clients":(
                raw_window_df["client_id"]
                .value_counts()
                .head(5)
                .index
                .tolist()
            ),
            "affected_hosts": raw_window_df["machine_id"].nunique(),
            "top_hosts":(
                raw_window_df["machine_id"]
                .value_counts()
                .head(5)
                .index
                .tolist()
            ),
            "top_endpoints": (
                raw_window_df["endpoint"]
                .value_counts()
                .head(5)
                .index
                .tolist()
            ),
            "transaction_value": float(raw_window_df["amount"].sum()),
            "record_count": len(raw_window_df),
        }
        
        payload_json = raw_window_df.to_dict(orient="records")
        print("Payload jason summary done")
        return payload_summary, payload_json
    except Exception as e:
        print(f"Error {e}")
        input("Error in save payload: ")
        return 
    """
#Not used anymore handled through enrichment itself, columns dropped
#Purpose: What happened? Operational Summary
def build_incident_summary(
    service,
    priority,
    payload_summary
):
    errors = payload_summary.get("top_errors", [])
    regions = payload_summary.get("regions", [])
    endpoints = payload_summary.get("top_endpoints", [])
    clients = payload_summary.get("affected_clients", 0)
    top_clients = payload_summary.get("top_clients", [])

    summary = f"{priority} anomaly detected in {service}. "

    if errors:
        summary += f"Primary error: {errors[0]}. "

    if regions:
        summary += (
            f"Regions impacted: "
            f"{', '.join(regions[:3])}. "
        )

    if endpoints:
        summary += (
            f"Endpoints involved: "
            f"{', '.join(endpoints[:3])}. "
        )

    summary += f"Affected clients: {clients}"

    if top_clients:
        summary += (
            f" (Key clients: "
            f"{', '.join(top_clients[:3])})"
        )

    summary += "."

    return summary


