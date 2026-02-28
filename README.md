# Toronto Water Break Watch (MVP Backend)

FastAPI + Postgres/PostGIS backend for clustering urban water break signals into incidents.

## Features
- Signal ingestion model for RSS/Reddit items.
- Incident clustering based on **300m radius** and **2-hour time window**.
- Toronto-only support through boundary polygon storage in PostGIS.
- Rules-based incident confidence scoring with explainable JSON breakdown.
- REST API for health, incident querying, incident details, and feedback.
- Celery placeholder jobs for RSS and Reddit ingest.

## Tech Stack
- Python 3.12
- FastAPI
- SQLAlchemy 2.x
- Postgres + PostGIS
- Alembic
- Celery + Redis
- Docker Compose

## Local Development

### 1) Start services
```bash
docker compose up --build -d
```

### 2) Run migrations
```bash
docker compose exec api alembic upgrade head
```

### 3) Run API
API is available at `http://localhost:8000`.

### 4) Run tests
```bash
docker compose exec api pytest
```

## API Endpoints
- `GET /health`
- `GET /incidents?since=...&min_confidence=...&bbox=minLon,minLat,maxLon,maxLat`
- `GET /incidents/{id}`
- `POST /feedback`

## Notes
- Reddit task intentionally exposes only a placeholder interface; credentials must be passed via environment variables and are not committed.
- A Toronto boundary polygon should be inserted into `boundaries` table with name matching `TORONTO_BOUNDARY_NAME`.
