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
import json
from numpy import rint
import pandas as pd
from datetime import datetime, timedelta, timezone
from collections import defaultdict

from src.stream_metrics import StreamMetrics
from src.feature_engineering import create_window_features
from src.detector import EnsembleDetector
from src.ensemble import EnsembleEngine
from config import WINDOW_SIZE_MINUTES

from backend.db_services import (
    save_window_metric,
    save_alert
)
# Initialize components
metrics_engine = StreamMetrics()
detector = EnsembleDetector()
ensemble = EnsembleEngine()
service_buffers = defaultdict(list)


# Set up Kafka consumer
consumer = KafkaConsumer(
    "banking_logs",
    bootstrap_servers=["localhost:9092"],
    value_deserializer=lambda m: json.loads(
        m.decode("utf-8")
    ),
    auto_offset_reset="latest",
    group_id="sentineliq-v1"
)
print("🚀 Consumer started, waiting for messages...")
current_time = datetime.now(timezone.utc)
window_start = current_time 
window_end = window_start + timedelta(minutes=WINDOW_SIZE_MINUTES)

try:
    for message in consumer:
        try:
            current_time = datetime.now(timezone.utc)
            if message is None:
                    print("No message received, waiting...")
                    continue
            record = message.value
            record["timestamp"] = (pd.to_datetime(record["timestamp"]))
            record = metrics_engine.update(record)
            service = record["service"]
            service_buffers[record["service"]].append(record)
            
            # Calculate EWMA/CUSUM/Persistence/IP  
            if current_time > window_end:
                print("⏰ 5-minute window complete, processing data...")
                print(f"service_buffers: { {k: len(v) for k, v in service_buffers.items()} } ") # Debug: print number of records per service
                print(f"Processing window {window_start} -> {window_end}")
                #Process each service's buffered data
                for service, records in list(service_buffers.items()):
                    if len(records) == 0:
                        continue
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
                    #print(f"Ensemble input: if_score: {ensemble_input['if_score']} ocsvm_score: {ensemble_input['ocsvm_score']}") # Debug: print ensemble input
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
                        save_alert(alert_data)
                
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
        
      
    
         
          

        