from datetime import datetime
import re

from sqlalchemy import func, case, text, or_
from sqlalchemy.orm import defer
from .db_models import Alert, WindowMetrics, Ticket, IncidentAssignmentHistory, UserMaster
import backend.schemas as schemas
from backend.logging_config import get_logger

logger = get_logger(__name__)

RAW_DATA_BULK_LIMIT = 2500
RAW_DATA_PAGE_MAX = 50
SQL_ROLLUP_TOP_N = 10
PATTERN_BUCKET_COUNT = 4
PATTERN_SPIKE_SHARE = 0.5
PATTERN_WIDESPREAD_MIN_HOSTS = 3
PATTERN_WIDESPREAD_MIN_CLIENTS = 3

def get_alerts(
        db,
        skip: int = 0,
        limit: int = 100 #ideally should be 50, since status not getting closed as of now
    ):
    
    alerts = (
        db.query(Alert)
        .order_by(Alert.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return alerts



def get_recent_alerts(db, limit: int = 5):

    return (
    db.query(Alert)
    .order_by(Alert.created_at.desc())
    .limit(limit)
    .all()
)


def get_dashboard_summary(db):


    return {
        "total_alerts":
            db.query(Alert)
             .filter(Alert.status == "OPEN")
            .count(),

        "critical":
            db.query(Alert)
            .filter(Alert.priority == "Critical", Alert.status == "OPEN" )
            .count(),

        "high":
            db.query(Alert)
            .filter(Alert.priority == "High")
            .count(),

        "medium":
            db.query(Alert)
            .filter(Alert.priority == "Medium")
            .count(),
         
        "low":
            db.query(Alert)
            .filter(Alert.priority == "Low")
            .count()
}

#Low remove later as Alert is not getting generated in this case
#When Status is built than needs to be changed
def get_service_distribution(db):

    rows = (
            db.query(
             Alert.service,
            func.count(Alert.id)
)           .filter(Alert.status == "OPEN").group_by(Alert.service).all()
                )

    return [
        {
            "service": row[0],
            "count": row[1]
        }
        for row in rows
        ]


    
def get_alert_by_id(db, alert_id: int):
    return (
    db.query(Alert)
    .filter(Alert.id == alert_id)
    .first()
)

def get_window_metrics(
    db,
    skip: int = 0,
    limit: int = 100
):

    return (
        db.query(WindowMetrics)
        .options(defer(WindowMetrics.payload_json))
        .options(defer(WindowMetrics.payload_summary))
        .order_by(WindowMetrics.window_start.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_recent_window_metrics(
    db,
    limit: int = 10
):

    return (
        db.query(WindowMetrics)
        .options(defer(WindowMetrics.payload_json))
        .options(defer(WindowMetrics.payload_summary))
        .order_by(WindowMetrics.window_start.desc())
        .limit(limit)
        .all()
    )

def get_window_metrics_by_service(
    db,
    service: str,
    limit: int = 50
):

    return (
        db.query(WindowMetrics)
        .options(defer(WindowMetrics.payload_json))
        .options(defer(WindowMetrics.payload_summary))
        .filter(WindowMetrics.service == service)
        .order_by(WindowMetrics.window_start.desc())
        .limit(limit)
        .all()
    )

def get_window_metric_by_id(
    db,
    metric_id: int
):
    metrics =  (
        db.query(WindowMetrics)
        .options(defer(WindowMetrics.payload_json))
        .options(defer(WindowMetrics.payload_summary))
        .filter(WindowMetrics.id == metric_id)
        .first()
    )
    return metrics
"""
def get_window_metric_details_by_id(db, metric_id: int):
        win_details = (
        db.query(WindowMetrics)
        .options(
            load_only(
                WindowMetrics.payload_json, 
                # If your id is required to fetch, you can include it, 
                # but load_only automatically includes the primary key.
                WindowMetrics.payload_summary
            )
        )
        .filter(WindowMetrics.id == metric_id)
        .first())
        print("Fetched window detils")  # debug line
        return win_details
    
"""

def get_window_metric_details_by_id(db, metric_id: int):
    # Use the main model to target exactly what you want
    row = (
        db.query(
            WindowMetrics.id, # Include ID so your frontend can map things cleanly
            WindowMetrics.payload_json, 
            WindowMetrics.payload_summary
        )
        .filter(WindowMetrics.id == metric_id)
        .first()
    )
    
    if row:
        print("Fetched data from DB successfully!")
        # Normalize JSONB string/double-encoded values before FastAPI response validation.
        from schemas import _parse_json_field
        return {
            "id": row.id,
            "payload_json": _parse_json_field(row.payload_json),
            "payload_summary": _parse_json_field(row.payload_summary),
        }
    
    return None


##############INCIDENTS#############

def get_incidents(
        db,
        skip: int = 0,
        limit: int = 50 #ideally should be 50, since status not getting closed as of now
    ):
    
    incidents = (
        db.query(Ticket)
        .options(defer(Ticket.incident_summary))
        .order_by(Ticket.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return incidents


def get_incidents_by_id(db, alert_id: int):
    
    incidents = (
        db.query(Ticket)
        .filter(Alert.id == alert_id)
        .options(defer(Ticket.incident_summary))
        .first()
    )
    return incidents


################################################################
# Methods for agent - Created as for UI sending 100+ records
# By Id, its just last 4 digit
################################################################



def get_agent_incidents(
    db,
    skip: int = 0,
    limit: int = 5,
    services: list[str] | None = None,
    priorities: list[str] | None = None,
    statuses: list[str] | None = None,
    assignee_scope: str | None = None,
    assignees: list[str] | None = None,
):
    
    severity_order = case(
        (func.upper(Ticket.priority) == "CRITICAL", 1),
        (func.upper(Ticket.priority) == "HIGH", 2),
        (func.upper(Ticket.priority) == "MEDIUM", 3),
        (func.upper(Ticket.priority) == "LOW", 4),
        else_=5
    )

    status_values = [
        str(value).strip().upper()
        for value in (statuses or [])
        if value is not None and str(value).strip()
    ]
    # Default: open queue only (backward compatible with "show open incidents").
    if not status_values:
        status_values = ["OPEN"]

    query = db.query(Ticket).filter(func.upper(Ticket.status).in_(status_values))

    service_values = [
        str(value).strip().casefold()
        for value in (services or [])
        if value is not None and str(value).strip()
    ]
    if service_values:
        query = query.filter(func.lower(Ticket.service).in_(service_values))

    priority_values = [
        str(value).strip().upper()
        for value in (priorities or [])
        if value is not None and str(value).strip()
    ]
    if priority_values:
        query = query.filter(func.upper(Ticket.priority).in_(priority_values))

    scope_mode = (assignee_scope or "").strip().casefold()
    assignee_values = [
        str(value).strip().upper()
        for value in (assignees or [])
        if value is not None and str(value).strip()
    ]
    if scope_mode == "mine" and assignee_values:
        queue_assignees = (
            "SYSTEM",
            "SUPPORT",
            "OPS MANAGER",
            "UNASSIGNED",
            "NONE",
            "N/A",
        )
        query = query.filter(
            or_(
                func.upper(Ticket.status) != "ASSIGNED",
                Ticket.assignee.is_(None),
                func.trim(Ticket.assignee) == "",
                func.upper(Ticket.assignee).in_(queue_assignees),
                func.upper(Ticket.assignee).in_(assignee_values),
            )
        )

    total = query.with_entities(func.count(Ticket.ticket_id)).scalar()

    incidents = (
        query.order_by(
            severity_order,
            Ticket.created_at.desc(),
        )
        .offset(skip)
        .limit(limit)
        .all()
    )
    logger.debug(
        "Agent incidents listed total=%s returned=%s services=%s "
        "priorities=%s statuses=%s assignee_scope=%s",
        total,
        len(incidents),
        service_values or None,
        priority_values or None,
        status_values,
        scope_mode or None,
    )
    return {
        "total": total,
        "latest_count": len(incidents),
        "incidents": incidents
    }

def get_agent_incident_by_id(db, tkt_id: str):
    token = (tkt_id or "").strip()
    if not token:
        return None
    exact = (
        db.query(Ticket)
        .filter(Ticket.ticket_id.ilike(token))
        .order_by(Ticket.created_at.desc())
        .first()
    )
    if exact is not None:
        return exact
    digits = re.findall(r"\d+", token)
    if not digits:
        return None
    return (
        db.query(Ticket)
        .filter(Ticket.ticket_id.like(f"%{digits[-1]}%"))
        .order_by(Ticket.created_at.desc())
        .first()
    )

def get_assignment_history(db,ticket_id: str):
    return (
        db.query(IncidentAssignmentHistory)
        .filter(
            IncidentAssignmentHistory.ticket_id.like(f"%{ticket_id}%")
        )
        .order_by(
            IncidentAssignmentHistory.assignment_time.desc()
        )
        .all()
    )

def get_users(db):

    return (
        db.query(UserMaster)
        .filter(
            UserMaster.active == True
        )
        .order_by(
            UserMaster.name
        )
        .all()
    )

def assign_incident(
    db,
    incident,
    assigned_to,
    remarks,
    prevt_remarks,
    action: schemas.IncidentAction = schemas.IncidentAction.ASSIGNED,
    assigned_by: str = "OPS MANAGER",
):
    
    prev_assignee = incident.assignee

    history = IncidentAssignmentHistory(
        ticket_id=incident.ticket_id,
        previous_assignee=prev_assignee,
        assigned_to=(assigned_to or "").upper(),
        assigned_by=(assigned_by or "OPS MANAGER").strip() or "OPS MANAGER",
        action=action,
        remarks=remarks
    )

    db.add(history)

    incident.assignee = (assigned_to or "").upper()
    incident.status = action
    incident.updated_at = datetime.utcnow()
    if incident.status == schemas.IncidentAction.CLOSED:
        resolution, preventive_action = get_preventive_actions(remarks)
        incident.resolution = resolution
        incident.preventive_action = preventive_action
    db.commit()

    db.refresh(history)
    logger.info(
        "Updated incident ticket_id=%s action=%s assignee=%s",
        incident.ticket_id,
        action,
        incident.assignee,
    )

    return history

def get_preventive_actions(remarks: str | None) -> tuple[str | None, str | None]:
    if remarks is None:
        return None

    # Split the remarks into lines and filter out empty lines
    lines = [line.strip() for line in remarks.splitlines() if line.strip()]

    # Join the non-empty lines back together with newline characters
    lines = "\n".join(lines) if lines else None
    
    resolution_match = re.search(
        r"Closure Remark:\s*(.*?)(?:Preventive Action:|$)",
        lines,
        re.DOTALL | re.IGNORECASE
    )

    preventive_match = re.search(
        r"Preventive Action:\s*(.*)$",
        lines,
        re.DOTALL | re.IGNORECASE
    )
    resolution = resolution_match.group(1).strip() if resolution_match else None
    preventive_action = preventive_match.group(1).strip() if preventive_match else None
    logger.debug(
        "Parsed closure remarks resolution=%s preventive_action=%s",
        resolution is not None,
        preventive_action is not None,
    )
    return resolution, preventive_action

#*********************Alert Details for Agent
def round_float(value, places=4):
    if value is None:
        return None
    try:
        return round(float(value), places)
    except (ValueError, TypeError):
        return None
# Get details for Alert from Windows and Incident
def get_agent_alert_details_by_id(db, ticket_id: str):
    result = (
        db.query(
            Alert.id,
            Ticket.ticket_id,
            Alert.service,
            Alert.priority, 
            Alert.status,
            WindowMetrics.window_start,
            WindowMetrics.window_end,
            Alert.final_score,
            WindowMetrics.ml_score,
            WindowMetrics.statistical_score,
            WindowMetrics.ewma,
            WindowMetrics.cusum,
            WindowMetrics.persistence_score,
            WindowMetrics.incident_probability,
            WindowMetrics.record_count,
            WindowMetrics.error_count,
            WindowMetrics.latency_mean,
            WindowMetrics.latency_max,
            WindowMetrics.latency_std,
            WindowMetrics.cpu_mean,
            WindowMetrics.cpu_max,
            WindowMetrics.memory_mean,
            WindowMetrics.queue_lag_mean,
            WindowMetrics.queue_lag_max            
        )
        .join(WindowMetrics, Alert.window_metric_id == WindowMetrics.id)
        .join(Ticket, Ticket.alert_id == Alert.id)
        .filter(Alert.id == ticket_id)
        .first()
    )

    if not result:
        return None

    return {
        "alert_id": result.id,
        "ticket_id": result.ticket_id,
        "status": result.status,
        "priority": result.priority,
        "service": result.service,
        "window_start": result.window_start.strftime("%Y-%m-%d %H:%M:%S") if result.window_start else None,
        "window_end": result.window_end.strftime("%Y-%m-%d %H:%M:%S") if result.window_end else None,
        "final_score": round_float(result.final_score),
        "ml_score": round_float(result.ml_score),
        "statistical_score": round_float(result.statistical_score),
        "ewma": round_float(result.ewma),
        "cusum": round_float(result.cusum),
        "persistence_score": round_float(result.persistence_score),
        "incident_probability": round_float(result.incident_probability),
        "record_count": result.record_count,
        "latency_mean": round_float(result.latency_mean),
        "latency_max": round_float(result.latency_max),
        "latency_std": round_float(result.latency_std),
        "cpu_mean": round_float(result.cpu_mean),
        "cpu_max": round_float(result.cpu_max),
        "memory_mean": round_float(result.memory_mean),
        "queue_lag_mean": round_float(result.queue_lag_mean),
        "queue_lag_max": round_float(result.queue_lag_max),
        "error_count": round_float(result.error_count),
    }


def _jsonb_payload_array_sql():
    return """
        CASE
            WHEN jsonb_typeof(wm.payload_json) = 'array' THEN wm.payload_json
            ELSE '[]'::jsonb
        END
    """


def _sql_top_facet(db, metric_id: int, json_key: str) -> list[dict]:
    array_sql = _jsonb_payload_array_sql()
    result = db.execute(
        text(
            f"""
            SELECT rec ->> :json_key AS facet_value, COUNT(*) AS cnt
            FROM window_metrics wm
            CROSS JOIN LATERAL jsonb_array_elements({array_sql}) AS rec
            WHERE wm.id = :metric_id
              AND rec ->> :json_key IS NOT NULL
              AND rec ->> :json_key <> ''
            GROUP BY rec ->> :json_key
            ORDER BY cnt DESC
            LIMIT :top_n
            """
        ),
        {
            "metric_id": metric_id,
            "json_key": json_key,
            "top_n": SQL_ROLLUP_TOP_N,
        },
    )
    rows = []
    for row in result:
        rows.append({"value": row[0], "count": int(row[1])})
    return rows


def _build_sql_rollup(db, metric_id: int) -> dict:
    array_sql = _jsonb_payload_array_sql()
    count_row = db.execute(
        text(
            f"""
            SELECT jsonb_array_length({array_sql})
            FROM window_metrics wm
            WHERE wm.id = :metric_id
            """
        ),
        {"metric_id": metric_id},
    ).first()
    record_count = int(count_row[0]) if count_row and count_row[0] is not None else 0
    top_errors = _sql_top_facet(db, metric_id, "error_code")
    top_clients = _sql_top_facet(db, metric_id, "client_id")
    top_hosts = _sql_top_facet(db, metric_id, "machine_id")
    regions = _sql_top_facet(db, metric_id, "region")
    return {
        "record_count": record_count,
        "top_errors": [
            {"error_code": item["value"], "count": item["count"]}
            for item in top_errors
        ],
        "top_clients": [
            {"client_id": item["value"], "count": item["count"]}
            for item in top_clients
        ],
        "top_hosts": [
            {"machine_id": item["value"], "count": item["count"]}
            for item in top_hosts
        ],
        "regions": [
            {"region": item["value"], "count": item["count"]}
            for item in regions
        ],
        "pattern": _classify_pattern(_sql_pattern_aggregates(db, metric_id)),
    }


def _sql_pattern_aggregates(db, metric_id: int) -> dict:
    """
    Aggregates anomaly timing and spread in SQL. Does not return raw records.
    """
    array_sql = _jsonb_payload_array_sql()
    row = db.execute(
        text(
            f"""
            WITH recs AS (
                SELECT
                    rec,
                    CASE
                        WHEN rec ->> 'timestamp' ~ '^[0-9]{{4}}-'
                        THEN (rec ->> 'timestamp')::timestamptz
                        ELSE NULL
                    END AS ts,
                    (
                        LOWER(COALESCE(rec ->> 'is_anomaly', 'false'))
                            IN ('true', 't', '1')
                        OR UPPER(COALESCE(rec ->> 'status', ''))
                            IN ('ERROR', 'FAILED')
                        OR NULLIF(TRIM(rec ->> 'error_code'), '') IS NOT NULL
                    ) AS is_problem
                FROM window_metrics wm
                CROSS JOIN LATERAL jsonb_array_elements({array_sql}) AS rec
                WHERE wm.id = :metric_id
            ),
            bounds AS (
                SELECT
                    MIN(ts) FILTER (WHERE ts IS NOT NULL) AS ts_min,
                    MAX(ts) FILTER (WHERE ts IS NOT NULL) AS ts_max,
                    COUNT(*) FILTER (WHERE is_problem) AS problem_count,
                    COUNT(DISTINCT rec ->> 'machine_id')
                        FILTER (
                            WHERE is_problem
                              AND NULLIF(rec ->> 'machine_id', '') IS NOT NULL
                        ) AS problem_hosts,
                    COUNT(DISTINCT rec ->> 'client_id')
                        FILTER (
                            WHERE is_problem
                              AND NULLIF(rec ->> 'client_id', '') IS NOT NULL
                        ) AS problem_clients
                FROM recs
            ),
            first_hit AS (
                SELECT
                    rec ->> 'machine_id' AS first_host,
                    rec ->> 'client_id' AS first_client,
                    ts AS first_ts
                FROM recs
                WHERE is_problem AND ts IS NOT NULL
                ORDER BY ts ASC
                LIMIT 1
            ),
            bucketed AS (
                SELECT
                    WIDTH_BUCKET(
                        EXTRACT(EPOCH FROM recs.ts),
                        EXTRACT(EPOCH FROM bounds.ts_min),
                        EXTRACT(EPOCH FROM bounds.ts_max) + 1.0,
                        :bucket_count
                    ) AS bucket_no,
                    COUNT(*) FILTER (WHERE recs.is_problem) AS problem_count,
                    MIN(recs.ts) AS time_from,
                    MAX(recs.ts) AS time_to
                FROM recs
                CROSS JOIN bounds
                WHERE recs.ts IS NOT NULL
                  AND bounds.ts_min IS NOT NULL
                  AND bounds.ts_max IS NOT NULL
                  AND bounds.ts_max > bounds.ts_min
                GROUP BY 1
            )
            SELECT
                bounds.problem_count,
                bounds.problem_hosts,
                bounds.problem_clients,
                bounds.ts_min,
                bounds.ts_max,
                first_hit.first_host,
                first_hit.first_client,
                first_hit.first_ts,
                (
                    SELECT COALESCE(json_agg(json_build_object(
                        'index', bucketed.bucket_no,
                        'problem_count', bucketed.problem_count,
                        'time_from', bucketed.time_from,
                        'time_to', bucketed.time_to
                    ) ORDER BY bucketed.bucket_no), '[]'::json)
                    FROM bucketed
                ) AS buckets
            FROM bounds
            LEFT JOIN first_hit ON TRUE
            """
        ),
        {"metric_id": metric_id, "bucket_count": PATTERN_BUCKET_COUNT},
    ).first()
    if row is None:
        return {
            "problem_count": 0,
            "problem_hosts": 0,
            "problem_clients": 0,
            "ts_min": None,
            "ts_max": None,
            "first_host": None,
            "first_client": None,
            "first_ts": None,
            "buckets": [],
        }
    buckets = row[8] or []
    if isinstance(buckets, str):
        buckets = schemas._parse_json_field(buckets)
    if not isinstance(buckets, list):
        buckets = []
    return {
        "problem_count": int(row[0] or 0),
        "problem_hosts": int(row[1] or 0),
        "problem_clients": int(row[2] or 0),
        "ts_min": row[3],
        "ts_max": row[4],
        "first_host": row[5],
        "first_client": row[6],
        "first_ts": row[7],
        "buckets": buckets,
    }


def _iso(value) -> str | None:
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _bucket_problem_count(bucket: dict) -> int:
    return int(bucket.get("problem_count") or 0)


def _classify_pattern(aggregates: dict) -> dict:
    """
    Classifies spread from SQL aggregates only (no raw records).
    """
    problem_count = int(aggregates.get("problem_count") or 0)
    buckets = list(aggregates.get("buckets") or [])
    first_ts = _iso(aggregates.get("first_ts"))
    observed_from = _iso(aggregates.get("ts_min"))
    observed_to = _iso(aggregates.get("ts_max"))
    base = {
        "labels": ["insufficient"],
        "primary": "insufficient",
        "first_problem_at": first_ts,
        "first_host": aggregates.get("first_host"),
        "first_client": aggregates.get("first_client"),
        "problem_record_count": problem_count,
        "distinct_problem_hosts": int(aggregates.get("problem_hosts") or 0),
        "distinct_problem_clients": int(aggregates.get("problem_clients") or 0),
        "observed_from": observed_from,
        "observed_to": observed_to,
        "buckets": buckets,
        "recommended_raw_fetch": {
            "scope": "whole_window",
            "time_from": observed_from,
            "time_to": observed_to,
        },
    }
    if problem_count <= 0:
        return base
    labels: list[str] = []
    if (
        base["distinct_problem_hosts"] >= PATTERN_WIDESPREAD_MIN_HOSTS
        or base["distinct_problem_clients"] >= PATTERN_WIDESPREAD_MIN_CLIENTS
    ):
        labels.append("widespread")
    peak = None
    share = 0.0
    if buckets:
        peak = max(buckets, key=_bucket_problem_count)
        peak_count = _bucket_problem_count(peak)
        share = peak_count / problem_count if problem_count else 0.0
        buckets_with_problems = sum(
            1 for bucket in buckets if _bucket_problem_count(bucket) > 0
        )
        if share >= PATTERN_SPIKE_SHARE and buckets_with_problems < len(buckets):
            labels.append("spike")
        counts = [
            _bucket_problem_count(bucket)
            for bucket in sorted(buckets, key=lambda item: int(item.get("index") or 0))
        ]
        if (
            len(counts) >= 3
            and counts == sorted(counts)
            and counts[-1] > counts[0] * 1.5
        ):
            labels.append("gradual")
        if buckets_with_problems >= 3 and share < PATTERN_SPIKE_SHARE:
            labels.append("continuous")
    if not labels:
        labels = ["mixed"]
    primary = "spike" if "spike" in labels else labels[0]
    rec_from = observed_from
    rec_to = observed_to
    scope = "whole_window"
    if primary == "spike" and peak is not None:
        rec_from = _iso(peak.get("time_from")) or observed_from
        rec_to = _iso(peak.get("time_to")) or observed_to
        scope = "peak_bucket"
    elif primary == "gradual" and buckets:
        last = sorted(buckets, key=lambda item: int(item.get("index") or 0))[-1]
        rec_from = _iso(last.get("time_from")) or observed_from
        rec_to = _iso(last.get("time_to")) or observed_to
        scope = "late_window"
    base["labels"] = labels
    base["primary"] = primary
    base["recommended_raw_fetch"] = {
        "scope": scope,
        "time_from": rec_from,
        "time_to": rec_to,
    }
    return base


def get_window_metric_telemetry_summary(db, metric_id: int):
    row = (
        db.query(
            WindowMetrics.id,
            WindowMetrics.payload_summary,
            WindowMetrics.window_start,
            WindowMetrics.window_end,
        )
        .filter(WindowMetrics.id == metric_id)
        .first()
    )
    if row is None:
        return None
    return {
        "window_metric_id": row.id,
        "window_start": _iso(row.window_start),
        "window_end": _iso(row.window_end),
        "payload_summary": schemas._parse_json_field(row.payload_summary),
        "sql_rollup": _build_sql_rollup(db, metric_id),
    }


def get_alert_telemetry_summary(db, alert_id: str):
    row = (
        db.query(
            Alert.id,
            Alert.window_metric_id,
            Alert.service,
            Alert.priority,
            Alert.status,
        )
        .filter(Alert.id == alert_id)
        .first()
    )
    if row is None or row.window_metric_id is None:
        return None
    summary = get_window_metric_telemetry_summary(db, row.window_metric_id)
    if summary is None:
        return None
    summary["alert_id"] = row.id
    summary["service"] = row.service
    summary["priority"] = row.priority
    summary["status"] = row.status
    return summary


def _alert_scope_fields(db, alert_id: str) -> dict:
    row = (
        db.query(Alert.id, Alert.service, Alert.priority, Alert.status)
        .filter(Alert.id == alert_id)
        .first()
    )
    if row is None:
        return {}
    return {
        "alert_id": row.id,
        "service": row.service,
        "priority": row.priority,
        "status": row.status,
    }


# Get Raw telemetry,alert_id is only digits in ticket 

def get_agent_alert_payload_by_id(
    db,
    alert_id: str,
    skip: int = 0,
    limit: int | None = None,
    time_from: str | None = None,
    time_to: str | None = None,
):
    #Keep it for future debugging
    """
    print(f"Alert id to get payload : {alert_id}", flush=True)
    print(f"alert_id={alert_id!r}, type={type(alert_id)}", flush=True)
    print(
    str(
        db.query(WindowMetrics.payload_json)
        .join(Alert, Alert.window_metric_id == WindowMetrics.id)
        .filter(Alert.id == alert_id)
        .statement.compile(compile_kwargs={"literal_binds": True})
    ),
    flush=True,
    )
    """
    scope = _alert_scope_fields(db, alert_id)
    record_count = (
            db.query(func.jsonb_array_length(WindowMetrics.payload_json))
            .join(Alert, Alert.window_metric_id == WindowMetrics.id)
            .filter(Alert.id == alert_id)
            .scalar()
        )

    if record_count is None:
        return None
    if limit is None:
        if record_count > RAW_DATA_BULK_LIMIT:
            return {
                "status": "too_large",
                "record_count": record_count,
                **scope,
            }
        payload = (
            db.query(WindowMetrics.payload_json)
            .join(Alert, Alert.window_metric_id == WindowMetrics.id)
            .filter(Alert.id == alert_id)
            .scalar()
        )
        return {
            "status": "success",
            "record_count": record_count,
            "payload_json": payload,
            **scope,
        }
    page_limit = min(max(limit, 1), RAW_DATA_PAGE_MAX)
    page_skip = max(skip, 0)
    array_sql = _jsonb_payload_array_sql()
    time_clause = ""
    params = {"alert_id": alert_id, "skip": page_skip, "limit": page_limit}
    if time_from:
        time_clause += """
            AND (t.elem ->> 'timestamp') ~ '^[0-9]{4}-'
            AND (t.elem ->> 'timestamp')::timestamptz
                >= CAST(:time_from AS timestamptz)
        """
        params["time_from"] = time_from
    if time_to:
        time_clause += """
            AND (t.elem ->> 'timestamp') ~ '^[0-9]{4}-'
            AND (t.elem ->> 'timestamp')::timestamptz
                <= CAST(:time_to AS timestamptz)
        """
        params["time_to"] = time_to
    page_sql = (
        f"""
            SELECT t.elem
            FROM alerts a
            JOIN window_metrics wm ON a.window_metric_id = wm.id
            CROSS JOIN LATERAL jsonb_array_elements({array_sql})
                WITH ORDINALITY AS t(elem, ord)
            WHERE a.id = :alert_id
        """
        + time_clause
        + """
            ORDER BY t.ord
            OFFSET :skip
            LIMIT :limit
        """
    )
    page_result = db.execute(text(page_sql), params)
    page = [schemas._parse_json_field(row[0]) for row in page_result]
    return {
        "status": "success",
        "alert_id": int(alert_id) if str(alert_id).isdigit() else alert_id,
        "record_count": record_count,
        "skip": page_skip,
        "limit": page_limit,
        "payload_json": page,
        **scope,
    }


def get_error_mapping_by_code(db, error_code: str) -> schemas.ErrorMappingResponse | None:
    """
    Returns one error_mapping catalog row by code (case-insensitive).

    Args:
        db: SQLAlchemy session.
        error_code: Catalog code such as ERR-705.

    Returns:
        ErrorMappingResponse when found; otherwise None.
    """
    normalized = (error_code or "").strip().upper()
    if not normalized:
        return None
    row = db.execute(
        text(
            """
            SELECT
                error_code,
                error_name,
                description,
                business_impact,
                customer_impact,
                recommended_action,
                severity_default,
                category
            FROM error_mapping
            WHERE UPPER(error_code) = :error_code
            LIMIT 1
            """
        ),
        {"error_code": normalized},
    ).mappings().first()
    if row is None:
        return None
    return schemas.ErrorMappingResponse(
        error_code=row["error_code"],
        error_name=row["error_name"],
        description=row["description"],
        business_impact=row["business_impact"],
        customer_impact=row["customer_impact"],
        recommended_action=row["recommended_action"],
        severity_default=row["severity_default"],
        category=row["category"],
    )


def list_error_mappings(db) -> schemas.ErrorMappingListResponse:
    """
    Returns all error_mapping catalog rows ordered by error_code.

    Args:
        db: SQLAlchemy session.

    Returns:
        ErrorMappingListResponse with total and errors list.
    """
    rows = db.execute(
        text(
            """
            SELECT
                error_code,
                error_name,
                description,
                business_impact,
                customer_impact,
                recommended_action,
                severity_default,
                category
            FROM error_mapping
            ORDER BY error_code
            """
        )
    ).mappings().all()
    errors = [
        schemas.ErrorMappingResponse(
            error_code=row["error_code"],
            error_name=row["error_name"],
            description=row["description"],
            business_impact=row["business_impact"],
            customer_impact=row["customer_impact"],
            recommended_action=row["recommended_action"],
            severity_default=row["severity_default"],
            category=row["category"],
        )
        for row in rows
    ]
    return schemas.ErrorMappingListResponse(total=len(errors), errors=errors)
    