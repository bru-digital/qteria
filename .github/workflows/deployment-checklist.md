# Railway Backend Deployment Checklist

> **Purpose:** Ensure reliable Railway backend deployments with comprehensive verification.
>
> **Last Updated:** 2025-12-13
>
> **Current Production URL:** https://qteriaappapi-production.up.railway.app

---

## Pre-Deployment Checklist

### 1. Configuration Verification

- [ ] **Dockerfile Exists**
  - Path: `/apps/api/Dockerfile`
  - Verify: `ls apps/api/Dockerfile` shows file exists
  - Base image: `python:3.11-slim`

- [ ] **Railway Service Settings**
  - Root Directory: `/apps/api`
  - Watch Paths: `/apps/api/**`
  - Builder: Automatic (Railway detects Dockerfile)
  - NO custom build command (Dockerfile handles this)
  - NO custom start command (Dockerfile CMD handles this)

### 2. Environment Variables

Verify all required environment variables are set in Railway dashboard:

**Required:**
- [ ] `DATABASE_URL` - Neon PostgreSQL connection string
  - Format: `postgresql://user:pass@host/dbname?sslmode=require`
  - Database: `qteria_prod` (NOT `qteria_dev` or `qteria_test`)
- [ ] `BLOB_READ_WRITE_TOKEN` - Vercel Blob storage token
- [ ] `JWT_SECRET` - JWT signing secret (32+ characters)
- [ ] `ANTHROPIC_API_KEY` - Claude API key for AI validation
- [ ] `CORS_ORIGINS` - Comma-separated allowed origins
  - Include: `https://qteria.com,https://qteria.vercel.app,https://*.vercel.app`
- [ ] `PYTHON_ENV` - Set to `production` (CRITICAL: NOT `ENVIRONMENT`)

**Optional:**
- [ ] `REDIS_URL` - Upstash Redis connection string (for background jobs)

**Do NOT Set:**
- [ ] ~~`PORT`~~ - Railway does NOT provide PORT env var, backend uses hardcoded port 8000

### 3. Database Migrations

- [ ] **Check Migration Status**
  ```bash
  # Connect to production database
  DATABASE_URL="postgresql://..." alembic current
  ```

- [ ] **Apply Pending Migrations (if needed)**
  ```bash
  # Run migrations against production database
  DATABASE_URL="postgresql://..." alembic upgrade head
  ```

- [ ] **Verify Tables Exist**
  ```bash
  # Connect to Neon PostgreSQL and check tables
  psql $DATABASE_URL -c "\dt"
  ```

---

## Deployment Steps

### 1. Trigger Deployment

- [ ] **Push to Main Branch**
  ```bash
  git checkout main
  git pull origin main
  git merge <feature-branch>
  git push origin main
  ```

- [ ] **Monitor Railway Build**
  - Railway dashboard → Deployments
  - Watch build logs for errors
  - Verify Dockerfile build steps complete
  - Look for "Successfully built" message

### 2. Monitor Deployment Progress

- [ ] **Build Phase**
  - Docker image build starts
  - Python dependencies installed
  - libmagic1 system dependency installed
  - Application files copied

- [ ] **Deploy Phase**
  - Container starts
  - Health check begins (usually within 30 seconds)
  - Status changes to "Ready" (green checkmark)

- [ ] **Check for Errors**
  - No errors in deployment logs
  - No Python tracebacks
  - No database connection errors

---

## Post-Deployment Verification

### 1. Health Check

- [ ] **Quick Health Check**
  ```bash
  curl https://qteriaappapi-production.up.railway.app/health
  ```

  **Expected Output:**
  ```json
  {"status":"healthy","environment":"production"}
  ```

- [ ] **Verify Environment Variable**
  - `environment` field should be `"production"`
  - If not, check `PYTHON_ENV` env var in Railway

### 2. CORS Configuration

