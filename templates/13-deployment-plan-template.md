# Deployment Strategy

> **Generated**: [Date] > **Product**: [Product Name] > **Status**: [Draft/In Progress/Implemented]

## Overview

This document defines the deployment strategy including environments, CI/CD pipelines, deployment patterns, rollback procedures, and operational runbooks.

---

## Deployment Strategy Overview

### Philosophy

**Deployment frequency**: [Multiple times per day / Daily / Weekly]

**Key principles**:

1. **[Principle 1 - e.g., "Automate everything"]**: [Why this matters]
2. **[Principle 2 - e.g., "Deploy small changes frequently"]**: [Why this matters]
3. **[Principle 3 - e.g., "Always have a rollback plan"]**: [Why this matters]

### Current State

**How we deploy today**:
[Describe current process, pain points]

**What we're changing**:
[New approach, improvements]

---

## Environment Architecture

### Environment Strategy

| Environment     | Purpose                | Data                    | Access        | Deployment                 |
| --------------- | ---------------------- | ----------------------- | ------------- | -------------------------- |
| **Local**       | Development            | Fake/seeded             | All engineers | Manual                     |
| **Development** | Integration testing    | Fake/seeded             | All engineers | Auto on merge to `develop` |
| **Staging**     | Pre-production testing | Production-like or copy | Internal team | Auto on merge to `main`    |
| **Production**  | Live system            | Real customer data      | Admins only   | Manual approval required   |

### Additional Environments (Optional)

**Preview/Ephemeral**: [Per PR, auto-deployed, auto-destroyed]
**Demo**: [For sales demos, stable, production-like data]
**Load Testing**: [For performance testing, scaled environment]

---

### Environment Specifications

#### Local Development

**Infrastructure**: Docker Compose / Local services

**Services**:

- [Service 1]: [How it runs locally]
- [Service 2]: [How it runs locally]
- Database: [PostgreSQL via Docker]

**Setup**: `npm run dev` or [command]

**Data**: Seeded with `npm run seed`

---

#### Development Environment

**Infrastructure**: [AWS ECS / Kubernetes / Vercel / etc.]

**URL**: `https://dev.example.com`

**Services**:

- [Service 1]: [Configuration]
- [Service 2]: [Configuration]
- Database: [RDS/managed DB]

**Deployment trigger**: Merge to `develop` branch

**Purpose**: Integration testing, feature branches

---

#### Staging Environment

**Infrastructure**: [Same as production]

**URL**: `https://staging.example.com`

**Services**: [Same as production configuration]

**Deployment trigger**: Merge to `main` branch

**Purpose**: Final QA before production

**Data strategy**: [Copy of production / Production-like fake data]

---

#### Production Environment

**Infrastructure**: [AWS / GCP / Azure / Multi-cloud]

**URL**: `https://example.com`

**Services**:

- [Service 1]: [Configuration]
- [Service 2]: [Configuration]
- Database: [Configuration]

**Deployment trigger**: Manual approval after staging verification

**Purpose**: Live customer traffic

**High availability**: [Multi-AZ / Multi-region setup]

---

## CI/CD Pipeline

### Pipeline Architecture

```
Code Push → GitHub
    ↓
Trigger CI/CD (GitHub Actions / CircleCI / etc.)
    ↓
┌─────────────────┐
│  Build Stage    │
│  - Lint         │
│  - Test         │
│  - Build        │
└─────────────────┘
    ↓
┌─────────────────┐
│  Security       │
│  - Dependency   │
│  - SAST         │
│  - Secrets scan │
└─────────────────┘
    ↓
┌─────────────────┐
│  Package        │
│  - Docker build │
│  - Push to      │
│    registry     │
└─────────────────┘
    ↓
┌─────────────────┐
│  Deploy         │
│  - Dev (auto)   │
│  - Staging      │
│    (auto)       │
│  - Prod         │
│    (manual)     │
└─────────────────┘
    ↓
┌─────────────────┐
│  Verify         │
│  - Smoke tests  │
│  - Health check │
│  - Alerts       │
└─────────────────┘
```

---

### Pipeline Configuration

#### Build Stage

**Linting**:

```yaml
- name: Lint
  run: npm run lint
  # Must pass for pipeline to continue
```

**Testing**:

```yaml
- name: Unit Tests
  run: npm test
  # Must pass for pipeline to continue

- name: Integration Tests
  run: npm run test:integration
  # Must pass for pipeline to continue

- name: Coverage Check
  run: npm run test:coverage
  # Require 80% coverage
```

**Build**:

```yaml
- name: Build
  run: npm run build
  # Compile TypeScript, bundle assets, etc.
```

**Estimated duration**: [X] minutes

---

#### Security Stage

