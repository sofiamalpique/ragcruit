# ragcruit
AI Hiring Copilot for CV Search, Matching and Ranking

## Local Stack

Start the local backend stack from the repository root:

```bash
docker compose up --build
```

The defaults in `docker-compose.yml` match the `DATABASE_URL` value in `.env.example`.
On a fresh Postgres volume, Compose now enables the `vector` extension automatically during database initialization.
The backend is available at `http://localhost:8000`.
