import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from confluent_kafka import Producer
from dotenv import load_dotenv
import os

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logging_config import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)


def delivery_report(err, msg):
    if err is not None:
        logger.error("Kafka delivery failed: %s", err)
    else:
        logger.debug(
            "Kafka message delivered partition=%s offset=%s",
            msg.partition(),
            msg.offset(),
        )


conf = {
    "bootstrap.servers": "host.docker.internal:9092",
    "client.id": "python-producer",
}

producer = Producer(conf)

try:
    logger.info("Connecting Kafka producer bootstrap=host.docker.internal:9092")

    load_dotenv()
    file_path = Path(os.getenv("OUTPUT_DATA_LOG_PATH_CSV"))
    if not file_path:
        logger.error("OUTPUT_DATA_LOG_PATH_CSV is not set")
        raise ValueError("OUTPUT_DATA_LOG_PATH_CSV environment variable is required")

    logger.info("Producer source file path=%s", file_path.resolve())

    def batch_then_stream(csv_path):
        df = pd.read_csv(csv_path)
        logger.info(
            "Batch mode starting rows=%s columns=%s",
            len(df),
            list(df.columns),
        )
        for _, row in df.iterrows():
            record = row.to_dict()
            producer.produce(
                "banking_logs",
                json.dumps(record).encode("utf-8"),
                callback=delivery_report,
            )
            producer.poll(0)
        producer.flush()
        logger.info("Batch mode finished — switching to tail streaming")

        with open(csv_path, "r") as f:
            f.seek(0, 2)
            while True:
                line = f.readline()
                if not line:
                    time.sleep(1)
                    continue
                fields = line.strip().split(",")
                record = {"status": fields[0], "message": fields[1]}
                producer.produce(
                    "banking_logs",
                    json.dumps(record).encode("utf-8"),
                    callback=delivery_report,
                )
                logger.debug("Streamed live record to topic banking_logs")
                producer.poll(0)

    batch_then_stream(file_path)

except Exception as e:
    logger.exception("Producer failed: %s", e)
