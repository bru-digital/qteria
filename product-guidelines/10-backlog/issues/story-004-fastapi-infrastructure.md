# [STORY-004] FastAPI Infrastructure & Health Checks

**Type**: Story
**Epic**: EPIC-01 (Database & Infrastructure)
**Journey Step**: Foundation
**Priority**: P0 (Blocks All APIs)
**RICE Score**: 133 (R:100 × I:2 × C:100% ÷ E:1.5)

---

## User Value

**Job-to-Be-Done**: When developers build API endpoints, they need a working FastAPI application with database connectivity, so they can quickly add features without infrastructure setup overhead.

**Value Delivered**: Production-ready API infrastructure with health checks, database connection pooling, CORS, error handling, and deployment to Railway.

**Success Metric**: FastAPI health check returns 200 OK with <50ms response time.

---

## Acceptance Criteria

- [ ] FastAPI application initialized with proper project structure
- [ ] SQLAlchemy database connection pool configured
- [ ] Health check endpoint (`GET /health`) returns 200 OK
- [ ] Health check includes database connectivity test
- [ ] CORS configured for frontend (localhost:3000 for development)
- [ ] Global error handling middleware (500 errors return JSON)
- [ ] Environment variables for configuration (DATABASE_URL, CORS_ORIGINS)
- [ ] Application deployed to Railway
- [ ] Logs structured (JSON format for production)
- [ ] API documentation auto-generated (FastAPI Swagger UI at `/docs`)

---

## Technical Approach

**Tech Stack Components Used**:

- Backend: FastAPI + Uvicorn (ASGI server)
- ORM: SQLAlchemy + asyncpg (async PostgreSQL driver)
- Deployment: Railway (backend hosting)
- Database: Vercel Postgres (connection via DATABASE_URL)

**Project Structure**:

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app initialization
│   ├── config.py            # Environment configuration
│   ├── database.py          # SQLAlchemy setup, connection pool
│   ├── models/              # SQLAlchemy models (from STORY-001 schema)
│   ├── api/
│   │   ├── __init__.py
│   │   └── health.py        # Health check endpoint
│   └── middleware/
│       └── error_handler.py # Global error handling
├── alembic/                 # Migrations (from STORY-002)
├── scripts/
│   └── seed_data.py         # Seed data (from STORY-003)
├── requirements.txt
└── Dockerfile               # Railway deployment
```

**FastAPI Application Setup** (`app/main.py`):

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine
from app.api import health

app = FastAPI(
    title="Qteria API",
    description="AI-powered certification document validation",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health.router)

@app.on_event("startup")
async def startup():
    # Test database connection
    await engine.connect()

@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()
```

**Health Check Endpoint** (`app/api/health.py`):

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    # Test database connectivity
    await db.execute("SELECT 1")
    return {
        "status": "healthy",
        "database": "connected",
        "version": "1.0.0"
    }
```

**Database Connection Pool** (`app/database.py`):

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True  # Test connections before using
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

**Environment Configuration** (`app/config.py`):

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()
```

**Railway Deployment**:

- Add `Procfile`: `web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Configure environment variables in Railway dashboard (DATABASE_URL, CORS_ORIGINS)
- Connect GitHub repo for auto-deployment

---

## Dependencies

- **Blocked By**:
  - STORY-001 (Database Schema) - need schema for SQLAlchemy models
  - STORY-002 (Migrations) - need migrations to apply schema
- **Blocks**: ALL API endpoints - no features can be built without FastAPI infrastructure

---

## Estimation

**Effort**: 1.5 person-days

**Breakdown**:

- FastAPI setup: 0.5 days (app initialization, project structure)
- Database connection pool: 0.25 days (SQLAlchemy async setup)
- Health check endpoint: 0.25 days (endpoint + database test)
- CORS + middleware: 0.25 days (error handling, logging)
- Railway deployment: 0.25 days (Dockerfile, Procfile, env vars)

---

## Definition of Done

- [ ] FastAPI application runs locally (`uvicorn app.main:app --reload`)
- [ ] Health check endpoint returns 200 OK at `GET /health`
- [ ] Health check tests database connectivity (fails if DB unreachable)
- [ ] CORS allows requests from localhost:3000 (frontend)
- [ ] Global error handler catches 500 errors, returns JSON
- [ ] Environment variables loaded from .env file
- [ ] SQLAlchemy connection pool configured (max 20 connections)
- [ ] Application deployed to Railway
- [ ] Railway deployment accessible via public URL
- [ ] API documentation accessible at `/docs` (Swagger UI)
- [ ] Logs show structured JSON output (not plain text)
- [ ] Code reviewed and merged to main

---

## Testing Requirements

**Functional Tests**:

- [ ] `GET /health` returns 200 OK with `{"status": "healthy", "database": "connected"}`
- [ ] `GET /health` returns 503 Service Unavailable if database unreachable
- [ ] CORS headers present in response (Access-Control-Allow-Origin)
- [ ] Request from disallowed origin → CORS error
- [ ] Unhandled exception → returns 500 with JSON error message (not HTML)

**Performance Tests**:

- [ ] Health check response time <50ms (P95)
- [ ] Database connection pool handles 20 concurrent requests
- [ ] Connection pool doesn't exhaust under load (max_overflow works)

**Integration Tests**:

- [ ] Deploy to Railway → health check accessible via public URL
- [ ] Environment variables loaded correctly in Railway
- [ ] Database connection works with Vercel Postgres (production DB)

---

## Risks & Mitigations

**Risk**: Connection pool exhausted under high load

- **Mitigation**: Set pool_size=20, max_overflow=10, add connection pool monitoring

**Risk**: Health check passes but database queries fail

- **Mitigation**: Health check executes actual query (`SELECT 1`), not just connection test

**Risk**: Railway deployment fails (missing dependencies)

- **Mitigation**: Test Dockerfile locally, pin all dependencies in requirements.txt

**Risk**: CORS misconfigured, frontend cannot connect

- **Mitigation**: Test CORS with curl from frontend URL, allow credentials for cookies

---

## Notes

- This completes the foundation (EPIC-01) - all future stories build on this infrastructure
- After completing this story, EPIC-01 is DONE → proceed to EPIC-02 (Authentication)
- Keep FastAPI app simple initially (no auth yet) - add authentication in STORY-005
- Use async SQLAlchemy for better performance (supports concurrent requests)
- Railway auto-deploys on git push → set up CI/CD in STORY-041
- Monitor Railway metrics (response time, memory usage) to optimize connection pool
