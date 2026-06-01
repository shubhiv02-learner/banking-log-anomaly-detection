import warnings
from sklearn.exceptions import InconsistentVersionWarning
from pathlib import Path
import joblib

# Suppress the version mismatch warning
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)


from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'banking_logs',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    consumer_timeout_ms=60000
)

print("Waiting for messages...")

for msg in consumer:
    print(msg.value)

BASE_DIR = Path(__file__).resolve().parent.parent

model_path = BASE_DIR / "models" / "isolation_forest_model_raw.joblib"

model = joblib.load(model_path)