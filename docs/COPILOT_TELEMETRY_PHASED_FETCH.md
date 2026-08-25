# Copilot telemetry — Phase 1a / 1b / Option B

**Product:** SentryyIQ  
**Component:** Window metrics and agent alert telemetry APIs  
**Purpose:** Bounded Copilot fetches for Salveris V1.3. Do not return the full
`payload_json` array in one hop.  
**Author:** SentryyIQ / Salveris Engineering (Aug 2026)

**Salveris parent:** `Salveris-Platform/docs/design/live_data_incident_context_v1_3.md` §4  
**API sketch (historical Option B `/telemetry/*`):** Salveris
`docs/design/sentryyiq_investigation_api_sketch.md` — those routes remain
**design-only**. Production Copilot uses the agent/window routes below.

---

## 1. Why this exists

`window_metrics.payload_json` is a JSONB **array of records** (median thousands of
rows). List/detail routes that load the whole array break Copilot latency and
prompt size. Dashboard list routes already **defer** both `payload_json` and
`payload_summary`.

Agreed Copilot hops:

| Hop | Route | Returns | Does not return |
| --- | --- | --- | --- |
| **1a** | `GET /window-metrics/{metric_id}` | Window **scalars** (scores, counts, bounds) | `payload_json`, `payload_summary` (deferred) |
| **1b** | `GET /window-metrics/{metric_id}/summary` **or** `GET /agent/alerts/telemetry_summary/{ref}` | Stored `payload_summary` **as-is** plus **SQL aggregates** of `payload_json` | Raw record array |
| **B** | `GET /agent/alerts/raw_data/{ref}?skip=&limit=` | One **page** of array elements | Full array; no `too_large` when paging |

`GET /window-metrics/details/{metric_id}` stays for Dashboard forensic UI only.
**Salveris Copilot must not call it.**

---

## 2. Phase 1a — scalars (existing)

`GET /window-metrics/{metric_id}` uses:

```text
.options(defer(WindowMetrics.payload_json))
.options(defer(WindowMetrics.payload_summary))
```

Use this when Salveris already has `window_metric_id` (from the alert join) and
only needs EWMA / CUSUM / latency / CPU / `record_count` columns.

Alert `final_score` remains on `GET /agent/alerts/details/{ref}` (alerts table).
Ticket field `assignee` is the **current assignee** (not assignment history).

---

## 3. Phase 1b — summary without raw records (new)

### 3.1 `GET /window-metrics/{metric_id}/summary`

**Auth:** same as other window-metrics reads.

**Behavior:**

1. Load `payload_summary` from the column (as stored).
2. Compute a **SQL rollup** of `payload_json` with `jsonb_array_elements` +
   `GROUP BY` (top `error_code`, `client_id`, `machine_id`, `region`, array
   length) plus a **pattern** block (first host/client, spike vs gradual vs
   continuous vs widespread, peak time slice). Never load the full array into
   the API process.
3. Return both `payload_summary` and `sql_rollup` in one JSON object. If they
   disagree, both are returned; Salveris must not invent a third score.
4. When `pattern.recommended_raw_fetch.scope` is `peak_bucket` or `late_window`,
   Option B should pass those timestamps as `time_from` / `time_to` so the first
   raw page is targeted. `whole_window` means page from the start of observed
   timestamps (or omit filters).

**Response `200` (shape):**

```json
{
  "window_metric_id": 108,
  "window_start": "2026-06-26T10:00:00",
  "window_end": "2026-06-26T10:05:00",
  "payload_summary": {},
  "sql_rollup": {
    "record_count": 42877,
    "top_errors": [{"error_code": "ERR-307", "count": 812}],
    "top_clients": [{"client_id": "CUST-100483", "count": 401}],
    "top_hosts": [{"machine_id": "DEV-MAC-0149A5", "count": 188}],
    "regions": [{"region": "us-east-1", "count": 1200}],
    "pattern": {
      "primary": "spike",
      "labels": ["spike", "widespread"],
      "first_problem_at": "2026-06-26T10:01:12+00:00",
      "first_host": "DEV-MAC-0149A5",
      "first_client": "CUST-100483",
      "problem_record_count": 1204,
      "distinct_problem_hosts": 4,
      "distinct_problem_clients": 5,
      "recommended_raw_fetch": {
        "scope": "peak_bucket",
        "time_from": "2026-06-26T10:03:00+00:00",
        "time_to": "2026-06-26T10:04:15+00:00"
      }
    }
  }
}
```

