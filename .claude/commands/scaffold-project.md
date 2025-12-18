---
description: Session 12 - Project scaffold from backlog to working codebase
---

# Session 12: Scaffold Project

This is **Session 12** of the cascade. You'll generate a complete, runnable development environment that bridges the gap between your strategic backlog and actual code implementation.

## Your Role

You are a senior engineer setting up a new project. Your job is to:

1. **Read previous outputs** (journey, tech stack, architecture, backlog)
2. **Generate working development environment** (not just documentation)
3. **Create actual config files** that developers can use immediately
4. **Set up CI/CD pipeline** for automated testing and deployment
5. **Document setup process** so team can get running in minutes

## Critical Philosophy

**This is where strategy meets reality.**

After 11 sessions, users have:

- ✅ Validated user journey
- ✅ Validated product strategy
- ✅ Chosen optimal tech stack
- ✅ Defined strategy (mission, metrics, monetization, architecture)
- ✅ Designed database schema
- ✅ Generated API contracts
- ✅ Created testing strategy
- ✅ Generated prioritized backlog
- ✅ Created GitHub issues

**What they DON'T have**: A single line of working code.

**Session 12 fixes this.** Generate a development environment where the first story can be implemented immediately.

---

## Process

### Step 1: Read ALL Previous Outputs

```
Read: product-guidelines/00-user-journey.md
Read: product-guidelines/11-product-strategy-essentials.md
Read: product-guidelines/02-tech-stack.md
Read: product-guidelines/04-architecture.md
Read: product-guidelines/07-database-schema-essentials.md
Read: product-guidelines/08-api-contracts-essentials.md
Read: product-guidelines/09-test-strategy-essentials.md
Read: product-guidelines/10-backlog/BACKLOG.md
```

**Context Optimization**: We read essentials versions for significant context reduction:

- `11-product-strategy-essentials.md` (~65% smaller) - Contains vision, positioning, goals, principles, and roadmap themes
- `07-database-schema-essentials.md` (~56% smaller) - Contains table list, ERD, relationships sufficient for scaffold generation
- `08-api-contracts-essentials.md` (~80% smaller) - Contains endpoint list organized by journey step
- `09-test-strategy-essentials.md` (~66% smaller) - Contains coverage targets, test types, and quality gates

**Extract**:

- **Project name** (from journey)
- **Tech stack choices** (languages, frameworks, databases, tools)
- **Architecture decisions** (monorepo vs multi-repo, patterns, modules)
- **Services/modules needed** (from backlog epics)

### Step 2: Determine Repository Structure

**Read architecture decision** (from `05-architecture.md`):

- Monorepo or multi-repo?
- Microservices or monolith?
- Number of distinct services?

**Decision Tree - Repository Type:**

```
1. How many deployable services/apps?
   ├─ 1 service (web app only) → Single repo, simple structure
   ├─ 2-4 services (web + API + worker) → Monorepo with workspaces
   └─ 5+ services → Multi-repo OR monorepo with build orchestration

2. Is there shared code between services?
   ├─ YES → Monorepo (easier to share types, utilities, components)
   └─ NO → Multi-repo is acceptable

3. Team size?
   ├─ 1-3 people → Monorepo (easier to manage, less overhead)
   ├─ 4-10 people → Monorepo with clear module boundaries
   └─ 10+ people → Consider multi-repo (team autonomy)

4. What's the deployment strategy?
   ├─ Everything deploys together → Monorepo, monolith structure
   ├─ Independent deployment → Monorepo with independent build/deploy
   └─ Microservices → Could be either (monorepo = easier, multi = autonomous)
```

**Example (compliance-saas):**

- **Services**: Web app (Next.js), Background worker (Python)
- **Shared code**: Data models, API contracts, validation schemas
- **Team size**: 2 developers
- **Decision**: **Monorepo with Turborepo**
  - `apps/web/` - Next.js frontend
  - `apps/worker/` - Python background jobs
  - `packages/shared/` - TypeScript types, utilities
  - `packages/database/` - Prisma schema

---

### Step 3: Generate Directory Structure

Based on repository type and tech stack, create the appropriate structure.

**Decision Tree - Monorepo Tool:**

```
If monorepo chosen:

1. What's the primary language?
   ├─ JavaScript/TypeScript → Turborepo, Nx, or pnpm workspaces
   ├─ Python → Poetry workspaces or simple requirements structure
   ├─ Go → Go modules with replace directives
   └─ Multi-language → Turborepo (language-agnostic) or Nx

2. Need build orchestration (caching, pipelines)?
   ├─ YES → Turborepo (best DX) or Nx (enterprise features)
   └─ NO → Native workspaces (npm/pnpm/yarn)

3. Monorepo complexity?
   ├─ 2-3 packages → Native workspaces (simplest)
   ├─ 4-10 packages → Turborepo (great balance)
   └─ 10+ packages → Nx (advanced features)
```

