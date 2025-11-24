# Deployment Guide

## Environment Setup

This project uses **3 separate databases** for proper isolation:

| Environment | Vercel Env | Database | Purpose |
|------------|-----------|----------|---------|
| **Local Development** | N/A | `qteria-db` | Your local work |
| **Preview (PRs)** | Preview | `qteria-test` | Testing PRs before merge |
| **Production** | Production | `qteria-prod` | Live customer data |

---

## Database Configuration

### 1. Neon Databases (Create These)

Create 3 separate databases in Neon:
- ✅ `qteria-db` - Already created (development)
- ✅ `qteria-test` - Already created (preview/testing)
- ⏳ `qteria-prod` - Create when ready to launch

### 2. Local Development (.env)

File: `/Users/bru/dev/qteria/.env`

```bash
# Points to qteria-db (development database)
DATABASE_URL=postgresql://neondb_owner:...@ep-xxx.neon.tech/qteria_db?sslmode=require
```

### 3. Test Environment (.env.test)

File: `/Users/bru/dev/qteria/apps/api/.env.test`

```bash
# Points to qteria-test (for pytest)
DATABASE_URL=postgresql://neondb_owner:...@ep-xxx.neon.tech/qteria_test?sslmode=require
```

### 4. Vercel Environment Variables

Go to: **Vercel Dashboard → qteria → Settings → Environment Variables**

#### Option A: Use TEST prefix (Current Setup)

If you connected with prefix `TEST`:

**Preview Environment:**
```
TEST_URL → postgresql://...qteria_test... (for PR previews)
```

**Production Environment:**
```
TEST_URL → postgresql://...qteria_prod... (for production - change later!)
```

#### Option B: Use DATABASE prefix (Recommended)

**Better approach** - Override the existing `DATABASE_POSTGRES_URL`:

1. Delete or rename `DATABASE_POSTGRES_URL` in Vercel
2. Reconnect Neon with prefix `DATABASE`
3. Set different values per environment:

**Preview Environment:**
```
DATABASE_URL → postgresql://...qteria_test...
```

**Production Environment:**
```
DATABASE_URL → postgresql://...qteria_prod...
```

---

## Current Issue: Prefix Conflict

You're seeing this error:
```
This project already has an existing environment variable with name
DATABASE_POSTGRES_URL in one of the chosen environments
```

### Solution:

#### Step 1: Check Existing Variables in Vercel

Go to: **Vercel → Settings → Environment Variables**

Find: `DATABASE_POSTGRES_URL`

You'll see which environments it's used in:
- [ ] Development
- [ ] Preview
- [ ] Production

#### Step 2: Decide Strategy

**Strategy 1: Keep Using DATABASE_POSTGRES_URL**
- Keep the existing variable
- Click "Cancel" in Neon dialog
- Manually set different values per environment
- Update your code to read `DATABASE_POSTGRES_URL` instead of `DATABASE_URL`

**Strategy 2: Use Different Prefix (TEST)**
- Use prefix `TEST` in Neon integration
- Update your code to read from `TEST_URL`
- Simpler for now

**Strategy 3: Delete Old Variable (Recommended)**
- Delete `DATABASE_POSTGRES_URL` from Vercel
- Reconnect Neon with prefix `DATABASE`
- Properly configure per environment

---

## Recommended Setup (Step by Step):

### Phase 1: Development (NOW)
✅ Local: `.env` → `qteria-db`
✅ Tests: `.env.test` → `qteria-test`
✅ Vercel: Ignore for now (not deploying yet)

### Phase 2: Preview/Testing (When Ready to Deploy)
1. Create Vercel Preview environment variable: `DATABASE_URL` → `qteria-test`
2. Every PR gets deployed to Vercel with test database
3. Safe to test without affecting dev work

### Phase 3: Production (When Launching)
1. Create `qteria-prod` database in Neon
2. Create Vercel Production environment variable: `DATABASE_URL` → `qteria-prod`
3. Deploy main branch to production
4. Production uses separate database from dev/test

---

## Migration Path

### Today (Development Phase):
```
You → Local Dev → qteria-db
Tests → pytest → qteria-test
Vercel → Not used yet
```

### Next Week (Preview Deployments):
```
You → Local Dev → qteria-db
Tests → pytest → qteria-test
Team → Preview URLs → qteria-test (same as tests)
```

### Launch Day (Production):
```
You → Local Dev → qteria-db
Tests → pytest → qteria-test
Customers → qteria.com → qteria-prod (NEW DATABASE)
```

---

## What To Do Right Now:

Since you're in **development phase** and not launching to customers yet:

### Option 1: Simple (Use TEST prefix)
1. In Neon dialog: Use prefix `TEST`
2. Click "Connect"
3. Update `.env.test` with the connection string
4. When launching to production later:
   - Your code reads `DATABASE_URL` from environment
   - Vercel will set different `DATABASE_URL` for production vs preview

### Option 2: Proper (Use DATABASE prefix)
1. Go to Vercel Settings → Environment Variables
2. Find `DATABASE_POSTGRES_URL`
3. Delete it or change name
4. Go back to Neon dialog
5. Use prefix `DATABASE`
6. Click "Connect"

---

## Code Configuration (No Changes Needed!)

Your `app/core/config.py` already reads `DATABASE_URL`:

```python
DATABASE_URL: str = Field(
    ..., description="PostgreSQL database URL (pooled connection)"
)
```

This means:
- Locally: reads from `.env`
- In Vercel Preview: reads from Preview environment variable
- In Vercel Production: reads from Production environment variable

**You don't need to change code when moving to production!**

---

## TL;DR

### Right Now:
1. **Click "Connect"** with prefix `TEST` (easiest)
2. Copy connection string to `.env.test`
3. Tests will work

### Later (Before Production Launch):
1. Create `qteria-prod` database in Neon
2. In Vercel → Settings → Environment Variables:
   - Set `DATABASE_URL` for **Production** environment → `qteria-prod` connection string
   - Set `DATABASE_URL` for **Preview** environment → `qteria-test` connection string
3. Deploy - Vercel handles the rest

### Key Point:
**You're NOT deploying to production yet**, so the current setup is fine. When you're ready to launch, you'll:
1. Create production database
2. Set production environment variables
3. Deploy

**No code changes needed** - just configuration in Vercel dashboard.

---

**Last Updated:** 2025-11-24
**Current Phase:** Development (local + tests)
**Next Phase:** Preview deployments (when team wants to test)
**Future Phase:** Production launch (when ready for customers)
