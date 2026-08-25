# ----
# Product Name: SentryyIQ
# Component Name: probe_json_columns
# Purpose: Read-only JSONB probe for incidents and window_metrics (V1.3 design).
# Author: Salveris Platform (D0)
# ----

"""Read-only sentineliq JSONB probe for Salveris V1.3 live context design."""

from __future__ import annotations

import json
import os
import statistics
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_ROOT / ".env")

from backend.logging_config import get_logger, setup_logging

setup_logging()
_logger = get_logger(__name__)

_RAW_DATA_RECORD_LIMIT = 2500


def _require_database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        _logger.error("DATABASE_URL is not set in environment.")
        sys.exit(1)
    return url


def _run_probe() -> dict:
    engine = create_engine(_require_database_url())
    report: dict = {"raw_data_record_limit_alignment": _RAW_DATA_RECORD_LIMIT}

    with engine.connect() as conn:
        counts = conn.execute(
            text(
                """
                SELECT
                  (SELECT COUNT(*) FROM incidents) AS incident_count,
                  (SELECT COUNT(*) FROM incidents WHERE incident_summary IS NOT NULL)
                    AS incident_summary_non_null,
                  (SELECT COUNT(*) FROM window_metrics) AS window_metrics_count,
                  (SELECT COUNT(*) FROM window_metrics WHERE payload_json IS NOT NULL)
                    AS payload_json_non_null,
                  (SELECT COUNT(*) FROM window_metrics WHERE payload_summary IS NOT NULL)
                    AS payload_summary_non_null,
                  (SELECT COUNT(*) FROM alerts) AS alert_count,
                  (SELECT COUNT(*) FROM alerts a
                     JOIN window_metrics wm ON wm.id = a.window_metric_id)
                    AS alerts_with_window_metrics
                """
            )
        ).mappings().one()
        report["counts"] = dict(counts)

        typeof_rows = conn.execute(
            text(
                """
                SELECT 'incidents.incident_summary' AS column_label,
                       jsonb_typeof(incident_summary) AS jsonb_type,
                       COUNT(*) AS row_count
                FROM incidents
                WHERE incident_summary IS NOT NULL
                GROUP BY 1, 2
                UNION ALL
                SELECT 'window_metrics.payload_summary',
                       jsonb_typeof(payload_summary),
                       COUNT(*)
                FROM window_metrics
                WHERE payload_summary IS NOT NULL
                GROUP BY 1, 2
                UNION ALL
                SELECT 'window_metrics.payload_json',
                       jsonb_typeof(payload_json),
                       COUNT(*)
                FROM window_metrics
                WHERE payload_json IS NOT NULL
                GROUP BY 1, 2
                ORDER BY 1, 2
                """
            )
        ).mappings().all()
        report["jsonb_typeof"] = [dict(r) for r in typeof_rows]

        size_stats = conn.execute(
            text(
                """
                SELECT 'incidents.incident_summary' AS column_label,
                       MIN(pg_column_size(incident_summary)) AS min_bytes,
                       PERCENTILE_CONT(0.5) WITHIN GROUP (
                         ORDER BY pg_column_size(incident_summary)
                       ) AS median_bytes,
                       MAX(pg_column_size(incident_summary)) AS max_bytes,
                       AVG(pg_column_size(incident_summary))::bigint AS avg_bytes
                FROM incidents
                WHERE incident_summary IS NOT NULL
                UNION ALL
                SELECT 'window_metrics.payload_summary',
                       MIN(pg_column_size(payload_summary)),
                       PERCENTILE_CONT(0.5) WITHIN GROUP (
                         ORDER BY pg_column_size(payload_summary)
                       ),
                       MAX(pg_column_size(payload_summary)),
                       AVG(pg_column_size(payload_summary))::bigint
                FROM window_metrics
                WHERE payload_summary IS NOT NULL
                UNION ALL
                SELECT 'window_metrics.payload_json',
                       MIN(pg_column_size(payload_json)),
                       PERCENTILE_CONT(0.5) WITHIN GROUP (
                         ORDER BY pg_column_size(payload_json)
                       ),
                       MAX(pg_column_size(payload_json)),
                       AVG(pg_column_size(payload_json))::bigint
                FROM window_metrics
                WHERE payload_json IS NOT NULL
                """
            )
        ).mappings().all()
        report["pg_column_size"] = [
            {k: (float(v) if k == "median_bytes" else v) for k, v in dict(r).items()}
            for r in size_stats
        ]

        incident_keys = conn.execute(
            text(
                """
                SELECT DISTINCT jsonb_object_keys(incident_summary) AS key_name
                FROM incidents
                WHERE incident_summary IS NOT NULL
                  AND jsonb_typeof(incident_summary) = 'object'
                ORDER BY 1
                """
            )
        ).scalars().all()
        report["incident_summary_top_level_keys"] = list(incident_keys)

        payload_summary_keys = conn.execute(
            text(
                """
                SELECT DISTINCT jsonb_object_keys(payload_summary) AS key_name
                FROM window_metrics
                WHERE payload_summary IS NOT NULL
                  AND jsonb_typeof(payload_summary) = 'object'
                ORDER BY 1
                """
            )
        ).scalars().all()
        report["payload_summary_top_level_keys"] = list(payload_summary_keys)

        array_lengths = conn.execute(
            text(
                """
                SELECT
                  jsonb_array_length(payload_json) AS arr_len,
                  pg_column_size(payload_json) AS payload_bytes
                FROM window_metrics
                WHERE payload_json IS NOT NULL
                  AND jsonb_typeof(payload_json) = 'array'
                """
            )
        ).mappings().all()
        lengths = [int(r["arr_len"]) for r in array_lengths]
        bytes_list = [int(r["payload_bytes"]) for r in array_lengths]
        over_limit = [n for n in lengths if n > _RAW_DATA_RECORD_LIMIT]
        report["payload_json_array"] = {
            "rows_as_array": len(lengths),
            "min_length": min(lengths) if lengths else None,
            "max_length": max(lengths) if lengths else None,
            "median_length": statistics.median(lengths) if lengths else None,
            "min_bytes": min(bytes_list) if bytes_list else None,
            "max_bytes": max(bytes_list) if bytes_list else None,
            "median_bytes": statistics.median(bytes_list) if bytes_list else None,
            "rows_over_raw_data_limit": len(over_limit),
            "max_length_over_limit": max(over_limit) if over_limit else None,
        }

        first_elem_keys = conn.execute(
            text(
                """
                SELECT DISTINCT jsonb_object_keys(payload_json->0) AS key_name
                FROM window_metrics
                WHERE payload_json IS NOT NULL
                  AND jsonb_typeof(payload_json) = 'array'
                  AND jsonb_array_length(payload_json) > 0
                  AND jsonb_typeof(payload_json->0) = 'object'
                ORDER BY 1
                """
            )
        ).scalars().all()
        report["payload_json_first_element_keys"] = list(first_elem_keys)

        sample_row = conn.execute(
            text(
                """
                SELECT ticket_id, incident_summary
                FROM incidents
                WHERE incident_summary IS NOT NULL
                ORDER BY id
                LIMIT 1
                """
            )
        ).mappings().one_or_none()
        if sample_row:
            summary = sample_row["incident_summary"]
            if isinstance(summary, str):
                summary = json.loads(summary)
            truncated = json.dumps(summary, default=str)
            if len(truncated) > 1200:
                truncated = truncated[:1200] + "…[truncated]"
            report["sample_incident_summary"] = {
                "ticket_id": sample_row["ticket_id"],
                "structure_preview": truncated,
            }

    return report


def main() -> None:
    report = _run_probe()
    _logger.info("JSONB probe report:\n%s", json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