**Example structures:**

**JavaScript/TypeScript Monorepo (Turborepo):**

```
project-name/
├── apps/
│   ├── web/                 # Next.js frontend
│   │   ├── src/
│   │   ├── public/
│   │   ├── package.json
│   │   └── tsconfig.json
│   └── api/                 # Express/Fastify API
│       ├── src/
│       ├── package.json
│       └── tsconfig.json
├── packages/
│   ├── ui/                  # Shared React components
│   ├── database/            # Prisma schema & client
│   ├── typescript-config/   # Shared tsconfig
│   └── eslint-config/       # Shared ESLint rules
├── docker-compose.yml       # Local dev services
├── .env.template            # Environment variables
├── turbo.json              # Turborepo config
├── package.json            # Root package
└── README.md
```

**Python Monorepo:**

```
project-name/
├── apps/
│   ├── api/                # FastAPI backend
│   │   ├── src/
│   │   ├── tests/
│   │   └── pyproject.toml
│   └── worker/             # Celery worker
│       ├── src/
│       ├── tests/
│       └── pyproject.toml
├── packages/
│   ├── shared/             # Shared utilities
│   └── models/             # SQLAlchemy models
├── docker-compose.yml
├── .env.template
└── pyproject.toml          # Root config
```

**Simple Single-Repo (No monorepo tool):**

```
project-name/
├── src/                    # Application code
├── tests/
├── public/                 # Static assets
├── docker-compose.yml
├── .env.template
├── package.json (or pyproject.toml)
└── README.md
```

---

### Step 4: Generate Configuration Files

For EACH file, create ACTUAL working configuration (not templates).

#### A. Package Manager Config

**JavaScript/TypeScript - package.json:**

```json
{
  "name": "project-name",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "turbo run dev",
    "build": "turbo run build",
    "test": "turbo run test",
    "lint": "turbo run lint",
    "type-check": "turbo run type-check",
    "db:migrate": "cd packages/database && prisma migrate dev",
    "db:studio": "cd packages/database && prisma studio"
  },
  "workspaces": ["apps/*", "packages/*"],
  "devDependencies": {
    "turbo": "^1.10.0",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "eslint": "^8.50.0",
    "prettier": "^3.0.0",
    "typescript": "^5.2.0"
  }
}
```

**Python - pyproject.toml:**

```toml
[tool.poetry]
name = "project-name"
version = "0.1.0"
description = "Description from user journey"
authors = ["Your Name <you@example.com>"]

[tool.poetry.dependencies]
python = "^3.11"
# Add dependencies from tech stack

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-cov = "^4.1.0"
black = "^23.7.0"
ruff = "^0.0.285"
mypy = "^1.5.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 100
target-version = ['py311']

[tool.ruff]
line-length = 100
select = ["E", "F", "I"]

[tool.mypy]
python_version = "3.11"
strict = true
```

#### B. Docker Compose (Local Development)

**Generate based on architecture services:**

```yaml
version: '3.8'

services:
  # Database (from tech stack - PostgreSQL example)
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${DB_NAME:-app_dev}
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-postgres}
    ports:
      - '5432:5432'
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ['CMD-SHELL', 'pg_isready -U postgres']
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis (if in tech stack)
  redis:
    image: redis:7-alpine
    ports:
      - '6379:6379'
    volumes:
      - redis_data:/data
    healthcheck:
      test: ['CMD', 'redis-cli', 'ping']
      interval: 10s
      timeout: 5s
      retries: 5

  # Development database UI (optional but useful)
  pgadmin:
    image: dpage/pgadmin4:latest
    environment:
      PGADMIN_DEFAULT_EMAIL: ${PGADMIN_EMAIL:-admin@example.com}
      PGADMIN_DEFAULT_PASSWORD: ${PGADMIN_PASSWORD:-admin}
    ports:
      - '5050:80'
    depends_on:
      postgres:
        condition: service_healthy

volumes:
  postgres_data:
  redis_data:
```

**Customize based on tech stack:**

- PostgreSQL → Use above
- MongoDB → Replace with mongo:7 image
- MySQL → Replace with mysql:8 image
- Add services from architecture: Message queues (RabbitMQ), caching (Redis), search (Elasticsearch)

#### C. Environment Configuration

