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
#save to PostgreSQL
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
                    print(f"Ensemble input: if_score: {ensemble_input['if_score']} ocsvm_score: {ensemble_input['ocsvm_score']}") # Debug: print ensemble input
                    ensemble_result = ensemble.predict(ensemble_input) #Final ensemble score + priority
                    if ensemble_result["prediction"]:
                        print(
                                f"ALERT: {service} "
                                f"{ensemble_result['priority']} "
                                f"score={ensemble_result['final_score']}"
                            )
                
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
        
      
    
         
          

        