**Dependency scanning**:

```yaml
- name: Dependency Audit
  run: npm audit --audit-level=moderate
  # Fail on moderate+ vulnerabilities
```

**SAST (Static Application Security Testing)**:

```yaml
- name: SAST
  uses: [tool-like-snyk-or-sonarqube]
  # Scan code for vulnerabilities
```

**Secrets scanning**:

```yaml
- name: Secrets Scan
  uses: trufflesecurity/trufflehog
  # Ensure no secrets in code
```

**Estimated duration**: [X] minutes

---

#### Package Stage

**Docker build**:

```dockerfile
# Multi-stage build for optimization
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

**Image tagging**:

- `latest` (latest from main)
- `v1.2.3` (semantic version)
- `sha-abc123` (git commit SHA)

**Registry**: [Docker Hub / ECR / GCR / ACR]

**Estimated duration**: [X] minutes

---

#### Deploy Stage

**Development**:

```yaml
- name: Deploy to Dev
  if: github.ref == 'refs/heads/develop'
  run: |
    # Deploy to development environment
    # Auto-deploy, no approval needed
```

**Staging**:

```yaml
- name: Deploy to Staging
  if: github.ref == 'refs/heads/main'
  run: |
    # Deploy to staging environment
    # Auto-deploy, no approval needed
```

**Production**:

```yaml
- name: Deploy to Production
  if: github.ref == 'refs/heads/main'
  environment:
    name: production
    url: https://example.com
  needs: [deploy-staging, run-smoke-tests]
  # Requires manual approval
```

**Estimated duration**: [X] minutes per environment

---

#### Verify Stage

**Health checks**:

```bash
# Check service is responding
curl https://[env].example.com/health

# Expected: 200 OK
{"status": "healthy", "version": "1.2.3"}
```

**Smoke tests**:

```bash
# Run critical path tests
npm run test:smoke

# Tests:
# - User can sign up
# - User can log in
# - Core action works
# - API returns correct data
```

**Monitoring alerts**:

- Check error rate (should be < 1%)
- Check latency (p95 < 500ms)
- Check traffic (expected levels)

**Estimated duration**: [X] minutes

---

## Deployment Patterns

### Chosen Pattern: [Rolling / Blue-Green / Canary]

**Why this pattern**: [Reasoning]

---

### Pattern 1: Rolling Deployment _(if chosen)_

**How it works**:

1. Deploy to subset of servers (e.g., 1 at a time)
2. Wait for health checks
3. Continue to next servers
4. Complete when all servers updated

**Pros**:

- Zero downtime
- Simple infrastructure
- Gradual rollout

**Cons**:

- Temporary mixed versions
- Harder to rollback all at once

**Configuration**:

```yaml
strategy:
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0
```

---

### Pattern 2: Blue-Green Deployment _(if chosen)_

**How it works**:

1. Deploy new version to "green" environment
2. Test green environment
3. Switch traffic from "blue" to "green"
4. Keep blue for quick rollback

**Pros**:

- Instant rollback (switch back to blue)
- Full testing before traffic switch
- No mixed versions

**Cons**:

- Requires double infrastructure
- Database migrations tricky

**Configuration**:

```yaml
# Two identical environments
# Traffic switching via load balancer/DNS
```

---

### Pattern 3: Canary Deployment _(if chosen)_

**How it works**:

1. Deploy new version to small % of traffic (e.g., 5%)
2. Monitor metrics (errors, latency, conversion)
3. If healthy, increase to 25%, 50%, 100%
4. If unhealthy, rollback immediately

**Pros**:

- Lowest risk (limited blast radius)
- Gradual validation with real traffic
- Auto-rollback on errors

**Cons**:

- Complex infrastructure
- Requires feature flags
- Longer deployment time

**Configuration**:

```yaml
canary:
  steps:
    - setWeight: 5 # 5% traffic
    - pause: { duration: 10m }
    - setWeight: 25
    - pause: { duration: 10m }
    - setWeight: 50
    - pause: { duration: 10m }
    - setWeight: 100
```

---

## Infrastructure as Code

### Tool: [Terraform / Pulumi / CloudFormation / CDK]

**Why**: [Reasoning]

**Repository**: `infrastructure/` or separate repo

**Structure**:

```
infrastructure/
├── modules/
│   ├── networking/
│   ├── compute/
│   ├── database/
│   └── monitoring/
├── environments/
│   ├── dev/
│   ├── staging/
│   └── production/
└── scripts/
    ├── apply.sh
    └── destroy.sh