**Create `.env.template`** (developers copy to `.env`):

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=app_dev
DB_USER=postgres
DB_PASSWORD=postgres
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}

# Redis Configuration (if applicable)
REDIS_URL=redis://localhost:6379

# API Configuration
API_PORT=3000
API_URL=http://localhost:3000

# Authentication (example - adjust based on tech stack)
JWT_SECRET=your-secret-key-change-in-production
JWT_EXPIRES_IN=7d

# Third-party services (from tech stack integrations)
# STRIPE_SECRET_KEY=sk_test_...
# OPENAI_API_KEY=sk-...
# SENDGRID_API_KEY=SG...

# Environment
NODE_ENV=development

# Feature flags (optional but recommended)
# FEATURE_DOCUMENT_PROCESSING=true
# FEATURE_AI_EXTRACTION=false
```

**Add variables based on:**

- Tech stack integrations (Stripe, OpenAI, etc.)
- Authentication method (Clerk, Auth0, etc.)
- Deployment target (Vercel, AWS, etc.)

#### D. CI/CD Pipeline (GitHub Actions)

**Create `.github/workflows/ci.yml`:**

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  # Job 1: Lint and Type Check
  lint:
    name: Lint and Type Check
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run linter
        run: npm run lint

      - name: Run type check
        run: npm run type-check

  # Job 2: Unit Tests
  test:
    name: Run Tests
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run database migrations
        run: npm run db:migrate
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db

      - name: Run tests
        run: npm run test
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        if: always()

  # Job 3: Build Check
  build:
    name: Build Application
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build
```

**Customize based on tech stack:**

- Python: Use `setup-python` action, `pip install`, `pytest`
- Go: Use `setup-go` action, `go test`, `go build`
- Multi-language: Add multiple jobs for each language

**Add deployment job** (if architecture specifies):

```yaml
deploy:
  name: Deploy to Staging
  runs-on: ubuntu-latest
  needs: [lint, test, build]
  if: github.ref == 'refs/heads/develop'

  steps:
    - uses: actions/checkout@v4
    # Add deployment steps based on target (Vercel, AWS, Railway, etc.)
```

#### E. Development Documentation (README.md)

**Create comprehensive setup instructions:**

````markdown
# [Project Name]

[One-sentence description from user journey]

## Quick Start

### Prerequisites

- Node.js 20+ (or Python 3.11+)
- Docker & Docker Compose
- Git

### Setup

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd project-name
   ```
````

2. **Install dependencies**

   ```bash
   npm install
   ```

3. **Set up environment variables**

   ```bash
   cp .env.template .env
   # Edit .env with your local values
   ```

4. **Start local services**

   ```bash
   docker-compose up -d
   ```

5. **Run database migrations**

   ```bash
   npm run db:migrate
   ```

6. **Start development server**

   ```bash
   npm run dev
   ```

7. **Open your browser**
   - Web app: http://localhost:3000
   - API: http://localhost:3001
   - Database UI: http://localhost:5050

## Project Structure

[Generated structure from Step 3]

## Available Scripts

- `npm run dev` - Start development servers
- `npm run build` - Build for production
- `npm run test` - Run tests
- `npm run lint` - Run linter
- `npm run type-check` - Run TypeScript type checking
- `npm run db:migrate` - Run database migrations
- `npm run db:studio` - Open database UI

## Tech Stack

[List from 02-tech-stack.md]

## Architecture

[Key points from 05-architecture.md]

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for development guidelines.

## License

[License information]

````

#### F. Additional Configuration Files

**TypeScript Configuration (tsconfig.json):**
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022"],
    "module": "commonjs",
    "moduleResolution": "node",
    "esModuleInterop": true,
    "strict": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
````

**ESLint Configuration (.eslintrc.json):**

```json
{
  "extends": ["eslint:recommended", "plugin:@typescript-eslint/recommended", "prettier"],
  "parser": "@typescript-eslint/parser",
  "plugins": ["@typescript-eslint"],
  "root": true,
  "rules": {
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    "@typescript-eslint/explicit-function-return-type": "off"
  }
}
```

**Prettier Configuration (.prettierrc):**

```json
{
  "semi": false,
  "singleQuote": true,
  "trailingComma": "es5",
  "printWidth": 100,
  "tabWidth": 2
}
```

**.gitignore:**

```gitignore
# Dependencies
node_modules/
.pnp/
.pnp.js

# Testing
coverage/
*.lcov

# Production
dist/
build/
.next/
out/

# Environment
.env
.env*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Database
*.db
*.sqlite

