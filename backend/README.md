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

## Scope

This folder currently contains only the initial application structure and a basic health check endpoint.
