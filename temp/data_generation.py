from pathlib import Path
import os
from dotenv import load_dotenv

# 1. Load the environment configuration file
load_dotenv()
input_path_csv = Path(os.getenv("INPUT_DATA_LOG_PATH_CSV"))
input_path_json = Path(os.getenv("INPUT_DATA_LOG_PATH_JSON"))
print("File path loaded successfully")


import random, json, pandas as pd
from datetime import datetime, timedelta

# --- CONFIG ---
TOTAL_RECORDS = 20000   # adjust to 30000–50000 as needed
CRITICAL_LIMIT = int(TOTAL_RECORDS * 0.05)

REGIONS = ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]
HEALTHY_REGIONS = ["us-east-1", "ap-southeast-1"]
UNSTABLE_REGIONS = ["us-west-2", "eu-west-1"]

SERVICE_ENDPOINTS = {
    "portfolio-service": ["/portfolio","/trade","/performance"],
    "trading-engine": ["/trade","/transfer","/payment"],
    "auth-service": ["/login","/logout","/kyc"],
    "notification-service": ["/login","/payment","/transfer"],
    "payment-api": ["/payment","/transfer","/withdrawal","/deposit"],
    "investment-engine": ["/portfolio","/trade","/withdrawal","/recommendation"],
    "fraud-detection": ["/kyc","/transfer","/payment"],
    "ledger-service": ["/balance_check"]
}

ERROR_MAP = {
    "ERR-101":"Database Timeout","ERR-102":"Database Connection Failure","ERR-103":"Database Authentication Failure",
    "ERR-104":"Database Deadlock Detected","ERR-105":"Database Replication Lag","ERR-106":"Database Storage Full",
    "ERR-107":"Slow Query Detected","ERR-108":"Database CPU High","ERR-109":"Database Memory High",
    "ERR-110":"Database Failover Triggered",
    "ERR-201":"Kafka Broker Down","ERR-202":"Kafka Topic Unavailable","ERR-203":"Kafka Producer Failure",
    "ERR-204":"Kafka Consumer Failure","ERR-205":"Consumer Lag High","ERR-206":"Kafka Partition Offline",
    "ERR-207":"Kafka ISR Shrink","ERR-208":"Kafka Disk Utilization High","ERR-209":"Kafka Throughput Drop",
    "ERR-210":"Kafka Cluster Unstable",
    "ERR-301":"API Endpoint Unavailable","ERR-302":"API Error Rate High","ERR-303":"API Gateway Failure",
    "ERR-304":"API Rate Limit Exceeded","ERR-305":"API Dependency Failure","ERR-306":"API SSL Certificate Expired",
    "ERR-307":"API Request Timeout","ERR-308":"API Payload Validation Failure","ERR-309":"API Traffic Spike",
    "ERR-310":"API Response Degradation",
    "ERR-701":"Authentication Failure","ERR-702":"Authorization Failure","ERR-703":"Token Validation Failure",
    "ERR-704":"Identity Provider Unavailable","ERR-705":"Database Authentication Critical",
    "ERR-901":"Memory Utilization Critical","ERR-902":"CPU Utilization Critical","ERR-903":"Disk Utilization Critical",
    "ERR-904":"Network Latency Critical","ERR-905":"Service Availability Critical"
}

CLIENT_IDS = ["CUST-100483","CUST-109482","CUST-112349","CUST-123456","CUST-134098"]
MACHINE_IDS = ["DEV-MAC-0149A5","DEV-WIN-84725","DEV-MAC-75825","DEV-LIN-11235","DEV-WIN-99325"]

