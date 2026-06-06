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
import pandas as pd
from datetime import datetime, timedelta, timezone
from collections import defaultdict

from src.stream_metrics import StreamMetrics
from src.feature_engineering import create_window_features
from src.detector import EnsembleDetector

# Initialize components
metrics_engine = StreamMetrics()
detector = EnsembleDetector()
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

while True:
    try:
        current_time = datetime.now(timezone.utc)
        window_start = current_time 
        window_end = window_start + timedelta(minutes=1)
        print(f"Current time: {current_time}, Window end time: {window_end}")
        while current_time < window_end:
        
            current_time = datetime.now(timezone.utc)
            # Process messages - buffer for 5 minutes
        
            print("⏳ Buffering data for 5-minute window...")
            input(f"Press Enter to fetch the next message.in process window.{current_time}, Window end time: {window_end}")
            
            for message in consumer:
                try:
                    current_time = datetime.now(timezone.utc)
                    if message is None:
                        print("No message received, waiting...")
                        continue
                    record = message.value
                    record["timestamp"] = (pd.to_datetime(record["timestamp"]))
                    #print(f"Received record for service: {record['service']} at {record['timestamp']}")
                    #print(f"Current time: {current_time}, Window end time: {window_end}")
                    #input("Press Enter to fetch the next message..in try of processing .")
                  
                    metrics_engine.update(record)
                    service = record["service"]
                    service_buffers[record["service"]].append(record)
                
                    # Calculate EWMA/CUSUM/Persistence/IP  
                    if current_time > window_end:
                        print("⏰ 5-minute window complete, processing data...")
                        print(f"service_buffers: { {k: len(v) for k, v in service_buffers.items()} } ") # Debug: print number of records per service
                        #input("Press Enter to start processing data for window...")
                        
                        #window_start = current_time
                        #window_end = window_start + timedelta(minutes=1)
                        break
                except Exception as e:
                    print(f"Error processing message: {e}, continue with next message")
                    continue
            #Process each service's buffered data
            for service, records in list(service_buffers.items()):
                print(f"Processing service: {service} with {len(records)} records")
                if len(records) == 0:
                    continue
                window_df = create_window_features(records)
                score = detector.score_window(window_df)
                print(f"Anomaly score for {service}: {score}")
                service_buffers.clear()
                #window_start = datetime.now(timezone.utc)
                #window_end = window_start + timedelta(minutes=2)
                print(f"New window started for service {service}. Current time: {current_time}, Window end time: {window_end}")   
                
    except KeyboardInterrupt:
        print("Consumer interrupted by user, shutting down...")
        print("\n🛑 Shutting down streaming pipeline gracefully...")
        consumer.close()
        break
    except Exception as e:
        consumer.close()
        break
      
        #finally:
         #   
          

        