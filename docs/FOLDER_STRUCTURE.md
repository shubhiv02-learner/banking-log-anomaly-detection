# Project folder structure

SentryyIQ – banking log anomaly detection & observability. Layout below reflects the repository as inspected (excluding `node_modules/`, `.venv/`, `__pycache__/`, `dist/`, `.vercel/`, and similar generated/cache dirs).

## Root

- `backend/` — FastAPI app: DB models, CRUD, and notifications
- `frontend/` — Vite/React (TanStack) dashboard UI and Vercel deploy config
- `consumer/` — Kafka (or stream) consumer that pulls logs for detection
- `producer/` — Log/telemetry producer that publishes banking events
- `src/` — Core ML/detection library (ensemble, features, enrichment, metrics)
- `scripts/` — Data generation and preprocessing utilities
- `notebooks/` — Exploratory notebooks plus mirrored data/models/outputs
- `docs/` — Architecture docs, guides, presentations, and screen recordings
- `data/` — Raw and processed banking log datasets
- `models/` — Trained joblib/pkl models, scalers, encoders, ensemble configs
- `n8n/` — n8n workflow exports (incident notification & assignment)
- `outputs/` — Analysis artifacts (charts, CSVs, PDF reports)
- `reports/` — Generated anomaly report PDFs
- `logs/` — Runtime application logs (consumer, producer, uvicorn)
- `temp/` — Scratch/working copies of data and experimental scripts
- `config.py` — Root project configuration
- `logging_config.py` — Shared logging setup
- `requirements.txt` — Python dependencies
- `README.md` — Project overview and architecture

## Deeper structure

### Backend

```
backend/
  main.py                 # FastAPI entrypoint
  database.py / db_models.py / crud.py / schemas.py
  db_services.py / notification.py
  config.py / constants.py / logging_config.py
  create_tables.py
  requirements.txt
  data/
  logs/
  test/
```

### Frontend (major folders only)

```
frontend/
  src/
    components/
      dashboard/          # KPI cards, charts, health tiles, dialogs
      layout/             # App shell, sidebar, topbar
      theme/              # Theme provider & toggle
      ui/                 # Shared UI primitives (shadcn-style)
    hooks/
    lib/
      api/                # Client, types, placeholder/example API helpers
    routes/               # index, alerts, analytics, incidents
    router.tsx / routeTree.gen.ts / start.ts / server.ts
    styles.css
  scripts/
  package.json / vite.config.ts / tsconfig.json / vercel.json
  DEPLOY_VERCEL.md
```

### Stream pipeline

```
producer/
  producer.py

consumer/
  consumer.py
```

### Detection & data tooling

```
src/
  detector.py
  ensemble.py
  enrichment.py
  feature_engineering.py
  stream_metrics.py
  generate_analysis.py
  generate_banking_logs_metrics.py
  run_logs.py
  test_detector.py / test.py

scripts/
  generate_banking_logs.py
  call_generate_banking_logs.py
  data_generation.py
  data_process.py

data/
  raw/
  processed/
  banking_logs.csv / banking_logs.json / …
```

### Notebooks (brief)

```
notebooks/
  *.ipynb                 # SentinelIQ exploration / model / gendata notebooks
  data/                   # Notebook-local raw & processed copies
  models/                 # Local model artifacts used in notebooks
  src/ / scripts/         # Notebook-adjacent helpers
  outputs/ / reports/ / visualizations/
```

### Docs, automation & artifacts

```
docs/
  FOLDER_STRUCTURE.md     # This file
  LOGGING.md / enhancements.md
  *.docx / *.pdf / *.pptm / *.mp4   # Guides, blueprints, demos

n8n/
  Critical Incident Notification.json
  incident_assignment (4).json
  SentryyIQ_HackathonV0.9.json

models/                   # Isolation Forest, OCSVM, LOF, scalers, encoders
outputs/
  visualizations/
reports/
logs/
temp/
```

## Intentionally omitted

- `.git/`, `.venv/`, `.cursor/`, `.vscode/`
- `node_modules/`, `frontend/dist/`, `frontend/.vercel/`, `frontend/.tanstack/`
- `__pycache__/` and large binary contents under `models/` / `data/` (dirs listed; files not enumerated)
