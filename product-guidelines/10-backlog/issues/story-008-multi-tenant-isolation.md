# [STORY-008] Multi-Tenant Isolation Middleware

**Type**: Story
**Epic**: EPIC-02 (Authentication & Authorization)
**Journey Step**: Foundation (Data Security)
**Priority**: P0 (CRITICAL for Data Privacy)
**RICE Score**: 300 (R:100 × I:3 × C:100% ÷ E:1)

---

## User Value

**Job-to-Be-Done**: When multiple organizations use the platform (TÜV SÜD, BSI, etc.), they need absolute data isolation, so that TÜV SÜD employees can NEVER see BSI's certification documents, even by mistake or malicious intent.

**Value Delivered**: Bulletproof multi-tenant isolation that automatically filters all database queries by organization_id, preventing data leakage between organizations.

**Success Metric**: 100% of database queries filtered by organization_id, zero cross-organization data access incidents.

---

## Acceptance Criteria

- [ ] FastAPI middleware extracts `organization_id` from JWT token
- [ ] All database queries automatically filtered by `organization_id`
- [ ] SQLAlchemy session scoped to organization (automatic filtering)
- [ ] Users from org A cannot access org B's data (workflows, assessments, documents)
- [ ] Admin users can only see their own organization's data (no cross-org admin)
- [ ] Multi-tenancy enforced at middleware level (not per-endpoint)
- [ ] Security tests validate isolation (100% coverage)
- [ ] Audit logs track organization_id for all operations

---

## Technical Approach

**Tech Stack Components Used**:
- Backend: FastAPI middleware
- ORM: SQLAlchemy query filters
- JWT: organization_id in token payload

**Multi-Tenant Middleware** (`app/middleware/multi_tenant.py`):
```python
from fastapi import Request
from app.dependencies.auth import get_current_user
from app.database import get_db

class MultiTenantMiddleware:
    """Automatically filter queries by organization_id"""

    async def __call__(self, request: Request, call_next):
        # Extract organization_id from JWT
        user = await get_current_user(request)
        organization_id = user["organization_id"]

        # Store in request state for query filtering
        request.state.organization_id = organization_id

        response = await call_next(request)
        return response
```

**SQLAlchemy Session Scoping** (`app/database.py`):
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import event
from contextvars import ContextVar

# Store current organization_id in context
current_org_id: ContextVar[str] = ContextVar("current_org_id")

async def get_db(request: Request):
    """Get database session with organization filter"""
    organization_id = request.state.organization_id
    current_org_id.set(organization_id)

    async with AsyncSessionLocal() as session:
        # Add organization_id filter to all queries
        @event.listens_for(session, "after_attach")
        def receive_after_attach(session, instance):
            if hasattr(instance, "organization_id"):
                # Automatically filter by organization
                pass

        yield session

# Automatic query filtering (option 1: SQLAlchemy filter)
class OrganizationFilterMixin:
    """Mixin to automatically filter queries by organization_id"""

    @classmethod
    def query(cls, session: AsyncSession):
        org_id = current_org_id.get()
        return session.query(cls).filter(cls.organization_id == org_id)
```

**Alternative: Query Wrapper** (`app/models/base.py`):
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class OrganizationScopedModel:
    """Base model with automatic organization filtering"""

    @classmethod
    async def get_all(cls, session: AsyncSession, org_id: str):
        """Get all records for organization"""
        result = await session.execute(
            select(cls).where(cls.organization_id == org_id)
        )
        return result.scalars().all()

    @classmethod
    async def get_by_id(cls, session: AsyncSession, org_id: str, record_id: str):
        """Get single record (with org check)"""
        result = await session.execute(
            select(cls)
            .where(cls.organization_id == org_id)
            .where(cls.id == record_id)
        )
        return result.scalar_one_or_none()
```

**Protected Endpoint Example** (`app/api/workflows.py`):
```python
@router.get("/workflows/{workflow_id}")
async def get_workflow(
    workflow_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get workflow (automatically filtered by organization)"""
    workflow = await Workflow.get_by_id(
        db,
        org_id=current_user["organization_id"],
        record_id=workflow_id
    )

    if not workflow:
        # Either doesn't exist or belongs to different org
        raise HTTPException(status_code=404, detail="Workflow not found")

    return workflow
```

