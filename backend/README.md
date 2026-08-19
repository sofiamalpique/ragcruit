# Backend

Minimal FastAPI service for `ragcruit`.

## Local development with uv

From the `backend/` directory:

```bash
uv python install 3.12
uv sync --python 3.12
```

`uv sync` will create or update the local virtual environment and generate `uv.lock` if it does not exist yet. The lockfile should be created by running `uv` commands, not written by hand.

## Run the app

```bash
uv run uvicorn app.main:app --reload
```

## Run tests

```bash
uv run pytest
```

## Database URL

If `DATABASE_URL` is not set, the backend uses the local SQLite fallback automatically.

See the root `.env.example` for a minimal local PostgreSQL example.

The backend uses `psycopg[binary]` for local development, so a separate local `libpq` installation is not required.
The `pgvector` Python package is also installed, so SQLAlchemy vector columns can be added next without more driver setup.
Embeddings are generated locally with `sentence-transformers`. The default model is `sentence-transformers/all-MiniLM-L6-v2`, and you can override it with `EMBEDDING_MODEL_NAME`.

For PostgreSQL, use a SQLAlchemy URL like:

```bash
export DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/ragcruit"
```

## Scope

This backend currently exposes:

- `GET /health`
- `POST /candidates`
- `POST /candidates/search`
- `POST /jobs`
- `GET /jobs`
- `GET /jobs/{job_posting_id}`
- `POST /jobs/{job_posting_id}/match`

The SQLite fallback is useful for basic local development, but semantic search and job matching require PostgreSQL with pgvector-backed embeddings.
