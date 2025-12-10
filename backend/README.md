# Backend Setup - Phase 2 Todo Application

This is the backend for the full-stack todo application with secure authentication, persistent storage, and REST APIs.

## Tech Stack
- Python 3.13+
- FastAPI
- SQLModel
- Neon PostgreSQL
- Better Auth (JWT)

## Setup Instructions

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Create Virtual Environment with UV
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
uv pip install -e .
```

### 4. Environment Configuration
Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

Update the `.env` file with your actual configuration:
- `DATABASE_URL`: Your Neon PostgreSQL connection string
- `BETTER_AUTH_SECRET`: A secure secret key for JWT signing
- `API_HOST` and `API_PORT`: Server configuration

### 5. Run Database Migrations
```bash
# Create tables in Neon database
python scripts/migrate.py
```

### 6. Start Backend Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000

**API Documentation** (auto-generated):
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Common Commands
```bash
# Run tests
pytest

# Format code
black .

# Lint code
ruff check .

# Type check
mypy .
```

## Project Structure
- `main.py`: FastAPI app initialization and router mounting
- `models.py`: SQLModel Task model
- `db.py`: Database engine and session management
- `middleware.py`: JWT authentication middleware
- `routes/tasks.py`: Task CRUD endpoints
- `schemas.py`: Pydantic request/response models
- `config.py`: Configuration (env vars, secrets)
- `scripts/migrate.py`: Database migration script