**Security Test Example**:
```python
def test_multi_tenant_isolation():
    """User from org A cannot access org B's data"""
    # Create workflow for org A
    workflow_a = create_workflow(org_id="org_a", name="Workflow A")

    # Login as user from org B
    user_b_token = login(user_id="user_b", org_id="org_b")

    # Try to access org A's workflow
    response = client.get(
        f"/workflows/{workflow_a.id}",
        headers={"Authorization": f"Bearer {user_b_token}"}
    )

    # Should return 404 (not 403, to avoid leaking existence)
    assert response.status_code == 404
    assert "Workflow not found" in response.json()["detail"]
```

---

## Dependencies

- **Blocked By**:
  - STORY-005 (User Login) - need organization_id in JWT
  - STORY-007 (RBAC) - need authentication middleware first
- **Blocks**:
  - EPIC-03 (Workflow Management) - workflows must be org-scoped
  - ALL user-facing features - everything needs multi-tenancy

---

## Estimation

**Effort**: 1 person-day

**Breakdown**:
- Middleware setup: 0.25 days (extract org_id from JWT)
- SQLAlchemy filtering: 0.5 days (automatic query scoping)
- Testing: 0.25 days (multi-tenant isolation tests)

---

## Definition of Done

- [ ] Middleware extracts organization_id from JWT
- [ ] All models use organization-scoped queries
- [ ] User from org A cannot access org B's workflows
- [ ] User from org A cannot access org B's assessments
- [ ] User from org A cannot access org B's documents
- [ ] 404 returned (not 403) when accessing other org's data (prevents info leakage)
- [ ] Security tests pass (100% coverage of cross-org access attempts)
- [ ] Audit logs include organization_id for all operations
- [ ] Code reviewed and merged to main

---

## Testing Requirements

**Security Tests** (100% coverage required):
- [ ] User A tries to GET user B's workflow → 404 Not Found
- [ ] User A tries to DELETE user B's workflow → 404 Not Found
- [ ] User A tries to UPDATE user B's assessment → 404 Not Found
- [ ] User A lists workflows → only sees org A workflows (not org B)
- [ ] User A lists users → only sees org A users (not org B)
- [ ] Admin from org A cannot see org B's data (admins are org-scoped)

**Edge Cases**:
- [ ] Workflow with same UUID in both orgs → correct org's workflow returned
- [ ] Join queries (workflow + buckets) → both filtered by org_id
- [ ] Aggregation queries (count assessments) → scoped to org
- [ ] User switches organizations → new JWT with new org_id → sees new org's data

**Performance Tests**:
- [ ] Query filtering adds <5ms latency
- [ ] Index on organization_id exists (fast filtering)

---

## Risks & Mitigations

**Risk**: Developer forgets to filter by organization_id → data leak
- **Mitigation**: Enforce at middleware level (automatic filtering), use base model with built-in org checks, 100% test coverage

**Risk**: SQL injection bypasses organization filter
- **Mitigation**: Use ORM (SQLAlchemy) for all queries (parameterized queries), never use raw SQL

**Risk**: JOIN queries leak data from other organizations
- **Mitigation**: Ensure all joined tables also filtered by organization_id, test all relationships

**Risk**: Admin bypasses multi-tenancy to see all orgs (intentional backdoor)
- **Mitigation**: NO super-admin role in MVP - admins are org-scoped, add super-admin cautiously in Year 2 with strict audit logs

---

## Notes

- This is the **highest RICE score story** (300) - absolutely critical for data security
- Multi-tenancy must be **automatic and transparent** - developers shouldn't need to remember to filter by org_id
- Return 404 (not 403) when accessing other org's data to avoid leaking existence information
- Consider using row-level security (RLS) in PostgreSQL for defense-in-depth (STORY-008B)
- After completing this story, EPIC-02 is DONE → proceed to EPIC-03 (Workflow Management)
- SOC2 compliance requires multi-tenancy audit trail - ensure audit_logs table includes organization_id
