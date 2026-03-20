# Ragcruit

AI recruiting prototype for candidate ingestion, local embeddings generation, and semantic search.

## Project Overview

Ragcruit is an early-stage recruiting project built around a FastAPI backend and a minimal React frontend. The current repository demonstrates a concrete end-to-end flow:

1. create a candidate record
2. generate a local embedding with `sentence-transformers`
3. persist that vector in PostgreSQL with pgvector
4. run semantic candidate search
5. view results in the frontend

This is not yet a complete hiring platform. It is a focused foundation for candidate storage and similarity-based retrieval.

## What Currently Works

- FastAPI backend with candidate creation and semantic search endpoints
- PostgreSQL 16 + pgvector local stack through Docker Compose
- Local embeddings generation using `sentence-transformers/all-MiniLM-L6-v2`
- Candidate embeddings persisted on create when running against PostgreSQL
- Semantic search through `POST /candidates/search`
- Minimal React + Vite + TypeScript frontend for candidate creation, semantic search, and result display

## Architecture / Repo Structure

- [backend/](backend/): FastAPI application, candidate schemas/models/services, database setup, and tests
- [frontend/](frontend/): React + Vite + TypeScript single-page frontend
- [docker-compose.yml](docker-compose.yml): local PostgreSQL + backend stack
- [docker/postgres/init/01-enable-pgvector.sql](docker/postgres/init/01-enable-pgvector.sql): enables the `vector` extension on fresh local database initialization
- [docs/](docs/): reserved for additional project documentation

## Tech Stack

- Python 3.12
- FastAPI
- SQLAlchemy 2.x
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

### Backend with Docker Compose

From the repository root:

```bash
docker compose up --build
```

This starts:

- PostgreSQL with pgvector on `localhost:5432`
- the FastAPI backend on `http://localhost:8000`

On a fresh volume, PostgreSQL enables the `vector` extension automatically before the backend creates tables.

### Frontend with npm

From the `frontend/` directory:

```bash
npm install
npm run dev
```

The Vite development server runs separately from Docker Compose. During local development, the frontend proxies `/candidates` requests to `http://localhost:8000`.

## Current API Capabilities

- `GET /health`
  Basic service health check.
- `POST /candidates`
  Creates a candidate, generates a local embedding when PostgreSQL/pgvector is active, and persists the stored vector with the candidate record.
- `POST /candidates/search`
  Accepts raw query text, generates a local embedding for that query, and returns candidates ordered by vector similarity.

## Current Limitations

- `skills` are accepted on candidate creation input but are not stored yet
- search is similarity-based retrieval only; there is no separate advanced ranking layer yet
- there is no authentication or user management
- there are no migrations yet; schema setup still relies on SQLAlchemy metadata creation for the current local workflow
- the semantic search path is intentionally PostgreSQL + pgvector dependent

## Future Improvements

- add schema migrations
- persist and manage candidate skills cleanly
- expand the candidate API beyond the current create and search flow
- add a more explicit ranking layer on top of similarity retrieval
- grow the frontend beyond the current single-page prototype
