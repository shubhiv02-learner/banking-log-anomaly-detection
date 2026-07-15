#from kafka import KafkaProducer
import pandas as pd
import json
import time
from pathlib import Path
from confluent_kafka import Producer
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
import numpy as np

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

try:
    print("🚀 Attempting connection to localhost:9092...")
    


    #file_path = BASE_DIR / "data" / "banking_logs.csv"
    #file_path = BASE_DIR / "data/processed" / "banking_logs_processed_new.csv"

    # 1. Dynamically calculate the path to the root folder
    SCRIPT_DIR = Path(__file__).resolve().parent
    ROOT_DIR = SCRIPT_DIR.parent
    if str(ROOT_DIR) not in sys.path:
        sys.path.append(str(ROOT_DIR))

    load_dotenv()
    file_path = Path(os.getenv("OUTPUT_DATA_LOG_PATH_CSV"))

    def batch_then_stream(file_path):
        # --- Batch mode: process whole file once ---
        df = pd.read_csv(file_path)   # assumes CSV with consistent columns
        print(df.columns)
        #input('in producer ...')
        for _, row in df.iterrows():
            record = row.to_dict()
           
            producer.produce("banking_logs", json.dumps(record).encode("utf-8"), callback=delivery_report)
            producer.poll(0)
        producer.flush()
        print("✅ Batch mode finished. Switching to streaming mode...")

        # --- Streaming mode: tail new lines until user exits ---
        with open(file_path, "r") as f:
            f.seek(0, 2)  # move to end of file
            while True:
                line = f.readline()
                if not line:
                    time.sleep(1)
                    continue
                fields = line.strip().split(",")
                record = {"status": fields[0], "message": fields[1]}
                producer.produce("banking_logs", json.dumps(record).encode("utf-8"), callback=delivery_report)
                print("live record processed   ")
                producer.poll(0)

    # Run hybrid mode
    batch_then_stream(file_path)

except Exception as e:
    print(f"❌ System Level Connection Error: {e}")

