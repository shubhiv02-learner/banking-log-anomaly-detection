from kafka import KafkaProducer
import pandas as pd
import json
import time
from pathlib import Path

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda x: json.dumps(x).encode("utf-8")
)

BASE_DIR = Path(__file__).resolve().parent.parent

csv_path = BASE_DIR / "data" / "banking_logs.csv"

logs = pd.read_csv(csv_path)
print(logs.head())


for _, row in logs.iterrows():

    event = row.to_dict()

    future = producer.send(
        "banking_logs",
        event
    )
    result = future.get(timeout=10)
    print(result)	
    print(
        f"Sent {event['timestamp']}"
    )

    producer.flush()

    time.sleep(2)