ANOMALY_PROB_RANGES = {
    "Healthy": (0, 5),
    "Normal": (5, 15),
    "Low": (20, 40),
    "Medium": (60, 80),
    "High": (80, 90),
    "Critical": (90, 100)
}
# --- Baseline Standards ---
BASELINE_STANDARDS = {
    ("auth-service","/login"): {"max_latency":50,"max_cpu":20,"max_memory":50,"max_queue":5},
    ("auth-service","/logout"): {"max_latency":50,"max_cpu":20,"max_memory":50,"max_queue":5},
    ("auth-service","/kyc"): {"max_latency":80,"max_cpu":30,"max_memory":70,"max_queue":5},
    ("payment-api", "/transfer"): {"max_latency": 160, "max_cpu": 80, "max_memory": 60, "max_queue": 15},
    ("payment-api", "/withdrawal"): {"max_latency": 160, "max_cpu": 80, "max_memory": 60, "max_queue": 15},
    ("trading-engine", "/trade"): {"max_latency": 150, "max_cpu": 80, "max_memory": 60, "max_queue": 2},
    ("fraud-detection", "/payment"): {"max_latency": 150, "max_cpu": 90, "max_memory": 100, "max_queue": 10},
    ("ledger-service", "/balance_check"): {"max_latency": 30, "max_cpu": 20, "max_memory": 50, "max_queue": 5},
    ("investment-engine", "/portfolio"): {"max_latency": 200, "max_cpu": 90, "max_memory": 90, "max_queue": 30}
    # ... (keep rest of your baseline standards unchanged)
}

# --- Outage Windows ---
start_time = datetime.now()
OUTAGE_WINDOWS = [
    (start_time + timedelta(minutes=2), start_time + timedelta(minutes=10)),
    (start_time + timedelta(minutes=20), start_time + timedelta(minutes=28)),
    (start_time + timedelta(minutes=40), start_time + timedelta(minutes=50))
]

# --- Target distribution percentages ---
TARGET_DISTRIBUTION = {
    "Critical": 0.05,   # 5%
    "High":     0.10,   # 10%
    "Medium":   0.20,   # 20%
    "Low":      0.40,   # 40%
    "Normal":   0.15,   # 15%
    "Healthy":  0.10    # 10%
}

severity_counts = {sev: 0 for sev in TARGET_DISTRIBUTION.keys()}
'''
def choose_severity():
    total_generated = sum(severity_counts.values())
    if total_generated == 0:
        return "Healthy"
    current_pct = {sev: severity_counts[sev]/total_generated for sev in TARGET_DISTRIBUTION.keys()}
    under_target = [sev for sev in TARGET_DISTRIBUTION if current_pct[sev] < TARGET_DISTRIBUTION[sev]]
    if under_target:
        chosen = random.choice(under_target)
    else:
        chosen = random.choices(list(TARGET_DISTRIBUTION.keys()), weights=list(TARGET_DISTRIBUTION.values()))[0]
    severity_counts[chosen] += 1
    return chosen
'''
def choose_severity():
    return random.choices(
        list(TARGET_DISTRIBUTION.keys()),
        weights=list(TARGET_DISTRIBUTION.values())
    )[0]

def in_outage_window(ts):
    ts_dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
    return any(start <= ts_dt <= end for start,end in OUTAGE_WINDOWS)

def pick_client_machine():
    return random.choice(CLIENT_IDS), random.choice(MACHINE_IDS)

'''
def evaluate_threshold(service, endpoint, metric, value):
    limits = BASELINE_STANDARDS.get((service, endpoint))
    if not limits: return "Healthy"
    max_val = limits[f"max_{metric}"]
    if value > max_val:
        return "Critical" if value > max_val*1.2 else "High"
    else:
        if value >= max_val*0.9: return "Low"
        elif value >= max_val*0.8: return "Normal"
        else: return "Healthy"
'''
def evaluate_threshold(service, endpoint, metric, value):
    limits = BASELINE_STANDARDS.get((service, endpoint))
    if not limits:
        return "Healthy"
    max_val = limits[f"max_{metric}"]

    # Special rule for auth-service: cap severity at Medium
    if service == "auth-service":
        if value > max_val:
            return "Medium"   # never High/Critical
        elif value >= max_val * 0.9:
            return "Low"
        elif value >= max_val * 0.8:
            return "Normal"
        else:
            return "Healthy"

    # Default logic for other services
    if value > max_val:
        return "Critical" if value > max_val * 1.2 else "High"
    elif value >= max_val * 0.9:
        return "Low"
    elif value >= max_val * 0.8:
        return "Normal"
    else:
        return "Healthy"

