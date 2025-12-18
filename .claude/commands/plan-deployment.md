---
description: Session 13 - Create deployment strategy and CI/CD pipeline plan
---

# Plan Deployment (Session 13 - Core)

You are helping the user create a comprehensive deployment strategy including CI/CD pipelines, environments, rollout procedures, and rollback plans. This is a core session that prepares your product for production deployment.

## When to Use This

**Run AFTER Session 12** (`/scaffold-project`):

- You have a working development environment and need deployment strategy
- You're ready to plan production infrastructure
- You want CI/CD automation from day one

**This is now a CORE session** because:

- Every product needs a deployment strategy to ship
- CI/CD and infrastructure decisions are foundational, not optional
- Deployment planning ensures reliable delivery of journey value

## Your Task

Create a comprehensive deployment strategy using the prompt in `/prompts/operations/deployment.md`.

### Steps to Execute

1. **Read the deployment prompt**:

   ```bash
   Read /prompts/operations/deployment.md
   ```

2. **Read the template structure**:

   ```bash
   Read templates/13-deployment-plan-template.md
   ```

3. **Check for architecture from Session 4** (recommended):

   ```bash
   Read product-guidelines/04-architecture.md
   ```

   - Understand system components and dependencies
   - Identify deployment requirements

4. **Check for tech stack from Session 3** (recommended):

   ```bash
   Read product-guidelines/02-tech-stack.md
   ```

   - Know what needs to be deployed (frontend, backend, database, etc.)

5. **Interview the user** following the deployment prompt:
   - **Current state**: How do you deploy now? What's painful?
   - **Environments**: How many? (dev, staging, prod? More?)
   - **CI/CD**: What needs to happen on every commit? Tests? Linting? Build?
   - **Deployment strategy**: Blue-green? Rolling? Canary? Feature flags?
   - **Infrastructure**: Cloud provider? Kubernetes? Serverless? VMs?
   - **Secrets management**: How to handle API keys, credentials?
   - **Database migrations**: How to manage schema changes?
   - **Rollback**: What's your rollback procedure?
   - **Monitoring**: How to know if deployment succeeded?
   - **Runbooks**: What could go wrong? How to fix?

6. **Develop deployment plan**:
   - Environment strategy (dev, staging, prod + ephemeral)
   - CI/CD pipeline (detailed workflow for each repo/service)
   - Deployment patterns (rolling, canary, feature flags)
   - Infrastructure as Code (Terraform, CloudFormation, etc.)
   - Secrets management (Vault, AWS Secrets Manager, etc.)
   - Database migration strategy
   - Rollback procedures
   - Deploy checklist
   - Runbooks for common issues
   - Security considerations
   - Cost optimization

7. **Write the output**:
   ```bash
   Write product-guidelines/13-deployment-plan.md
   ```

## Output Location

`product-guidelines/13-deployment-plan.md`

This will be used by:

- Engineers setting up CI/CD
- DevOps/Platform teams managing infrastructure
- Product managers understanding deploy cadence
- On-call engineers executing rollbacks

## Template Structure

The output follows this structure:

- Deployment Strategy Overview
- Environment Architecture (dev, staging, prod)
- CI/CD Pipeline Specifications
- Deployment Patterns (rolling, canary, blue-green)
- Infrastructure as Code Setup
- Secrets and Configuration Management
- Database Migration Strategy
- Rollback Procedures
- Pre-deployment Checklist
- Post-deployment Verification
- Runbooks (common failure scenarios)
- Security and Compliance
- Cost Optimization
- Future Improvements

## Key Principles

1. **Automate everything** - Manual deploys create inconsistency
2. **Test in production-like** - Staging should mirror prod
3. **Deploy frequently** - Small deploys = lower risk
4. **Always have rollback** - Things will go wrong
5. **Monitor deploys** - Deployment is not done when code ships
6. **Document procedures** - Runbooks save 2am debugging
7. **Security by default** - Secrets never in code, principle of least privilege

## Example Prompt Flow

```
You: Let's plan your deployment strategy. First, let me check your tech stack and architecture...

[Read product-guidelines/02-tech-stack.md and product-guidelines/04-architecture.md]

You: Got it - you have [frontend] + [backend] + [database]. How do you deploy today? What's painful?

User: [Describes current state]

You: I see. Let's design a better system. How many environments do you need? Most teams use dev (local), staging (pre-prod), and prod. Do you need more?

User: [Describes environments]

You: Perfect. Now let's design your CI/CD pipeline. When you push to main, what should happen automatically?
- Run tests?
- Lint code?
- Build artifacts?
- Deploy to staging?
- Deploy to prod (with approval)?

User: [Describes desired workflow]

You: Great. Now deployment strategy. Do you want:
- **Rolling**: Deploy gradually across servers (zero downtime)
- **Blue-green**: Deploy to new environment, switch traffic (easy rollback)
- **Canary**: Deploy to 5%, monitor, then 100% (lowest risk)
- **Feature flags**: Deploy code hidden, enable features gradually

User: [Chooses strategy]

You: Excellent choice. Now infrastructure - are you on AWS, GCP, Azure? Using Kubernetes? Serverless? VMs?

User: [Describes infrastructure]

You: Perfect. How do you handle secrets? API keys, database credentials, etc.

User: [Describes secrets management]

You: Great. What about database migrations? How do you change schema without downtime?

User: [Describes migration strategy]

You: And rollback - if a deploy goes bad, what's the procedure? How fast can you roll back?

User: [Describes rollback]

[Continue through monitoring, runbooks, security...]

You: Excellent! I've created your deployment plan in product-guidelines/13-deployment-plan.md:
- 3 environments (dev, staging, prod) with ephemeral preview environments
- CI/CD pipeline (GitHub Actions): lint → test → build → deploy
- Canary deployment pattern (5% → 50% → 100% with auto-rollback)
- Infrastructure as Code (Terraform) for AWS
- Secrets management (AWS Secrets Manager + env vars)
- Database migrations (Flyway with zero-downtime patterns)
- Rollback procedure (< 5 min to previous version)
- Pre-deploy checklist (8 items)
- Post-deploy verification (health checks, smoke tests)
- 6 runbooks (DB down, high error rate, etc.)
- Security: least privilege, secrets rotation, audit logging
- Estimated cost: $[X]/month at launch scale

Ready to implement? Start with the CI/CD pipeline setup.
```

## After This Session

**Implementation steps**:

1. Set up CI/CD pipeline (GitHub Actions, CircleCI, etc.)
2. Create infrastructure as code (Terraform, Pulumi, etc.)
3. Configure environments (dev, staging, prod)
4. Implement secrets management
5. Test deployment with a simple change
6. Document runbooks for your team

**Use this document**:

- When setting up new services
- When onboarding engineers
- When debugging deployment issues
- When planning infrastructure changes

---

**Remember**: This is a CORE session. Good deployment strategy = faster shipping and less stress. Deployment planning is essential for reliably delivering journey value to users.