# Logs
logs/
*.log
npm-debug.log*
```

---

### Step 5: Generate Scaffold Output

Create two outputs:

#### A. Documentation (product-guidelines/12-project-scaffold.md)

````markdown
# Project Scaffold

**Generated**: [Date]
**Based on**: Sessions 1-7 outputs

## Decisions Made

### Repository Structure

**Decision**: [Monorepo/Multi-repo/Simple]
**Tool**: [Turborepo/Nx/Poetry/None]
**Reasoning**: [Why this structure fits the architecture and team]

### Development Environment

**Services**: [List Docker services]
**Database**: [PostgreSQL/MongoDB/etc.]
**Caching**: [Redis/Memcached/None]
**Message Queue**: [RabbitMQ/SQS/None]

### CI/CD Pipeline

**Platform**: GitHub Actions
**Jobs**: Lint, Test, Build, [Deploy if applicable]
**Test Database**: [How tests run]
**Deployment Target**: [Vercel/AWS/Railway/Manual]

## Generated Files

### Configuration

- ✅ `package.json` (or `pyproject.toml`)
- ✅ `docker-compose.yml`
- ✅ `.env.template`
- ✅ `turbo.json` (if monorepo)
- ✅ `tsconfig.json` (if TypeScript)
- ✅ `.eslintrc.json`
- ✅ `.prettierrc`
- ✅ `.gitignore`

### CI/CD

- ✅ `.github/workflows/ci.yml`

### Documentation

- ✅ `README.md`

### Directory Structure

[Full tree from Step 3]

## Setup Instructions

1. Copy all files from `product-guidelines/12-project-scaffold/` to your project root
2. Run `docker-compose up -d` to start local services
3. Copy `.env.template` to `.env` and fill in values
4. Run `npm install` (or `poetry install`)
5. Run `npm run dev` to start development

## Next Steps

After copying the scaffold:

1. **Initialize Git** (if not already)
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Project scaffold"
   ```
````

2. **Set up GitHub repository**

   ```bash
   gh repo create project-name --private
   git remote add origin <repo-url>
   git push -u origin main
   ```

3. **Start implementing backlog**
   - Reference `product-guidelines/10-backlog/` for prioritized stories
   - Start with P0 (critical) stories
   - Each story references tech stack and design system

4. **Configure deployment**
   - Set up deployment target (Vercel/AWS/etc.)
   - Add deployment secrets to GitHub
   - Update CI/CD to deploy on merge to main

```

#### B. Actual Files (product-guidelines/12-project-scaffold/)

Create a directory with ALL generated files:

```

product-guidelines/12-project-scaffold/
├── package.json
├── docker-compose.yml
├── .env.template
├── turbo.json
├── tsconfig.json
├── .eslintrc.json
├── .prettierrc
├── .gitignore
├── .github/
│ └── workflows/
│ └── ci.yml
├── README.md
└── apps/ (or src/)
└── .gitkeep

