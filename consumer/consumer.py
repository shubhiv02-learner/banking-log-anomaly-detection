#Kafka Message
#      |
#StreamMetrics.update()
#     |
#Buffer
#     |
#5-minute window complete?
#     |
#create_window_features()
#     |
#detector.score_window()
#     |
#ensemble score
#     |
#save to PostgreSQL - window_metrics → increasing every window
#                   alerts → increasing only when anomaly detected
import numpy as np
from kafka import KafkaConsumer
import pandas as pd
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import json

#from confluent_kafka import Consumer, KafkaError, KafkaException - Not working with Controller

from src.stream_metrics import StreamMetrics
from src.feature_engineering import create_window_features
from src.detector import EnsembleDetector
from src.ensemble import EnsembleEngine
from config import WINDOW_SIZE_MINUTES

from backend.db_services import (
    save_window_metric,
    save_alert,
    save_ticket,
    update_window_payload,
)
# Initialize components
metrics_engine = StreamMetrics()
detector = EnsembleDetector()
ensemble = EnsembleEngine()
service_buffers = defaultdict(list)

def save_payload_summary(raw_window_df, window_metric_id):
    raw_window_df = raw_window_df.copy()
    print(f"List of regions : {raw_window_df['region']}")
    payload_summary = {
        "regions": list(raw_window_df["region"].dropna().unique()),
        "top_error_codes": (
            raw_window_df[raw_window_df["error_code"] != "ERR-000"]
            ["error_code"]
            .value_counts()
            .head(5)
            .index
            .tolist()
        ),
        "affected_clients": raw_window_df["client_id"].nunique(),
        "affected_hosts": raw_window_df["machine_id"].nunique(),
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
    update_window_payload(payload_summary, payload_json, window_metric_id)


# Configuration dictionary using standard dot properties
consumer = KafkaConsumer(
    'banking_logs',
    bootstrap_servers=['host.docker.internal:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=False,
    group_id=None # disables group tracking
)

print("🚀 Windows Consumer Connected! Polling for messages...")

current_time = datetime.now(timezone.utc)
window_start = current_time 
window_end = window_start + timedelta(minutes=WINDOW_SIZE_MINUTES)

try:
    for message in consumer:
        try:
            current_time = datetime.now(timezone.utc)
            #print(f"in loop Curr update ent time: {current_time}")
            if message is None:
                    print("No message received, waiting...")
                    continue
            try:
                raw_value = message.value.decode('utf-8')

                #print("got raw value of msg")
                record = json.loads(raw_value)
                #print(f"Message received   {record}")
                record["timestamp"] = (pd.to_datetime(record["timestamp"]))
            except (UnicodeDecodeError, json.JSONDecodeError, TypeError, KeyError) as e:
                    print(f"Error processing message: {e}, continue with next message")
                    continue
            #print("Message converted to datetime")
            record = metrics_engine.update(record)
            #print("Message metrics processed .......")
            service = record["service"]
            service_buffers[record["service"]].append(record)
            #print(f"Message processed .......{current_time}....end: {window_end}")
            # Calculate EWMA/CUSUM/Persistence/IP  
            if current_time > window_end:
                print("⏰ 5-minute window complete, processing data...")
                print(f"service_buffers: { {k: len(v) for k, v in service_buffers.items()} } ") # Debug: print number of records per service
                print(f"Processing window {window_start} -> {window_end}")
                #Process each service's buffered data
                for service, records in list(service_buffers.items()):
                    if len(records) == 0:
                        continue
                    raw_window_df = pd.DataFrame(records).copy()
                    window_df = create_window_features(records)
                    ml_result = detector.score_window(window_df) #ML Scores + raw scores for normalization
                    print(type(window_df.iloc[0]["ewma_mean"]))
                    #input(f"Press Enter to continue...") # Debug: pause before ensemble prediction
                    ensemble_input = {
                            "service": service,
                            "window_start": window_start,
                            "window_end": window_end,
                            "record_count": len(records),
                            "if_score": ml_result["if_score_raw"],
                            "ocsvm_score": ml_result["ocsvm_score_raw"],
                            "ewma": window_df.iloc[0]["ewma_mean"],
                            "cusum": window_df.iloc[0]["cusum_max"],
                            "persistence":window_df.iloc[0]["persistence_score_mean"],
                            "incident_probability":window_df.iloc[0]["incident_probability_mean"]}
                    print(f"Ensemble input: if_score: {ensemble_input['if_score']} ocsvm_score: {ensemble_input['ocsvm_score']}") # Debug: print ensemble input
                    ensemble_result = ensemble.predict(ensemble_input) #Final ensemble score + priority
                    print(f"In consumer Ensemble result: {ensemble_result}")
                    print(f"In consumer window_df.columns before renameing : {window_df.columns}")
                    #Column names to match database table names
                    window_df = window_df.rename(columns={
                        "latency_ms_mean": "latency_mean",
                        "latency_ms_max": "latency_max",
                        "latency_ms_std": "latency_std",

                        "cpu_usage_mean": "cpu_mean",
                        "cpu_usage_max": "cpu_max",

                        "memory_usage_mean": "memory_mean",
                        "ewma_mean": "ewma",
                        "cusum_max": "cusum",
                        
                        "persistence_score_mean": "persistence_score",
                        "incident_probability_mean": "incident_probability",

                         "error_count_sum": "error_count"
                        })
                    print(f"In consumer before enrichment {window_df.columns}")
                    #Enrich it to save additional info in database
                    window_df["service"] = service
                    window_df["ml_score"] = ensemble_result["ml_score"]
                    window_df["statistical_score"] = ensemble_result["statistical_score"]
                    window_df["final_score"] = ensemble_result["final_score"]
                    window_df["prediction"] = np.array(ensemble_result["prediction"]).astype(int)
                    window_df["priority"] = ensemble_result["priority"]                    
                    window_df["window_start"] = window_start
                    window_df["window_end"] = window_end
                    window_df["record_count"] = len(records)
                    window_metric_data = window_df.iloc[0].to_dict()
                    print(f"In consumer window metric data {window_metric_data}")
                    metric = save_window_metric(window_metric_data)
                    print(f"In consumer metric data saved ")
                    if ensemble_result["prediction"]:
                        print(
                                f"ALERT: {service} "
                                f"{ensemble_result['priority']} "
                                f"score={ensemble_result['final_score']}"
                            )
                        alert_data = {
                                    "window_metric_id": metric.id,
                                    "service": service,
                                    "final_score":
                                        ensemble_result["final_score"],
                                    "priority":
                                        ensemble_result["priority"],
                                }
                        save_payload_summary(raw_window_df, metric.id)
                        alert = save_alert(alert_data)
                        print("Alert saved to database")
                        ticket_data = {
                                    "alert_id": alert.id,
                                    "ticket_id":f"INC-{datetime.now().strftime('%Y%m%d')}-{alert.id}",
                                    "service":alert.service,
                                    "priority":alert.priority,
                                    "assignee":"SUPPORT"
                                }
                        print("Ticket data prepared")
                        save_ticket(ticket_data)
                        print("Ticket saved to database")
                service_buffers.clear()
                window_start = datetime.now(timezone.utc)
                window_end = window_start + timedelta(minutes=WINDOW_SIZE_MINUTES)    
        except Exception as e:
                print(f"Error processing message: {e}, continue with next message")
                continue
                
            
except KeyboardInterrupt:
            print("Consumer interrupted by user, shutting down...")
            print("\n🛑 Shutting down streaming pipeline gracefully...")
            consumer.close()
            
except Exception as e:
        consumer.close()
        
      
    
       