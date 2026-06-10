# Island Delta

Basic project skeleton for the "Island Delta" emotion-map application.

This repository intentionally contains only the foundation needed for later work:

- `frontend/`: Vue 3 + Vite + TypeScript application shell.
- `backend/`: Spring Boot business service shell.
- `nlp-service/`: FastAPI NLP and agent service shell.
- `database/`: GaussDB/openGauss SQL and seed placeholders.
- `deploy/`: deployment placeholders.
- `scripts/`: project helper script placeholders.
- `docs/`: project requirements and task documents.

No product task is implemented in this skeleton. Feature work should be added under the matching module according to the task documents in `docs/`.

## Local Development Targets

Planned commands after dependencies are installed:

```text
cd frontend && npm run dev
cd backend && mvn spring-boot:run
cd nlp-service && uvicorn app.main:app --reload
```

Database initialization scripts should be added under `database/` when task three starts.
