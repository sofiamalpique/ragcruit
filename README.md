# ragcruit
AI Hiring Copilot for CV Search, Matching and Ranking

## Local Stack

Start the local backend stack from the repository root:

```bash
docker compose up --build
```

The defaults in `docker-compose.yml` match the `DATABASE_URL` value in `.env.example`.
The local database image now includes pgvector, so the extension can be enabled in the database when the backend is ready to use it.
The backend is available at `http://localhost:8000`.