```

**Example**: [Show sample Terraform]

```hcl
# Example: Terraform for production
resource "aws_ecs_cluster" "main" {
  name = "production-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_service" "api" {
  name            = "api-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = 3

  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "api"
    container_port   = 3000
  }
}
```

---

## Secrets and Configuration Management

### Secrets Strategy

**Tool**: [AWS Secrets Manager / HashiCorp Vault / Doppler]

**What goes in secrets**:

- ✅ Database credentials
- ✅ API keys (third-party services)
- ✅ Encryption keys
- ✅ OAuth client secrets

**What goes in environment variables** (not secret):

- ✅ Feature flags
- ✅ Public API endpoints
- ✅ Environment name

**Rotation policy**: [Every 90 days / On employee departure / As needed]

---

### Configuration Management

**Environment variables**:

```bash
# .env.development
NODE_ENV=development
API_URL=https://api.dev.example.com
LOG_LEVEL=debug

# .env.production
NODE_ENV=production
API_URL=https://api.example.com
LOG_LEVEL=info
```

**Never commit**:

- ❌ `.env` files (use `.env.example`)
- ❌ Secrets or credentials
- ❌ API keys

**Access control**:

- Developers: Read access to dev/staging secrets
- Ops: Read/write access to all environments
- CI/CD: Read access via service account

---

## Database Migration Strategy

### Migration Tool: [Flyway / Liquibase / Prisma / Sequelize]

**Migration workflow**:

1. **Develop migration** (in feature branch):

   ```sql
   -- migrations/001_add_user_email.sql
   ALTER TABLE users ADD COLUMN email VARCHAR(255);
   CREATE INDEX idx_users_email ON users(email);
   ```

2. **Test locally** (run migration on local DB)

3. **Review** (include migrations in PR)

4. **Deploy**:
   - Staging: Auto-run migrations before deploy
   - Production: Manual approval to run migrations

### Zero-Downtime Migrations

**For breaking changes**:

**Step 1**: Add new column (backward compatible)

```sql
ALTER TABLE users ADD COLUMN email_new VARCHAR(255);
```

**Step 2**: Dual write (code writes to both columns)

```javascript
user.email = email
user.email_new = email // Dual write
```

**Step 3**: Backfill data

```sql
UPDATE users SET email_new = email WHERE email_new IS NULL;
```

**Step 4**: Switch reads (code reads from new column)

```javascript
const email = user.email_new || user.email
```

**Step 5**: Drop old column (after verification)

```sql
ALTER TABLE users DROP COLUMN email;
ALTER TABLE users RENAME COLUMN email_new TO email;
```

**Timeline**: [Weeks or months, not single deploy]

---

## Rollback Procedures

### When to Rollback

**Automatic rollback triggers**:

- Error rate > [5%]
- Latency p95 > [2x baseline]
- Health checks failing
- Database connection errors

**Manual rollback decision**:

- Critical bug discovered
- Data corruption detected
- Security vulnerability

### Rollback Methods

**Method 1: Revert deployment**

```bash
# Kubernetes example
kubectl rollout undo deployment/api-deployment

# Expected duration: < 2 minutes
```

**Method 2: Deploy previous version**

```bash
# Deploy specific version
./deploy.sh --version v1.2.2 --env production

# Expected duration: < 5 minutes
```

**Method 3: Traffic switch** (Blue-Green)

```bash
# Switch load balancer to previous environment
aws elbv2 modify-listener --listener-arn [ARN] --default-actions TargetGroupArn=[blue-target-group]

# Expected duration: < 30 seconds
```

**Method 4: Feature flag kill switch**

```javascript
// Disable feature immediately
featureFlags.disable('new-checkout-flow')

