# Backend Guidelines – FastAPI App (hackathon-todo)

## Stack
- FastAPI
- SQLModel
- Neon PostgreSQL
- JWT auth (Better Auth tokens)
- Uvicorn for dev server

## Target Structure
- `main.py`          – FastAPI app, router mounting
- `models.py`        – SQLModel models (Task, etc.)
- `schemas.py`       – Pydantic request/response models
- `db.py`            – DB engine + session management
- `routes/tasks.py`  – Task CRUD endpoints
- `auth.py`          – JWT validation utilities/middleware

## API Conventions
- All endpoints under `/api/`.
- Implement endpoints as specified in:
  - @specs/api/rest-endpoints.md
  - @specs/api/auth-flow.md
- All responses are JSON.
- Use Pydantic models for request/response bodies.
- Use `HTTPException` with proper status codes for errors.

## Database
- Use SQLModel models matching:
  - @specs/database/schema.md
- DB connection URL comes from env var `DATABASE_URL` (Neon PostgreSQL).
- Use alembic or simple migration strategy as needed (later phases can refine).

## Auth & Authorization
- Every request must include a JWT in `Authorization: Bearer <token>`.
- Use shared secret `BETTER_AUTH_SECRET` to verify tokens.
- Extract `user_id` from JWT and ensure:
  - Path user_id == token user_id
  - Queries are always filtered by `user_id`.

## Running Dev Server (expected)
- `uvicorn main:app --reload --port 8000`