**Pattern heuristics (from SQL counts only):**

| `primary` | Meaning | Typical Option B target |
| --- | --- | --- |
| `spike` | ≥50% of problem rows in one of four equal time buckets | That bucket (`peak_bucket`) |
| `gradual` | Problem counts rise across buckets | Last bucket (`late_window`) |
| `continuous` | Problems in ≥3 buckets, no single bucket ≥50% | Whole observed span |
| `widespread` | ≥3 problem hosts or clients (may combine with others) | Whole span unless also `spike` |
| `insufficient` | No problem rows detected | No time filter |

A problem row is `is_anomaly` true, `status` ERROR/FAILED, or a non-empty
`error_code`. Classification is a **heuristic**, not a confirmed root cause.
```

**Errors:** `404` if the window row is missing.

### 3.2 `GET /agent/alerts/telemetry_summary/{ind_details}`

Same body as 3.1, plus `alert_id`. Path token extraction matches other agent
alert routes: last `\d+` group → `alerts.id`. Join
`alerts.window_metric_id` → `window_metrics.id`.

Salveris `LiveFetchKind.telemetry_summary` maps here when the spec has
`alert_id`. When only `window_metric_id` is known, Salveris uses 3.1.

---

## 4. Option B — paged raw records (existing route, new CRUD)

### 4.1 `GET /agent/alerts/raw_data/{ind_details}`

Query parameters:

| Param | Default | Max | Notes |
| --- | --- | --- | --- |
| `skip` | `0` | — | Offset into the JSONB **array**, not ORM rows |
| `limit` | omitted | **50** | When omitted, keep **legacy** behaviour. When present, **always page**. |
| `time_from` | omitted | — | Optional ISO lower bound from 1b `recommended_raw_fetch` |
| `time_to` | omitted | — | Optional ISO upper bound |

Salveris always sends `limit` (default **30**, cap **50**).

**Paging SQL (required):** `jsonb_array_elements(payload_json) … OFFSET skip LIMIT limit`.  
SQLAlchemy `.offset().limit()` on `WindowMetrics` pages **window rows**, not
records inside the array. Do not use that for Option B.

**Paged response `200`:**

```json
{
  "status": "success",
  "alert_id": 42,
  "record_count": 42877,
  "skip": 0,
  "limit": 30,
  "payload_json": []
}
```

`payload_json` here is **one page** (list of record objects), not the full column.

**Legacy (no `limit` query param):** unchanged for Telegram/n8n:
`too_large` when `jsonb_array_length > 2500`, else full array.

---

## 5. Users and assignment (unchanged routes)

| Route | Copilot use |
| --- | --- |
| `GET /agent/users` | Active `user_master` directory (assign picker). **Exists.** |
| `GET /agent/incidents/assignments/{ref}` | Assignment **history** |
| `GET /agent/incidents/details/{ref}` | Incident including **current** `assignee` |

There is no `GET /agent/users/{id}`.

---

## 6. Salveris mapping

| `LiveFetchKind` | SentryyIQ call |
| --- | --- |
| `window_metric_detail` | `GET /window-metrics/{metric_id}` (1a) |
| `telemetry_summary` | `GET /agent/alerts/telemetry_summary/{alert_id}` or `/window-metrics/{id}/summary` (1b) |
| `telemetry_records_page` | `GET /agent/alerts/raw_data/{alert_id}?skip=&limit=` (B) |
| `users_list` | `GET /agent/users` |
| `assignment_history` | `GET /agent/incidents/assignments/{ref}` |
| `dashboard_summary` | `GET /dashboard/summary` |

`GET /telemetry/summary` and `GET /telemetry/records` are **not** required for
this Copilot path.
