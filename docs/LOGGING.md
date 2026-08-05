# Logging

Central configuration: [`logging_config.py`](../logging_config.py) at the repository root.

## Environment

| Variable   | Values              | Default |
|------------|---------------------|---------|
| `LOG_LEVEL` | `INFO`, `DEBUG`, `ERROR` | `INFO` |

Logs go to **stdout** and `logs/application.log` (rotating, 5 MB × 5 files).

## Format

```
2026-08-05 09:15:00 | INFO     | consumer.consumer              | Window closed ...
```

## Usage

```python
from logging_config import setup_logging, get_logger

setup_logging()  # once per process entrypoint
logger = get_logger(__name__)

logger.info("Started")
logger.debug("detail=%s", value)
logger.error("Failed: %s", err)
```

Backend modules may use `from backend.logging_config import get_logger` (re-exports root config).

## Entrypoints that call `setup_logging()`

- FastAPI: `backend/main.py` lifespan (+ `backend/database.py` on import)
- Kafka: `consumer/consumer.py`, `producer/producer.py`
- Offline pipeline: `src/run_logs.py`
- Migrations helper: `backend/create_tables.py`

## Consumer / database

The streaming consumer logs window boundaries, scoring, anomalies, and relies on `backend/db_services.py` for **insert/update** audit lines (`window_metric`, `alert`, `ticket`, payload updates, n8n notifications).
