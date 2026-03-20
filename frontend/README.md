# Frontend

Minimal React frontend for the current Ragcruit backend flow.

## Stack

- React
- Vite
- TypeScript
- `fetch` for API calls

## What It Does

This frontend demonstrates the current backend capabilities in one small single-page app:

- create a candidate
- run semantic candidate search
- render search results with similarity scores

It is intentionally minimal and is meant to exercise the current backend, not to represent a full product UI.

## Run Locally

From the `frontend/` directory:

```bash
npm install
npm run dev
```

The app expects the backend to be available at `http://localhost:8000`. In local Vite development, `/candidates` requests are proxied to that backend.

## Backend Endpoints Used

- `POST /candidates`
- `POST /candidates/search`

## Current Scope

The frontend currently covers:

- candidate creation form
- semantic search form
- search results display

It does not include routing, authentication, global state management, or any advanced UI framework.
