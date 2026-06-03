##Producer is combined to send alert messages to a separate topic when anomalies are detected. This allows for a streamlined architecture where the consumer not only detects anomalies but also handles the alerting mechanism without needing an additional service. The producer is configured to serialize messages as JSON, making it easy to integrate with various alerting tools that can consume from the 'banking-logs-anomalies' topic.
#Processing a live Kafka stream sequentially means code must be optimized for speed, 
# handle unexpected logging formats gracefully, and maintain zero memory leaks.
# Kafka consumer loop reads incoming JSON logs, processes them with the pipeline we built,
#  and routes the anomalies to a dedicated topic or alert dashboard.
from operator import le
from pyexpat import model
import warnings
import json
from narwhals import col
from sklearn.exceptions import InconsistentVersionWarning
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler, LabelEncoder
from sklearn.metrics import confusion_matrix, classification_report
from kafka import KafkaConsumer, KafkaProducer

# Suppress the version mismatch warning
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

BASE_DIR = Path(__file__).resolve().parent.parent

# 
#robust_scaler = RobustScaler()

# Load the Isolation Forest model
try:
    #Define path to the pre-trained Isolation Forest model
    model_path = BASE_DIR / "models" / "Isolation_forest_RawData.joblib"
    isolation_forest_model = joblib.load(model_path)
    model_path = BASE_DIR / "models" / "robust_scaler.pkl"
    robust_scaler = joblib.load(model_path  )
    model_path = BASE_DIR / "models" / "label_encoder.pkl"
    le = joblib.load(model_path)
    print(f"Successfully loaded Isolation Forest model from {model_path}")
except FileNotFoundError:
    print(f"Error: Model file not found at {model_path}")
    isolation_forest = None



# 1. Initialize your Kafka Consumer and Producer
consumer = KafkaConsumer(
    'banking_logs',               # Your incoming log stream topic
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='latest',       # Process new logs as they arrive
    group_id='anomaly-detector-v1'
)

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Explicit feature mapping matching your training schema
FEATURE_NAMES = ["service", "latency_ms", "cpu_usage", "queue_lag", "error_count"]
NUMERIC_COLS = ["latency_ms", "cpu_usage", "queue_lag", "error_count"]

print("🚀 Anomaly detection service is listening to Kafka stream...")

cnt = 0 #adding temp logic to exit for loop after 5 
        #messages for testing purpose, remove this in production
# 2. Sequential Streaming Loop
for message in consumer:
    try:
        data_json = message.value
        cnt+=1
        # Fast, defensive extraction of fields (handles missing keys gracefully)
        raw_row = [
            data_json.get("service", "unknown"),
            data_json.get("latency_ms", np.nan),
            data_json.get("cpu_usage", np.nan),
            data_json.get("queue_lag", np.nan),
            data_json.get("error_count", np.nan)
        ]
        print(f"Received log for service '{raw_row[0]}': {raw_row[1:]}")
        
        # 3. Create DataFrame directly (faster than raw NumPy array string conversion)
        df_features = pd.DataFrame([raw_row], columns=FEATURE_NAMES)
               
        # 4. Transform string column (Label Encoder)
        # Handle unseen services safely if they appear in production
        try:
            df_features["service"] = le.transform(df_features["service"])
        except ValueError:
            # Fallback for brand new services not present during model training
            df_features["service"] = -1 
        

        # 5. Clean, fill missing data, and Scale
        df_features[NUMERIC_COLS] = df_features[NUMERIC_COLS].apply(pd.to_numeric, errors='coerce')
        df_features[NUMERIC_COLS] = df_features[NUMERIC_COLS].fillna(df_features[NUMERIC_COLS].median())
        print(f"Filled missing values for service '{raw_row[0]}':{df_features[NUMERIC_COLS].iloc[0].tolist()}")
        
        print("SCALER EXPECTS THESE NAMES EXACTLY:", robust_scaler.feature_names_in_)

        scaled_features = robust_scaler.transform(df_features)
        print(f"Processed log for service '{raw_row[0]}': Scaled features ready for inference.")
        # 6. Isolation Forest Inference
        prediction = isolation_forest_model.predict(scaled_features)[0]  # Extract scalar
        anomaly_score = isolation_forest_model.decision_function(scaled_features)[0]
        print(f"Isolation Forest prediction: {prediction} | Anomaly Score: {anomaly_score:.4f}")
        # 7. Route Anomalies (-1 means anomaly, 1 means normal)
        if prediction == -1:
            alert_payload = {
                "status": "ANOMALY",
                "score": float(anomaly_score),
                "original_log": data_json
            }
            # Publish to dedicated anomaly topic for alerting tools (PagerDuty, Slack, etc.)
            producer.send('banking-logs-anomalies', value=alert_payload)
            print(f"⚠️ Anomaly flag raised for service '{raw_row[0]}' | Score: {anomaly_score:.4f}")
            if cnt>=20 :#temp logic to exit for loop after 5 messages for testing purpose, remove this in production
                print("Exiting after processing 5 messages for testing purposes.")
                raise KeyboardInterrupt        
    except Exception as e:
        # Prevent the entire streaming pipeline from crashing over a single corrupted JSON body
        print(f"❌ Error processing message: {str(e)}")
        continue
    except KeyboardInterrupt:
        print("\n🛑 Shutting down streaming pipeline gracefully...")

    finally:
        # This prevents the atexit crash by shutting down connections cleanly first
        print("🔌 Closing Kafka connections...")
        try:
            producer.flush()  # Force send any buffered messages remaining in memory
        except Exception as e:
            print(f"Error during flush: {e}")
        finally:
            producer.close()  # Safely terminate the producer threads
            consumer.close()  # Safely close the consumer connection
            print("✅ Kafka connections closed successfully.")
