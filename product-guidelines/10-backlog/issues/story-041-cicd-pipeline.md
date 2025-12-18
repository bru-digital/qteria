# [STORY-041] CI/CD Pipeline (GitHub Actions)

**Epic**: EPIC-10 - Testing & Quality Assurance
**Priority**: P0 (MVP Critical)
**Estimated Effort**: 2 days
**Journey Step**: Cross-Cutting - Quality

---

## User Story

**As a** developer
**I want to** automate testing and deployment with CI/CD
**So that** every code change is validated and deployed safely

---

## Acceptance Criteria

- [ ] GitHub Actions workflow configured
- [ ] Runs on every PR to main
- [ ] Enforces quality gates (tests, coverage, linting)
- [ ] Auto-deploy to staging on merge to main
- [ ] Auto-deploy to production on release tag
- [ ] Test suite completes in <10 minutes
- [ ] Deployment automated (zero manual steps)

---

## Technical Details

**Quality Gates** (Must pass before merge):

1. ✅ All unit tests pass (<2 min)
2. ✅ All integration tests pass (<5 min)
3. ✅ Code coverage >= 70% overall (95% for AI validation)
4. ✅ E2E smoke tests pass (<5 min)
5. ✅ Linting passes (ESLint, Ruff)
6. ✅ Type checking passes (TypeScript, MyPy)
7. ✅ No high/critical security vulnerabilities (Snyk)

**GitHub Actions Workflow**:

```yaml
# .github/workflows/ci-cd.yml

name: CI/CD

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]
    tags:
      - 'v*'

jobs:
  test:
    name: Test & Quality Gates
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: testpassword
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Setup Node.js 20
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install backend dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Install frontend dependencies
        run: |
          cd frontend
          npm ci

      - name: Run linters
        run: |
          cd backend && ruff check .
          cd frontend && npm run lint

      - name: Run type checking
        run: |
          cd backend && mypy .
          cd frontend && npm run type-check

      - name: Run unit tests (backend)
        run: |
          cd backend
          pytest tests/unit --cov --cov-report=xml

      - name: Run unit tests (frontend)
        run: |
          cd frontend
          npm run test:unit -- --coverage

      - name: Run integration tests
        run: |
          cd backend
          pytest tests/integration

      - name: Check code coverage
        run: |
          cd backend
          coverage report --fail-under=70

      - name: Run E2E smoke tests
        run: |
          cd frontend
          npm run test:e2e:smoke

      - name: Security scan (Snyk)
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

  deploy-staging:
    name: Deploy to Staging
    needs: test
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Deploy backend to Railway
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: |
          npm install -g railway
          railway link ${{ secrets.RAILWAY_PROJECT_ID }}
          railway up --service backend --environment staging

      - name: Deploy frontend to Vercel
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
        run: |
          npm install -g vercel
          cd frontend
          vercel --prod --token ${{ secrets.VERCEL_TOKEN }} --env=staging

      - name: Run E2E full suite (staging)
        run: |
          cd frontend
          STAGING_URL=${{ secrets.STAGING_URL }} npm run test:e2e:full

  deploy-production:
    name: Deploy to Production
    needs: test
    if: startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Deploy backend to Railway (production)
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: |
          npm install -g railway
          railway link ${{ secrets.RAILWAY_PROJECT_ID }}
          railway up --service backend --environment production

      - name: Deploy frontend to Vercel (production)
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
        run: |
          npm install -g vercel
          cd frontend
          vercel --prod --token ${{ secrets.VERCEL_TOKEN }}

      - name: Create GitHub Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          draft: false
          prerelease: false
```

**Secrets to Configure**:

```
RAILWAY_TOKEN           # Railway API token
RAILWAY_PROJECT_ID      # Railway project ID
VERCEL_TOKEN            # Vercel deploy token
SNYK_TOKEN              # Snyk security scan token
STAGING_URL             # Staging environment URL
```

**Deployment Strategy**:

- **PR**: Run tests + quality gates (block merge if failed)
- **Merge to main**: Deploy to staging automatically
- **Release tag** (e.g., `v1.0.0`): Deploy to production automatically

**Rollback Strategy**:

- Railway: `railway rollback --service backend`
- Vercel: Automatic rollback via Vercel dashboard
- Git: Revert commit and push

---

## RICE Score

**RICE**: (100 × 2 × 1.00) ÷ 2 = **100**

---

## Definition of Done

- [ ] GitHub Actions workflow configured
- [ ] Quality gates enforced (tests, coverage, linting)
- [ ] Tests run on every PR
- [ ] Coverage >= 70% enforced
- [ ] Auto-deploy to staging on merge
- [ ] Auto-deploy to production on release tag
- [ ] Security scanning automated (Snyk)
- [ ] Deployment successful (tested end-to-end)
- [ ] Secrets configured in GitHub
- [ ] Documentation updated (deployment guide)
- [ ] Code reviewed and merged

---

## Risks & Mitigations

**Risk**: CI/CD too slow (>10 min blocks PRs)

- **Mitigation**: Run smoke tests on PR (5 min), full suite nightly

**Risk**: Flaky tests fail CI (false negatives)

- **Mitigation**: Improve test stability (STORY-040), retry flaky tests 3x

**Risk**: Deployment breaks production

- **Mitigation**: Deploy to staging first, run E2E tests on staging, require manual approval for production (optional)

---

## Notes

CI/CD is MVP critical - without automation, manual deployments will slow development and introduce human errors in compliance industry.

**Reference**: `product-guidelines/09-test-strategy.md` (testing strategy)