def assign_amount(service):
    if service in ["payment-api", "trading-engine"]:
        return round(random.uniform(100.0, 10000.0), 2)
    elif service in ["portfolio-service", "investment-engine"]:
        return round(random.uniform(5000.0, 15000.0), 2)
    else:
        return 0.0

def assign_status(severity):
    return "Failure" if severity in ["Critical","High","Medium","Low"] else "Success"

def assign_error(severity, service, endpoint, latency, cpu, memory, queue):
    # Success cases should never have error codes
    if severity in ["Healthy", "Normal"]:
        return "ERR-000"

    limits = BASELINE_STANDARDS.get((service, endpoint))
    if limits:
        # Clamp values so they never exceed 100
        memory = min(memory, 100)
        cpu = min(cpu, 100)

        # Metric-driven errors
        if memory > limits["max_memory"] * 1.2:
            return "ERR-901"
        if cpu > limits["max_cpu"] * 1.2:
            return "ERR-902"
        if memory > limits["max_memory"] and cpu > limits["max_cpu"]:
            return "ERR-903"
        if latency > limits["max_latency"] * 1.2:
            return "ERR-904"

    # For High/Medium/Critical, always assign some error code
    return random.choice(list(ERROR_MAP.keys()))

def anomaly_probability(severity):
    low, high = ANOMALY_PROB_RANGES[severity]
    return random.randint(low, high)

def assign_error_count():
    return random.randint(1,20)
"""
def generate_metrics(service, endpoint):
    limits = BASELINE_STANDARDS.get((service, endpoint))
    if not limits:
        return (random.randint(5, 400), random.randint(10, 250),
                random.randint(50, 800), random.randint(1, 50))
    latency = random.randint(1, int(limits["max_latency"] * 1.5))
    cpu     = random.randint(1, int(limits["max_cpu"] * 1.5))
    memory  = random.randint(1, int(limits["max_memory"] * 1.5))
    queue   = random.randint(1, int(limits["max_queue"] * 2))
    return latency, cpu, memory, queue
"""
def regenerate_metrics_for_severity(service, endpoint, severity):
    limits = BASELINE_STANDARDS.get((service, endpoint))
    if not limits:
        return (random.randint(5, 400), random.randint(10, 250),
                random.randint(50, 800), random.randint(1, 50))

    if severity == "Healthy":
        latency = random.randint(1, int(limits["max_latency"]*0.7))
        cpu     = random.randint(1, int(limits["max_cpu"]*0.7))
        memory  = random.randint(1, int(limits["max_memory"]*0.7))
        queue   = random.randint(1, int(limits["max_queue"]*0.7))

    elif severity == "Normal":
        latency = random.randint(int(limits["max_latency"]*0.8), limits["max_latency"])
        cpu     = random.randint(int(limits["max_cpu"]*0.8), limits["max_cpu"])
        memory  = random.randint(int(limits["max_memory"]*0.8), limits["max_memory"])
        queue   = random.randint(int(limits["max_queue"]*0.8), limits["max_queue"])

    elif severity == "Low":
        latency = random.randint(int(limits["max_latency"]*0.9), int(limits["max_latency"]*1.0))
        cpu     = random.randint(int(limits["max_cpu"]*0.9), int(limits["max_cpu"]*1.0))
        memory  = random.randint(int(limits["max_memory"]*0.9), int(limits["max_memory"]*1.0))
        queue   = random.randint(int(limits["max_queue"]*0.9), int(limits["max_queue"]*1.0))

    elif severity == "Medium":
        if service == "auth-service":
            # tighter range so values stay close to limits, not spilling into High
            latency = random.randint(limits["max_latency"], int(limits["max_latency"]*1.05))
            cpu     = random.randint(limits["max_cpu"], int(limits["max_cpu"]*1.05))
            memory  = random.randint(limits["max_memory"], int(limits["max_memory"]*1.05))
            queue   = random.randint(limits["max_queue"], int(limits["max_queue"]*1.05))
        else:
            latency = random.randint(int(limits["max_latency"]*1.0), int(limits["max_latency"]*1.2))
            cpu     = random.randint(int(limits["max_cpu"]*1.0), int(limits["max_cpu"]*1.2))
            memory  = random.randint(int(limits["max_memory"]*1.0), int(limits["max_memory"]*1.2))
            queue   = random.randint(int(limits["max_queue"]*1.0), int(limits["max_queue"]*1.2))
    elif severity == "High":
        latency = random.randint(int(limits["max_latency"]*1.2), int(limits["max_latency"]*1.4))
        cpu     = random.randint(int(limits["max_cpu"]*1.2), int(limits["max_cpu"]*1.4))
        memory  = random.randint(int(limits["max_memory"]*1.2), int(limits["max_memory"]*1.4))
        queue   = random.randint(int(limits["max_queue"]*1.2), int(limits["max_queue"]*1.4))

    elif severity == "Critical":
        latency = random.randint(int(limits["max_latency"]*1.4), int(limits["max_latency"]*1.8))
        cpu     = random.randint(int(limits["max_cpu"]*1.4), int(limits["max_cpu"]*1.8))
        memory  = random.randint(int(limits["max_memory"]*1.4), int(limits["max_memory"]*1.8))
        queue   = random.randint(int(limits["max_queue"]*1.4), int(limits["max_queue"]*1.8))

    # Clamp CPU and memory before returning
    cpu = min(cpu, 100)
    memory = min(memory, 100)
    return latency, cpu, memory, queue