- [ ] **Test CORS Headers**
  ```bash
  curl -I -H "Origin: https://qteria.vercel.app" \
    https://qteriaappapi-production.up.railway.app/health
  ```

  **Expected Headers:**
  ```
  access-control-allow-origin: https://qteria.vercel.app
  access-control-allow-methods: GET, POST, PUT, DELETE, OPTIONS
  access-control-allow-credentials: true
  ```

- [ ] **Test Preflight Request**
  ```bash
  curl -X OPTIONS \
    -H "Origin: https://qteria.vercel.app" \
    -H "Access-Control-Request-Method: POST" \
    https://qteriaappapi-production.up.railway.app/v1/workflows
  ```

### 3. API Endpoints

- [ ] **Test Unauthenticated Endpoint (should return 401)**
  ```bash
  curl https://qteriaappapi-production.up.railway.app/v1/workflows
  ```

  **Expected:** 401 Unauthorized (proves endpoint exists and auth is enforced)

- [ ] **Verify Error Format**
  ```bash
  curl https://qteriaappapi-production.up.railway.app/v1/invalid-endpoint
  ```

  **Expected:** 404 with proper error format (error.code, error.message)

### 4. Comprehensive Integration Tests

- [ ] **Run Integration Test Script**
  ```bash
  cd apps/web
  API_URL=https://qteriaappapi-production.up.railway.app npm run verify:integration
  ```

  **Expected Output:**
  ```
  ✓ Backend Health Check
  ✓ CORS Configuration
  ✓ API Endpoints Availability
  ✓ Error Format Consistency
  ✓ Database Connectivity
  ✓ Response Time Check

  ✓ ALL INTEGRATION TESTS PASSED
  ```

### 5. Database Connectivity

- [ ] **Verify Database Connection**
  - Check Railway logs for successful database connection
  - No SQLAlchemy errors
  - No connection timeout errors

- [ ] **Test Database Read**
  ```bash
  curl https://qteriaappapi-production.up.railway.app/v1/workflows
  ```

  **Expected:** 401 Unauthorized (NOT 500 Internal Server Error)
  - 401 = database working, auth enforced
  - 500 = database connection failed

### 6. Performance Check

- [ ] **Response Time Verification**
  ```bash
  time curl https://qteriaappapi-production.up.railway.app/health
  ```

  **Expected:** <2 seconds (including network latency)

  **Target:** P95 <500ms for CRUD operations (per CLAUDE.md)

---

## Frontend Integration

### 1. Update Vercel Environment Variable

- [ ] **Set API_URL in Vercel**
  1. Vercel dashboard → qteria (project) → Settings → Environment Variables
  2. Update `API_URL` to: `https://qteriaappapi-production.up.railway.app`
  3. Apply to: Production, Preview, Development (or just Production for now)

### 2. Redeploy Frontend

- [ ] **Trigger Vercel Redeploy**
  1. Vercel dashboard → qteria (project) → Deployments
  2. Find latest deployment → Click [...] → Redeploy
  3. Wait for deployment to complete (green checkmark)

### 3. End-to-End Testing (Manual)

- [ ] **Test Workflow Creation**
  1. Visit https://qteria.com or https://qteria.vercel.app
  2. Navigate to workflow creation page
  3. Create a test workflow
  4. Verify workflow is saved (appears in list)
  5. Check browser console for errors

- [ ] **Verify No CORS Errors**
  - Open browser DevTools → Console
  - No "CORS policy" errors
  - No "blocked by CORS policy" messages

- [ ] **Test API Proxy**
  - Frontend should call Railway backend via Next.js API proxy
  - Check Network tab for API calls
  - Verify requests go to `https://qteriaappapi-production.up.railway.app`

---

## Monitoring & Alerts

### 1. Railway Logs

- [ ] **Check Startup Logs**
  - Railway dashboard → Deployments → Click deployment → Logs
  - Verify "Application startup complete" message
  - No Python errors or warnings
  - No database connection errors

