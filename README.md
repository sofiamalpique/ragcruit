# Ragcruit

AI Hiring Copilot for CV search, matching, and ranking.

## What Ragcruit Is

Ragcruit is an early-stage backend-first project for building a hiring workflow around candidate ingestion, storage, semantic matching, and ranking.

At the moment, the repository focuses on the backend and database foundation needed for that product direction. It is not yet a complete hiring platform.

## Current Status

- FastAPI backend is running locally.
- Candidate domain foundations are in place: schemas, SQLAlchemy model, mapper, and a first create endpoint.
- PostgreSQL is supported through `DATABASE_URL`.
- Local Docker Compose runs the backend together with PostgreSQL and pgvector.
- A pgvector-ready model field exists as groundwork for future embeddings support.
- Embeddings generation, vector retrieval, ranking logic, authentication, and frontend product flows are not implemented yet.

## Tech Stack

- Python 3.12
- FastAPI
- SQLAlchemy 2.x
- PostgreSQL 16
- pgvector
- psycopg 3
- `uv` for Python dependency management
- Docker Compose for local stack orchestration

## Architecture Overview

- [backend/](backend/): FastAPI application, candidate domain code, database setup, and tests
- [docker-compose.yml](docker-compose.yml): local backend + PostgreSQL stack
- [docker/postgres/init/01-enable-pgvector.sql](docker/postgres/init/01-enable-pgvector.sql): Postgres init hook that enables the `vector` extension on a fresh database
- [frontend/](frontend/): reserved for future frontend work
- [docs/](docs/): reserved for project documentation

## Local Development

The simplest way to run the current backend stack is from the repository root:

```bash
docker compose up --build
```

This starts:

- PostgreSQL with pgvector on `localhost:5432`
- the FastAPI backend on `http://localhost:8000`

For a fresh database volume, the local Postgres container enables the `vector` extension automatically during initialization.

For host-side tools, [.env.example](.env.example) contains the matching local PostgreSQL URL:

```bash
postgresql+psycopg://postgres:postgres@localhost:5432/ragcruit
```

Inside Docker Compose, the backend uses the internal Postgres service hostname instead of `localhost`.

For the non-Docker backend workflow, see [backend/README.md](backend/README.md).

## What Currently Works

- `GET /health` responds successfully
- `POST /candidates` accepts candidate input and persists core candidate fields to the database
- local PostgreSQL startup works with pgvector enabled on a fresh volume
- the candidate model is prepared for a future embedding column under PostgreSQL

Current limitations:

- candidate `skills` are accepted on input but are not stored yet
- embeddings are not generated or written yet
- vector search and retrieval are not implemented yet
- there is no frontend application yet

## What Is Planned Next

- add proper schema migration support
- persist and manage candidate skills cleanly
- implement embeddings generation for candidates
- enable pgvector-backed similarity search and ranking
- expand the candidate API beyond the initial create flow
- start the first frontend experience on top of the current backend foundation
