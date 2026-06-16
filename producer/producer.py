#from kafka import KafkaProducer
import pandas as pd
import json
import time
from pathlib import Path

import json
from confluent_kafka import Producer

def delivery_report(err, msg):
    """ Called once for each message success or failure. """
    if err is not None:
        print(f"❌ Message delivery failed: {err}")
    else:
        print(f"🎯 ACTUAL SUCCESS! Saved to partition {msg.partition()} at offset {msg.offset()}")

# 1. Configuration matching your docker external port  'host.docker.internal:9092'
conf = {
    'bootstrap.servers': 'host.docker.internal:9092',
    'client.id': 'python-producer'
}

producer = Producer(conf)

#payload = {"status": "active", "message": "Guaranteed Data Delivery"}

try:
    print("🚀 Attempting connection to localhost:9092...")
    
    BASE_DIR = Path(__file__).resolve().parent.parent

    csv_path = BASE_DIR / "data" / "banking_logs.csv"
    #csv_path = BASE_DIR / "data/processed" / "banking_logs_processed.csv"
    df = pd.read_csv(csv_path)
    #logs = raw_data.rename(columns=COLUMN_MAPPING)
    # 3. Create a clean working DataFrame containing ONLY the columns you care about
    # .filter() avoids crashes if the CSV has extra, unexpected metadata columns
    #available_columns = [col for col in COLUMN_MAPPING.values() if col in raw_df.columns]
    #logs = raw_df[available_columns].copy()

    print(df.head())

    for _, row in df.iterrows():
        record = row.to_dict()
        producer.produce(
            topic="banking_logs",
            value=json.dumps(record).encode("utf-8")
        )
        producer.poll(0)

    producer.flush()
    time.sleep(2)
except Exception as e:
    print(f"❌ System Level Connection Error: {e}")

