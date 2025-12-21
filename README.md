# Qteria

**AI-driven document pre-assessment for TIC industry**

Fast, evidence-based validation that saves time and reduces certification back-and-forth.

---

## Quick Start

### Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** 20+ ([Download](https://nodejs.org/))
- **Python** 3.11+ ([Download](https://www.python.org/downloads/))
- **Docker** & **Docker Compose** ([Download](https://www.docker.com/products/docker-desktop))
- **Git** ([Download](https://git-scm.com/downloads))

### Setup (5 Steps to Running)

#### 1. Clone the repository

```bash
git clone https://github.com/your-org/qteria.git
cd qteria
```

#### 2. Set up environment variables

```bash
# Copy environment template
cp .env.template .env

# Edit .env with your local values
# Required:
# - NEXTAUTH_SECRET (generate with: openssl rand -base64 32)
# - JWT_SECRET (generate with: openssl rand -base64 32)
# - ANTHROPIC_API_KEY (get from https://console.anthropic.com/)
```

#### 3. Start local services (PostgreSQL + Redis)

```bash
# Start database and cache
npm run docker:up

# Verify services are running
docker ps
# You should see: qteria-postgres, qteria-redis, qteria-pgadmin
```

#### 4. Install dependencies

```bash
# Install frontend dependencies
npm install

# Install backend dependencies
cd apps/api
pip install -r requirements-dev.txt
cd ../..
```

#### 5. Install pre-commit hooks (Recommended)

```bash
# Install pre-commit (one-time setup)
pip install pre-commit

# Or with pipx (recommended)
pipx install pre-commit

# Install git hooks
pre-commit install

# Optional: Run on all files to verify setup
pre-commit run --all-files
```

**What pre-commit does:**

- **Black**: Automatically formats Python code
- **Ruff**: Lints Python code and auto-fixes issues
- **Prettier**: Formats JavaScript, TypeScript, JSON, Markdown, YAML
- **File checks**: Removes trailing whitespace, fixes line endings, validates YAML/JSON/TOML

Pre-commit hooks run automatically when you `git commit`. To bypass (use sparingly): `git commit --no-verify`

#### 6. Run database migrations

```bash
# Apply database schema
npm run db:migrate
```

#### 7. Seed development data (Optional)

```bash
# Populate database with sample data (recommended for development)
cd apps/api
source venv/bin/activate  # On Windows: venv\Scripts\activate
python scripts/seed_data.py
```

**What gets created:**

- 1 demo organization: "TÜV SÜD Demo"
- 2 users with different roles:
  - Process Manager: `process.manager@tuvsud-demo.com`
  - Project Handler: `project.handler@tuvsud-demo.com`
- 2 realistic workflows based on EU certification standards:
  - Machinery Directive 2006/42/EC (2 buckets, 6 criteria)
  - Medical Device Regulation (EU) 2017/745 (2 buckets, 4 criteria)

**Script options:**

```bash
python scripts/seed_data.py           # Idempotent - skips if data exists
python scripts/seed_data.py --reset   # Reset database and reseed
```

#### 8. Start development servers

```bash
# Terminal 1: Start frontend (Next.js)
npm run dev

# Terminal 2: Start backend (FastAPI)
npm run dev:api
```

#### 9. Open your browser

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs (FastAPI Swagger UI)
- **Database UI**: http://localhost:5050 (PgAdmin)
  - Email: `admin@qteria.local`
  - Password: `admin`

---

## Project Structure

```
qteria/
├── apps/
│   ├── web/                 # Next.js frontend (TypeScript)
│   │   ├── src/
│   │   │   ├── app/         # Next.js App Router pages
│   │   │   ├── components/  # React components
│   │   │   ├── lib/         # Utilities, API client
│   │   │   └── types/       # TypeScript types
│   │   ├── public/          # Static assets
│   │   └── package.json
│   │
│   └── api/                 # FastAPI backend (Python)
│       ├── app/
│       │   ├── main.py      # FastAPI app entry
│       │   ├── api/         # API endpoints (routers)
│       │   ├── models/      # SQLAlchemy models
│       │   ├── schemas/     # Pydantic schemas
│       │   ├── services/    # Business logic
│       │   ├── core/        # Config, security, dependencies
│       │   └── workers/     # Celery tasks
│       ├── alembic/         # Database migrations
│       ├── tests/           # Pytest tests
│       └── requirements.txt
│
├── packages/
│   └── types/               # Shared TypeScript types
│
├── docker-compose.yml       # Local dev services (PostgreSQL, Redis)
├── .env.template            # Environment variables template
├── .gitignore
├── package.json             # Root npm workspace config
└── README.md                # This file
```

---

## Available Scripts

### Root Level (Workspace)

```bash
# Development
npm run dev              # Start Next.js frontend dev server
npm run dev:api          # Start FastAPI backend dev server
npm run docker:up        # Start Docker services (PostgreSQL + Redis)
npm run docker:down      # Stop Docker services
npm run docker:logs      # View Docker logs

# Building
npm run build            # Build Next.js for production

# Testing
npm run test             # Run all tests (frontend + backend)
npm run lint             # Lint all code
npm run type-check       # TypeScript type checking
npm run format           # Format code with Prettier
npm run format:check     # Check code formatting

# Database
npm run db:migrate       # Run database migrations
npm run db:migrate:create "migration name"  # Create new migration
npm run db:reset         # Reset database (⚠️ destroys data)

# Code Quality (Pre-commit)
pre-commit install       # Install pre-commit hooks (one-time)
pre-commit run --all-files  # Run pre-commit on all files
pre-commit run           # Run pre-commit on staged files only
git commit --no-verify   # Bypass pre-commit hooks (use sparingly)
```

### Frontend (apps/web/)

```bash
cd apps/web
npm run dev              # Start dev server (localhost:3000)
npm run build            # Build for production
npm run start            # Start production server
npm run test             # Run Vitest unit tests
npm run test:watch       # Run tests in watch mode
npm run lint             # ESLint
npm run type-check       # TypeScript
```

### Backend (apps/api/)

```bash
cd apps/api

# Development
uvicorn app.main:app --reload --port 8000  # Start dev server
celery -A app.workers worker --loglevel=info  # Start Celery worker

# Testing
pytest                   # Run all tests
pytest --cov             # Run tests with coverage
pytest -v tests/unit     # Run unit tests only
pytest -v tests/integration  # Run integration tests only
pytest -m "not slow"     # Skip slow tests

# Code Quality
black .                  # Format code
ruff check .             # Lint code
mypy app                 # Type checking

# Database
alembic upgrade head     # Run migrations
alembic revision --autogenerate -m "description"  # Create migration
alembic downgrade -1     # Rollback one migration

# Seed Data
python scripts/seed_data.py        # Seed development data
python scripts/seed_data.py --reset  # Reset and reseed
```

---

## Tech Stack

### Frontend

- **Next.js 14+** (React 18, App Router)
- **TypeScript** (strict mode)
- **Tailwind CSS** (styling)
- **shadcn/ui** (component library)
- **Auth.js** (authentication)
- **React Query** (data fetching)
- **Zustand** (state management)

### Backend

- **FastAPI** (Python web framework)
- **SQLAlchemy 2.0** (ORM)
- **Alembic** (database migrations)
- **Pydantic v2** (data validation)
- **Celery** (background jobs)
- **Redis** (job queue + cache)
- **PyPDF2** + **pdfplumber** (PDF parsing)
- **Claude 3.5 Sonnet** (AI validation)

### Infrastructure

- **PostgreSQL 15** (database)
- **Redis 7** (cache + queue)
- **Vercel** (frontend hosting)
- **Railway** / **Render** (backend hosting)
- **Vercel Blob** (file storage)
- **GitHub Actions** (CI/CD)

---

## Development Workflow

### 1. Create a New Feature

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes, write tests
# ...

# Run tests locally
npm run test
npm run lint

# Commit changes
git add .
git commit -m "feat: add your feature description"

# Push to GitHub
git push origin feature/your-feature-name

# Open Pull Request on GitHub
```

### 2. Database Changes

```bash
# Edit SQLAlchemy models in apps/api/app/models/

# Generate migration
cd apps/api
alembic revision --autogenerate -m "add new table"

# Review generated migration in alembic/versions/

# Apply migration
alembic upgrade head

# Or use npm script from root:
npm run db:migrate:create "add new table"
npm run db:migrate
```

### 3. API Development

1. **Create Pydantic schema** in `apps/api/app/schemas/`
2. **Create SQLAlchemy model** in `apps/api/app/models/`
3. **Create service** in `apps/api/app/services/`
4. **Create API router** in `apps/api/app/api/v1/endpoints/`
5. **Write tests** in `apps/api/tests/`
6. **Run tests**: `pytest`

### 4. Frontend Development

1. **Create component** in `apps/web/src/components/`
2. **Create API client** in `apps/web/src/lib/api.ts`
3. **Create page** in `apps/web/src/app/`
4. **Write tests** in `apps/web/src/__tests__/`
5. **Run tests**: `npm run test`

---

## Testing

### Backend Testing

```bash
cd apps/api

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
# Open htmlcov/index.html to view coverage

# Run specific test file
pytest tests/unit/test_workflows.py

# Run specific test function
pytest tests/unit/test_workflows.py::test_create_workflow

# Run tests matching pattern
pytest -k "workflow"

# Run tests with markers
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
pytest -m "not slow"     # Skip slow tests
```

### Frontend Testing

```bash
cd apps/web

# Run all tests
npm run test

# Run in watch mode
npm run test:watch

# Run with coverage
npm run test -- --coverage

# Run E2E tests (Playwright)
npx playwright test

# Run E2E in UI mode
npx playwright test --ui
```

### CI/CD Testing

Tests run automatically on:

- **Every PR**: Lint, type-check, unit tests, integration tests, E2E smoke tests
- **Every merge to main**: Full test suite + security scans

Quality gates (must pass to merge):

- ✅ All tests passing
- ✅ Code coverage >= 70%
- ✅ No ESLint/Ruff errors
- ✅ TypeScript/MyPy type checking passes
- ✅ No high/critical security vulnerabilities

---

## Environment Variables

See `.env.template` for all available environment variables.

### Required Variables

| Variable            | Description                    | Example                                                    |
| ------------------- | ------------------------------ | ---------------------------------------------------------- |
| `DATABASE_URL`      | PostgreSQL connection string   | `postgresql://postgres:postgres@localhost:5432/qteria_dev` |
| `REDIS_URL`         | Redis connection string        | `redis://localhost:6379/0`                                 |
| `NEXTAUTH_SECRET`   | NextAuth.js secret (32+ chars) | Generate: `openssl rand -base64 32`                        |
| `JWT_SECRET`        | JWT signing secret (32+ chars) | Generate: `openssl rand -base64 32`                        |
| `ANTHROPIC_API_KEY` | Claude API key                 | `sk-ant-...` from https://console.anthropic.com/           |

### Optional Variables

| Variable                | Description               | Default                          |
| ----------------------- | ------------------------- | -------------------------------- |
| `NEXT_PUBLIC_API_URL`   | API base URL for frontend | `http://localhost:8000/v1`       |
| `LOG_LEVEL`             | Logging level             | `INFO`                           |
| `SENTRY_DSN`            | Sentry error tracking     | (none)                           |
| `BLOB_READ_WRITE_TOKEN` | Vercel Blob token         | (none - required for production) |

---

## Deployment

### Frontend (Vercel)

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

Environment variables to set in Vercel dashboard:

- `NEXT_PUBLIC_API_URL`
- `NEXTAUTH_SECRET`
- `DATABASE_URL` (Vercel Postgres)
- `BLOB_READ_WRITE_TOKEN` (auto-set by Vercel)

### Backend (Railway)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# Deploy
railway up
```

Environment variables to set in Railway dashboard:

- `DATABASE_URL`
- `REDIS_URL`
- `JWT_SECRET`
- `ANTHROPIC_API_KEY`
- All variables from `.env.template`

---

## Troubleshooting

### Docker services won't start

```bash
# Check if ports are in use
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
lsof -i :5050  # PgAdmin

# Stop conflicting services
# Kill process: kill -9 <PID>

# Or change ports in docker-compose.yml
```

### Database connection errors

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check connection
docker exec -it qteria-postgres psql -U postgres -d qteria_dev

# Reset database
npm run docker:down
npm run docker:up
npm run db:migrate
```

### Frontend won't connect to API

```bash
# Check API is running
curl http://localhost:8000/health

# Check NEXT_PUBLIC_API_URL in .env
# Should be: http://localhost:8000/v1

# Check CORS settings in apps/api/app/main.py
```

### Celery worker not processing jobs

```bash
# Check Redis is running
redis-cli ping
# Should return: PONG

# Check Celery worker logs
cd apps/api
celery -A app.workers worker --loglevel=debug

# Flush Redis queue (⚠️ deletes all jobs)
redis-cli FLUSHDB
```

### Python dependencies issues

```bash
# Clear pip cache
pip cache purge

# Reinstall dependencies
cd apps/api
rm -rf venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
```

### Node modules issues

```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

## Architecture Principles

1. **Monolith First**: Frontend (Next.js) + Backend (FastAPI) as separate apps, but deployed as monolith
2. **Background Jobs**: Long AI validation (5-10 min) runs async via Celery + Redis
3. **API-First**: FastAPI exposes REST API, Next.js consumes it
4. **Data Privacy by Design**: PDFs encrypted in Blob, AI with zero-retention, audit logs in PostgreSQL
5. **Boring Technology**: Proven stack (Next.js, FastAPI, PostgreSQL, Redis) - no bleeding edge

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for development guidelines.

---

## License

Proprietary - All rights reserved

---

## Support

For issues or questions:

- **Documentation**: `/docs` folder
- **GitHub Issues**: https://github.com/your-org/qteria/issues
- **Email**: support@qteria.com

---

**Built with simplicity, reliability, and evidence-based validation in mind.**