- [ ] **Monitor Runtime Logs**
  - Watch for 500 errors
  - Watch for database errors
  - Watch for CORS errors (blocked origins)

### 2. Health Check Monitoring

- [ ] **Set Up Health Check Alerts**
  - Railway dashboard → Service → Settings → Health Checks
  - Configure `/health` endpoint check
  - Set alert thresholds (e.g., 3 failed checks = alert)

### 3. Error Tracking (Optional)

- [ ] **Set Up Sentry (if configured)**
  - Verify errors are being tracked
  - Test error reporting with intentional error
  - Check Sentry dashboard for errors

---

## Rollback Procedure

If deployment fails or introduces critical bugs:

### Method 1: Railway Dashboard Rollback

- [ ] **Find Last Working Deployment**
  1. Railway dashboard → Deployments
  2. Find last deployment with "Ready" status (before failed deployment)
  3. Click [...] → Redeploy
  4. Wait for deployment to complete

### Method 2: Git Revert

- [ ] **Revert Problematic Commit**
  ```bash
  git log --oneline  # Find commit to revert
  git revert <commit-hash>
  git push origin main
  ```

  Railway will auto-deploy the reverted commit.

### Method 3: Emergency Fallback (Last Resort)

- [ ] **Temporarily Point Frontend to Local Backend**
  1. Update Vercel `API_URL` to local backend URL
  2. Run backend locally: `cd apps/api && uvicorn app.main:app --port 8000`
  3. Debug issue, fix, commit, redeploy to Railway
  4. Update Vercel `API_URL` back to Railway domain

---

## Common Issues & Quick Fixes

### Issue: Health check fails with 500 error

**Quick Fix:**
1. Check Railway logs for Python traceback
2. Most common: Missing environment variable
3. Verify all required env vars are set (see checklist above)
4. Redeploy after fixing env vars

### Issue: CORS errors in browser

**Quick Fix:**
1. Verify `CORS_ORIGINS` includes all Vercel domains
2. Add `https://*.vercel.app` for preview deployments
3. Redeploy backend after updating CORS_ORIGINS

### Issue: Database connection timeout

**Quick Fix:**
1. Verify `DATABASE_URL` is correct
2. Check Neon PostgreSQL allows connections from anywhere
3. Test connection: `psql $DATABASE_URL -c "SELECT 1"`
4. Verify `?sslmode=require` in connection string

### Issue: Application crashes on startup

**Quick Fix:**
1. Check Railway logs for error message
2. Common causes:
   - Missing system dependency (libmagic1)
   - Missing Python dependency
   - Invalid DATABASE_URL format
3. Verify Dockerfile has all dependencies
4. Test locally: `docker build -t qteria-api apps/api && docker run -p 8000:8000 qteria-api`

---

## Success Criteria

Deployment is considered successful when:

- [x] Health check returns 200 OK with `environment: production`
- [x] CORS headers allow Vercel origins
- [x] Integration tests pass (6/6 tests)
- [x] Database connectivity verified
- [ ] Frontend can create workflows without errors
- [ ] No CORS errors in browser console
- [ ] Railway logs show no errors
- [ ] Response times within acceptable range (<2s)

---

## Lessons Learned

**Deployment Evolution:**
1. **Nixpacks (Failed):** Python 3.14 detection, complex config
2. **railway.json + Nixpacks (Failed):** Port binding, env var confusion
3. **Dockerfile (Success):** Simple, testable, reliable

**Key Takeaways:**
- Dockerfile is more reliable than Nixpacks for complex Python apps
- Railway does NOT provide PORT env var in all scenarios (hardcode port 8000)
- Use `PYTHON_ENV` instead of `ENVIRONMENT` for environment detection
- Always test locally with Docker before deploying to Railway
- Integration tests catch deployment issues before frontend integration

---

**Checklist Version:** 1.0
**Last Successful Deployment:** 2025-12-13
**Deployment Time:** ~5 minutes (build + deploy)
**Uptime Target:** 99.9%