# --- Main Generation ---
# --- Main Generation ---
records = []
critical_count = 0
severity_distribution = {sev:0 for sev in TARGET_DISTRIBUTION.keys()}
region_errors = {r:0 for r in REGIONS}
service_errors = {s:0 for s in SERVICE_ENDPOINTS.keys()}
start_time = datetime.now()

# Track service × severity counts
service_severity_counts = {s: {sev:0 for sev in severity_distribution.keys()} 
                           for s in SERVICE_ENDPOINTS.keys()}

for i in range(TOTAL_RECORDS):
    severity_counts = {sev: 0 for sev in TARGET_DISTRIBUTION.keys()}
    ts = (start_time + timedelta(seconds=i//5)*10).strftime("%Y-%m-%d %H:%M:%S")
    client_id, machine_id = pick_client_machine()
    region = random.choice(REGIONS)

    if i % 5 == 0:
        batch_services = random.sample(list(SERVICE_ENDPOINTS.keys()), k=5)
    service = batch_services[i % 5]
    endpoint = random.choice(SERVICE_ENDPOINTS[service])

    # Step 1: Decide severity (distribution controlled)
    severity = choose_severity()

    # Step 2: Apply bias
    if service in ["auth-service","ledger-service"] and severity in ["Critical","High"]:
        severity = random.choice(["Normal","Healthy","Low","Medium"])
    if region in HEALTHY_REGIONS and severity in ["Critical","High"]:
        severity = random.choice(["Normal","Healthy","Low","Medium"])


    # Step 3: Generate metrics based on severity band
    latency, cpu, memory, queue = regenerate_metrics_for_severity(service, endpoint, severity)
    # sanity check: if metrics fall outside severity band, adjust severity
    sev_latency = evaluate_threshold(service, endpoint, "latency", latency)
    sev_cpu     = evaluate_threshold(service, endpoint, "cpu", cpu)
    sev_mem     = evaluate_threshold(service, endpoint, "memory", memory)
    sev_queue   = evaluate_threshold(service, endpoint, "queue", queue)

    # pick the max severity from metrics vs chosen severity
    severity = max([severity, sev_latency, sev_cpu, sev_mem, sev_queue],
               key=lambda s: ["Healthy","Normal","Low","Medium","High","Critical"].index(s))

    # Step 4: Update counts
    service_severity_counts[service][severity] += 1
    if severity == "Critical":
        critical_count += 1
    severity_distribution[severity] += 1

    # Step 5: Assign other fields
    status = assign_status(severity)
    error_code = assign_error(severity, service, endpoint, latency, cpu, memory, queue)
    anomaly_prob = anomaly_probability(severity)
    is_anomaly = 1 if status == "Failure" else 0

    if status == "Failure":
        region_errors[region] += 1
        service_errors[service] += 1

    row = {
        "timestamp": datetime.fromisoformat(ts).isoformat(),
         "service": service,
        "endpoint": endpoint,
        "region": region,
        "latency_ms": f"{latency}ms",
        "cpu_usage": f"{cpu}m",
        "memory_usage": f"{memory}MiB",
        "queue_lag": f"{queue}ms",
        "amount": assign_amount(service),
        "error_code": error_code if error_code is not None else "ERR-000",
        "severity": severity,
        "status": status,
        "error_count": assign_error_count(),
        "anomaly_probability_%": anomaly_prob,
        "is_anomaly": is_anomaly,
        "client_id": client_id,
        "machine_id": machine_id
    }
    records.append(row)

# --- Save Outputs ---
df = pd.DataFrame(records)
df.to_csv(input_path_csv, index=False)

with open(input_path_json,"w") as f:
    json.dump(records, f, indent=2)

# --- Summary ---
print(f"Generated {len(records)} records")
print(f"Critical records: {critical_count}")
print("Severity distribution:")
for sev, count in severity_distribution.items():
    pct = (count/len(records))*100
    print(f"  {sev}: {count} ({pct:.2f}%)")

# Target distribution table
print("\nTarget distribution (expected %):")
for sev, pct in TARGET_DISTRIBUTION.items():
    print(f"  {sev}: {pct*100:.1f}%")

print("\nHealthy regions:")
for r in HEALTHY_REGIONS:
    print(f"  {r}: {region_errors[r]} failures")

print("\nRegion-wise error counts:")
for r, count in region_errors.items():
    print(f"  {r}: {count} failures")

print("\nService-wise error counts:")
for s, count in service_errors.items():
    print(f"  {s}: {count}")

print("\nService × Severity counts:")
for service, sev_counts in service_severity_counts.items():
    print(f"\n{service}:")
    for sev, count in sev_counts.items():
        print(f"  {sev}: {count}")

print("\nGap analysis (actual % vs target %):")
for sev, target_pct in TARGET_DISTRIBUTION.items():
    actual_pct = (severity_distribution[sev]/len(records))*100
    diff = actual_pct - (target_pct*100)
    print(f"  {sev}: actual {actual_pct:.2f}% vs target {target_pct*100:.1f}% (diff {diff:+.2f}%)")

print(f"\nCSV saved to {input_path_csv}")
print(f"JSON saved to {input_path_json}")

"""
# --- Save Outputs ---
df = pd.DataFrame(records)
df.to_csv(input_path_csv, index=False)

with open(input_path_json,"w") as f:
    json.dump(records, f, indent=2)

# --- Summary ---

print(f"Generated {len(records)} records")
print(f"Critical records: {critical_count}")
print("Severity distribution:")
for sev, count in severity_distribution.items():
    print(f"  {sev}: {count}")

print("\nHealthy regions:")
for r in HEALTHY_REGIONS:
    print(f"  {r}: {region_errors[r]} failures")

print("\nRegion-wise error counts:")
for r, count in region_errors.items():
    print(f"  {r}: {count} failures")

print("\nService-wise error counts:")
for s, count in service_errors.items():
    print(f"  {s}: {count}")

print("\nService × Severity counts:")
for service, sev_counts in service_severity_counts.items():
    print(f"\n{service}:")
    for sev, count in sev_counts.items():
        print(f"  {sev}: {count}")

print("\nCSV saved to synthetic_data.csv")
print("JSON saved to synthetic_data.json")
"""