// Expected duration: < 10 seconds
```

---

### Rollback Checklist

When rolling back:

- [ ] **Announce** in #incidents channel
- [ ] **Determine** rollback method
- [ ] **Execute** rollback
- [ ] **Verify** error rate returns to normal
- [ ] **Verify** latency returns to normal
- [ ] **Communicate** status to users (if customer-facing)
- [ ] **Schedule** post-mortem
- [ ] **Create** issue to fix underlying problem

**Expected time to rollback**: [< 5 minutes]

---

## Pre-Deployment Checklist

Before deploying to production:

### Code Quality

- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] No merge conflicts
- [ ] Linting passing
- [ ] Test coverage meets minimum ([X%])

### Testing

- [ ] Manual testing in staging complete
- [ ] Smoke tests passing
- [ ] No critical bugs
- [ ] Performance tests passing (if applicable)

### Migrations

- [ ] Database migrations reviewed
- [ ] Migration tested in staging
- [ ] Rollback plan for migrations

### Communication

- [ ] Team notified of deploy
- [ ] Customers notified (if breaking changes)
- [ ] On-call engineer available
- [ ] Rollback plan documented

### Infrastructure

- [ ] Infrastructure changes applied (if any)
- [ ] Secrets updated (if needed)
- [ ] Environment variables configured

### Monitoring

- [ ] Alerts configured
- [ ] Dashboards ready
- [ ] On-call rotation scheduled

---

## Post-Deployment Verification

After deploying:

### Immediate (0-5 minutes)

- [ ] Health checks passing
- [ ] Smoke tests passing
- [ ] Error rate normal
- [ ] Latency normal
- [ ] No alerts firing

### Short-term (5-30 minutes)

- [ ] User actions succeeding (login, core action)
- [ ] Database queries performing well
- [ ] Third-party integrations working
- [ ] Background jobs running

### Medium-term (30 minutes - 2 hours)

- [ ] Conversion rates normal
- [ ] No increase in support tickets
- [ ] No customer complaints
- [ ] Metrics trending as expected

---

## Runbooks

### Runbook 1: Database Connection Failure

**Symptoms**:

- Health checks failing
- API returning 500 errors
- Logs show "Cannot connect to database"

**Diagnosis**:

1. Check database status in AWS RDS console
2. Check security groups (DB accessible from app?)
3. Check credentials in secrets manager

**Fix**:

- If DB down: Restore from backup or wait for AWS to restore
- If credentials wrong: Rotate credentials, redeploy
- If network issue: Fix security group rules

**Rollback**: If unfixable quickly, rollback deployment

---

### Runbook 2: High Error Rate After Deploy

**Symptoms**:

- Error rate > 5%
- Customers reporting issues
- Alerts firing

**Diagnosis**:

1. Check logs for common errors
2. Check which endpoints failing
3. Check if specific to new code

**Fix**:

- If new code: Rollback immediately
- If bad data: Fix data, may not need rollback
- If third-party: Wait for third-party, consider feature flag disable

**Rollback**: Roll back if error rate > 10% or affecting > 50% of users

---

### Runbook 3: Slow Performance After Deploy

**Symptoms**:

- Latency p95 > [baseline × 2]
- Customers reporting slowness
- Latency alerts firing

**Diagnosis**:

1. Check APM tool for slow endpoints
2. Check database query times
3. Check if new code introduced N+1 queries

**Fix**:

- If new code: Rollback and optimize
- If database: Add index, optimize query
- If third-party: Cache or disable feature

**Rollback**: Roll back if p95 > [baseline × 3]

---

_[Add 5-10 runbooks for common issues]_

---

## Security Considerations

### Access Control

**Who can deploy**:

- **Development**: All engineers (via CI/CD)
- **Staging**: All engineers (via CI/CD)
- **Production**: [Ops team / Senior engineers] (manual approval)

**Service accounts**:

- CI/CD service account (least privilege)
- Monitoring service account (read-only)

### Secrets Management

**Best practices**:

- ✅ Rotate secrets every 90 days
- ✅ Use unique secrets per environment
- ✅ Never log secrets
- ✅ Encrypt secrets at rest
- ✅ Audit secret access

### Network Security

**Firewall rules**:

- Database: Only accessible from app servers
- App servers: Only accessible from load balancer
- SSH: Only accessible from VPN/bastion

**Encryption**:

- ✅ TLS 1.3 for all traffic
- ✅ Data encrypted at rest
- ✅ Secrets encrypted in transit and at rest

---

## Cost Optimization

### Infrastructure Costs

**Current monthly cost**: $[X]

**Breakdown**:

- Compute: $[X] ([Y]%)
- Database: $[X] ([Y]%)
- Storage: $[X] ([Y]%)
- Networking: $[X] ([Y]%)
- Monitoring: $[X] ([Y]%)

### Optimization Strategies

1. **[Strategy 1 - e.g., "Auto-scale down in non-business hours"]**: Savings $[X]/month
2. **[Strategy 2 - e.g., "Use reserved instances"]**: Savings $[X]/month
3. **[Strategy 3]**: Savings $[X]/month

**Projected savings**: $[X]/month ([Y]%)

---

## Future Improvements

**Short-term** (next 3 months):

- [ ] [Improvement 1 - e.g., "Add preview environments for PRs"]
- [ ] [Improvement 2 - e.g., "Implement feature flags"]
- [ ] [Improvement 3]

**Long-term** (6-12 months):

- [ ] [Improvement 1 - e.g., "Multi-region deployment"]
- [ ] [Improvement 2 - e.g., "Automated canary analysis"]
- [ ] [Improvement 3]

---

## Document Control

**Status**: [Draft/In Progress/Implemented]
**Last Updated**: [Date]
**Next Review**: [Quarterly]
**Owner**: [Name/Role - DevOps/Platform]
**On-Call Rotation**: [Link to PagerDuty/schedule]