```

---

### Step 6: Validate Scaffold

**Quality Checklist:**

- [ ] Repository structure matches architecture decisions?
- [ ] All tech stack choices reflected in configs?
- [ ] Docker Compose includes all required services from architecture?
- [ ] CI/CD pipeline runs tests and linting?
- [ ] Environment template includes all necessary variables?
- [ ] README documents complete setup process?
- [ ] Developer can run `docker-compose up && npm install && npm run dev` and see working app?
- [ ] All generated files use correct syntax (valid JSON, YAML, etc.)?
- [ ] Monorepo tool configured correctly (if applicable)?
- [ ] Git ignores sensitive files (.env, node_modules, etc.)?

**Test the scaffold mentally:**
1. Imagine developer clones empty repo
2. They copy scaffold files
3. They follow README
4. Can they start coding first story in <15 minutes?
5. If NO: Scaffold is incomplete

---

## What We DIDN'T Choose (And Why)

### Kubernetes for Local Development

**What it is**: Container orchestration platform, industry standard for production

**Why not (for this journey)**:
- **Journey is MVP stage** (< 1000 users expected from backlog)
- **Team is 1-3 people** (Kubernetes operational overhead is massive)
- **Docker Compose is sufficient** for local dev and small-scale production
- **"Boring is beautiful"** principle - Docker Compose is simpler, well-understood
- **Can migrate later** if scale demands it (Kubernetes is deployment, not architecture change)

**When to reconsider**:
- IF hitting >100K requests/day with scaling bottlenecks
- IF need multi-region deployment (Kubernetes excels at this)
- IF team grows DevOps/platform engineering capability
- IF using managed Kubernetes (GKE, EKS) reduces operational burden

**Example**: If compliance document processing hits 50K docs/day and single-region deployment can't keep up, migrate worker service to Kubernetes for auto-scaling while keeping web app on simpler platform.

---

### Microservices Architecture from Day 1

**What it is**: Each feature as independent service with own database and deployment

**Why not (for this journey)**:
- **Journey is early stage** (MVP, unvalidated scale)
- **Premature optimization** - microservices solve problems you don't have yet
- **Operational complexity** is high (distributed tracing, service mesh, etc.)
- **Team is small** (1-3 people can't maintain 10 services effectively)
- **Data consistency is simpler** in monolith (no distributed transactions)

**When to reconsider**:
- IF team grows >10 engineers (need autonomous teams)
- IF different features need independent scaling (parse service 100x more load than UI)
- IF services have truly different tech requirements (ML service in Python, real-time in Go)
- IF organizational structure demands it (Conway's Law)

**Example**: Monolith for MVP. When document parsing becomes bottleneck (10K docs/day), extract ONLY that service to independent microservice with dedicated resources. Keep rest as monolith.

---

### Feature Branch Deployment (Vercel/Netlify Preview)

**What it is**: Every git branch gets deployed preview URL automatically

**Why not initially**:
- **Great feature but adds complexity** to CI/CD pipeline
- **Cost increases** with many preview deploys
- **MVP focus** - optimize for shipping, not preview URLs
- **Can add later** easily (doesn't require architecture change)

**When to reconsider**:
- IF team grows and wants design/PM review of features
- IF doing A/B testing or customer preview before production
- IF budget allows ($20-50/month for preview deploys)

**Example**: Start with main branch → staging/production only. Add preview deploys when you have 3+ developers and need feature review workflow.

---

### Multi-Stage Docker Builds for Local Dev

**What it is**: Optimized Docker images for production, dev uses docker-compose

**Why not initially**:
- **Local dev with Docker is slower** than native (hot reload, volume mounts)
- **Docker Compose is for infrastructure** (DB, Redis), not app code
- **Better DX to run app natively** and only use Docker for services
- **Can containerize later** for production deployment

**When to reconsider**:
- IF deploying to production via Docker (not Vercel/serverless)
- IF team has environment inconsistencies ("works on my machine")
- IF app has complex native dependencies (image processing, etc.)

**Example**: Dev runs `npm run dev` natively, Docker Compose for PostgreSQL/Redis. When ready for production, create Dockerfile for deployment to Railway/Fly.io/AWS.

---

### Separate Infrastructure Repository

**What it is**: Terraform/Pulumi in separate repo from application code

**Why not**:
- **Journey is pre-launch** (no production infrastructure yet)
- **Managed platforms handle infrastructure** (Vercel, Railway, etc.)
- **Team is small** (infrastructure-as-code is overkill)
- **Can extract later** if infrastructure grows complex

**When to reconsider**:
- IF using AWS/GCP with custom infrastructure (VPCs, load balancers, etc.)
- IF need reproducible infrastructure (disaster recovery, multi-region)
- IF DevOps engineer joins team

**Example**: Start with Vercel/Railway (zero infrastructure code). When scaling to 100K+ users on AWS, extract infrastructure to Terraform repo.

---

## After Generation

```

✅ Session 8 complete! Development environment ready.

Your Scaffold:
📁 Complete directory structure
⚙️ Configuration files (package.json, docker-compose.yml, etc.)
🔧 CI/CD pipeline (GitHub Actions)
📝 Developer documentation (README.md)
🐳 Local development services (Docker Compose)

Next Steps:

1. Copy files from product-guidelines/12-project-scaffold/ to your project root
2. Follow README.md setup instructions
3. Verify environment works (docker-compose up, npm run dev)
4. Start implementing P0 stories from product-guidelines/10-backlog/

When ready, start building or run: /cascade-status

```

---

## Important Guidelines

1. **Generate REAL files**: Not templates with placeholders - actual working configs
2. **Match tech stack**: Every generated file must reflect Session 3 tech choices
3. **Match architecture**: Structure must align with Session 4 architecture decisions
4. **Developer experience**: Setup should take <15 minutes from clone to running
5. **One command to rule them all**: `docker-compose up` should start everything needed
6. **Documentation is critical**: README must be complete, step-by-step, tested

## Reference

- Previous session: `/create-gh-issues` (Session 7)
- Next: Start building! Reference backlog in `product-guidelines/10-backlog/` or GitHub issues
- Example: `/examples/compliance-saas/scaffold/` (if created)

---

**Now, bridge the gap from strategy to working code! Generate a complete development environment!**
```
