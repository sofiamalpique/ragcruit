# Ragcruit

AI recruiting prototype for candidate ingestion, local embeddings generation, semantic search, and early job matching.

## Project Overview

Ragcruit is an early-stage recruiting project built around a FastAPI backend, PostgreSQL + pgvector, and a minimal React frontend. The current repository demonstrates a concrete local flow:

1. create a candidate
2. generate a local embedding with `sentence-transformers`
3. persist that vector in PostgreSQL with pgvector
4. create a job posting and persist its embedding
5. run semantic candidate search
6. run candidate-to-job matching
7. view the results in the frontend

This is not yet a complete hiring platform. It is a focused prototype for candidate storage, job posting storage, and similarity-based retrieval on top of local embeddings.

## What Currently Works

- FastAPI backend with candidate creation, semantic search, job posting creation/listing/read, and candidate-to-job matching endpoints
- PostgreSQL 16 + pgvector local stack through Docker Compose
- Local embeddings generation using `sentence-transformers/all-MiniLM-L6-v2`
- Candidate embeddings persisted on create when running against PostgreSQL
- Job posting embeddings persisted on create when running against PostgreSQL
- Semantic candidate search through `POST /candidates/search`
- Candidate-to-job matching through `POST /jobs/{job_posting_id}/match`
- Minimal React + Vite + TypeScript frontend for candidate creation, job posting creation, semantic search, matching, and result display
- One-command local web stack through Docker Compose
- Alembic-backed database migrations for the PostgreSQL container path

## Architecture / Repo Structure

- [backend/](backend/): FastAPI application, candidate schemas/models/services, Alembic migrations, and tests
- [frontend/](frontend/): React + Vite + TypeScript single-page frontend
- [docker-compose.yml](docker-compose.yml): local PostgreSQL + backend + frontend stack
- [docker/postgres/init/01-enable-pgvector.sql](docker/postgres/init/01-enable-pgvector.sql): enables the `vector` extension on fresh local database initialization
- [docs/](docs/): reserved for additional project documentation

## Tech Stack

- Python 3.12
- FastAPI
- SQLAlchemy 2.x
- Alembic
- PostgreSQL 16
- pgvector
- psycopg 3
- `sentence-transformers`
- `uv` for Python dependency management
- React
- Vite
- TypeScript
- Docker Compose

## Local Setup

### One-command local web stack

From the repository root:

```bash
docker compose up --build
```

This starts:

- PostgreSQL with pgvector on `localhost:5432`
- the FastAPI backend on `http://localhost:8000`
- the frontend on `http://localhost:5173`

On a fresh volume, PostgreSQL enables the `vector` extension automatically before Alembic runs the current schema migrations.

### Frontend with npm

If you want to run the frontend outside Docker:

```bash
cd frontend
npm install
npm run dev
```

The Vite development server proxies `/candidates` requests to the backend.

## Current API Capabilities

- `GET /health`
  Basic service health check.
- `POST /candidates`
  Creates a candidate, generates a local embedding when PostgreSQL/pgvector is active, and persists the stored vector with the candidate record.
- `POST /candidates/search`
  Accepts raw query text, generates a local embedding for that query, and returns candidates ordered by vector similarity.
- `POST /jobs`
  Creates a job posting, generates a local embedding when PostgreSQL/pgvector is active, and persists the job record.
- `GET /jobs`
  Lists persisted job postings in reverse chronological order.
- `GET /jobs/{job_posting_id}`
  Returns a single job posting by id.
- `POST /jobs/{job_posting_id}/match`
  Uses the persisted job embedding to rank candidates by similarity, then adds lightweight relevance adjustments for experience and location matches.

## Current Limitations

- `skills` are accepted on candidate creation input but are not stored yet
- job postings currently support create/list/get only; there is no update/delete flow yet
- there is no shortlist workflow or recruiter workflow state yet
- there is no authentication or user management
- semantic candidate search and candidate-to-job matching are intentionally PostgreSQL + pgvector dependent
- the frontend is still a small single-page demo surface, not a full product UI

## Future Improvements

- persist and manage candidate skills cleanly
- add job posting update/delete flows and a fuller posting lifecycle
- add a more explicit ranking layer beyond the current similarity + lightweight heuristics
- introduce shortlist and recruiter workflow state
- add CV upload and parse-to-draft ingestion
- grow the frontend beyond the current single-page prototype
