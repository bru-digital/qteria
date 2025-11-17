# [STORY-007] Role-Based Access Control (RBAC)

**Type**: Story
**Epic**: EPIC-02 (Authentication & Authorization)
**Journey Step**: Foundation (Enforces Permissions)
**Priority**: P0 (Critical for Security)
**RICE Score**: 100 (R:100 × I:2 × C:100% ÷ E:2)

---

## User Value

**Job-to-Be-Done**: When users with different responsibilities access the platform, they need role-based permissions enforced, so that Process Managers can create workflows while Project Handlers cannot accidentally delete critical validation templates.

**Value Delivered**: Secure permission enforcement that prevents unauthorized actions, ensuring users can only perform tasks appropriate to their role.

**Success Metric**: 100% of protected endpoints enforce role checks, zero unauthorized access incidents.

---

## Acceptance Criteria

- [ ] Three roles defined: `process_manager`, `project_handler`, `admin`
- [ ] Role stored in JWT token payload (from STORY-005)
- [ ] FastAPI middleware validates JWT and extracts role
- [ ] Role decorator/dependency for protected endpoints (`@require_role("process_manager")`)
- [ ] Insufficient role returns 403 Forbidden with clear error message
- [ ] Admin role has full access to all endpoints
- [ ] Frontend UI shows/hides features based on role (e.g., "Create Workflow" button only for Process Managers)
- [ ] Role permissions documented (who can do what)
- [ ] Security tests validate role enforcement (100% coverage)

---

## Technical Approach

**Tech Stack Components Used**:
- Backend: FastAPI (middleware, dependencies)
- JWT: Role stored in token payload
- Frontend: Next.js (role-based UI rendering)

**Role Definitions**:
```python
from enum import Enum

class UserRole(str, Enum):
    PROCESS_MANAGER = "process_manager"
    PROJECT_HANDLER = "project_handler"
    ADMIN = "admin"

# Permissions
ROLE_PERMISSIONS = {
    UserRole.PROCESS_MANAGER: [
        "workflows:create",
        "workflows:read",
        "workflows:update",
        "workflows:delete",
        "assessments:read",
    ],
    UserRole.PROJECT_HANDLER: [
        "workflows:read",
        "assessments:create",
        "assessments:read",
        "documents:upload",
        "documents:download",
    ],
    UserRole.ADMIN: ["*"]  # All permissions
}
```

**FastAPI Role Dependency** (`app/dependencies/auth.py`):
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.config import settings

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Extract user from JWT token"""
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=["HS256"]
        )
        return {
            "id": payload["sub"],
            "email": payload["email"],
            "role": payload["role"],
            "organization_id": payload["org_id"]
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

def require_role(*allowed_roles: UserRole):
    """Decorator to enforce role-based access"""
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {allowed_roles}"
            )
        return current_user
    return role_checker
```

**Protected Endpoint Example** (`app/api/workflows.py`):
```python
from fastapi import APIRouter, Depends
from app.dependencies.auth import require_role, get_current_user
from app.models import UserRole

router = APIRouter()

@router.post("/workflows")
async def create_workflow(
    workflow: WorkflowCreate,
    current_user: dict = Depends(require_role(UserRole.PROCESS_MANAGER, UserRole.ADMIN))
):
    """Only Process Managers and Admins can create workflows"""
    return {"message": "Workflow created"}

@router.get("/workflows")
async def list_workflows(
    current_user: dict = Depends(get_current_user)
):
    """All authenticated users can list workflows"""
    return {"workflows": []}

@router.delete("/workflows/{workflow_id}")
async def delete_workflow(
    workflow_id: str,
    current_user: dict = Depends(require_role(UserRole.PROCESS_MANAGER, UserRole.ADMIN))
):
    """Only Process Managers and Admins can delete workflows"""
    return {"message": "Workflow deleted"}
```

**Frontend Role-Based UI** (`components/WorkflowActions.tsx`):
```typescript
"use client"
import { useSession } from "next-auth/react"

export function WorkflowActions() {
  const { data: session } = useSession()
  const isProcessManager = session?.user?.role === "process_manager"
  const isAdmin = session?.user?.role === "admin"

  return (
    <>
      {/* All users can view workflows */}
      <button>View Workflows</button>

      {/* Only Process Managers and Admins can create/edit */}
      {(isProcessManager || isAdmin) && (
        <>
          <button>Create Workflow</button>
          <button>Edit Workflow</button>
          <button>Delete Workflow</button>
        </>
      )}
    </>
  )
}
```

---

## Dependencies

- **Blocked By**:
  - STORY-005 (User Login) - need JWT with role in payload
- **Blocks**:
  - EPIC-03 (Workflow Management) - workflows need role enforcement
  - EPIC-04 (Document Processing) - uploads need role checks

---

## Estimation

**Effort**: 2 person-days

**Breakdown**:
- FastAPI middleware: 0.5 days (JWT validation, role extraction)
- Role decorator/dependency: 0.5 days (require_role logic)
- Frontend role-based UI: 0.5 days (show/hide features)
- Testing: 0.5 days (security tests for all roles)

---

## Definition of Done

- [ ] Three roles defined (process_manager, project_handler, admin)
- [ ] JWT includes role in payload
- [ ] FastAPI dependency extracts and validates role
- [ ] `require_role` decorator works on protected endpoints
- [ ] Insufficient role returns 403 Forbidden
- [ ] Admin role can access all endpoints
- [ ] Frontend hides/shows features based on role
- [ ] Role permissions documented
- [ ] Security tests pass (100% coverage of role checks)
- [ ] Code reviewed and merged to main

---

## Testing Requirements

**Security Tests** (100% coverage required):
- [ ] Process Manager can create workflow → 201 Created
- [ ] Project Handler tries to create workflow → 403 Forbidden
- [ ] Admin can create workflow → 201 Created
- [ ] Process Manager can delete workflow → 200 OK
- [ ] Project Handler tries to delete workflow → 403 Forbidden
- [ ] Project Handler can upload document → 201 Created
- [ ] Unauthenticated request → 401 Unauthorized
- [ ] Invalid JWT → 401 Unauthorized

**Functional Tests**:
- [ ] Login as Process Manager → see "Create Workflow" button
- [ ] Login as Project Handler → "Create Workflow" button hidden
- [ ] Login as Admin → see all admin features
- [ ] Role change propagates immediately (no stale permissions)

**Edge Cases**:
- [ ] User role changed in database → old JWT still valid until expiry (acceptable)
- [ ] Multiple roles required → endpoint requires any of [process_manager, admin]
- [ ] No role in JWT → default to lowest permission level

---

## Risks & Mitigations

**Risk**: Role enforcement bypassed (developer forgets to add `require_role`)
- **Mitigation**: Default all new endpoints to require authentication, code review checklist includes role check verification

**Risk**: Frontend hides button but backend allows request
- **Mitigation**: ALWAYS enforce roles on backend (frontend is just UX enhancement), test backend directly

**Risk**: Admin role abused (single admin deletes all workflows)
- **Mitigation**: Audit logs track admin actions (STORY-001 audit_logs table), review admin activity regularly

**Risk**: Role granularity insufficient (need per-workflow permissions)
- **Mitigation**: For MVP, three roles sufficient; consider resource-level permissions in Year 2 (e.g., workflow owner can edit, others read-only)

---

## Notes

- This is **critical for security** - every protected endpoint MUST check roles
- RBAC is simpler than ABAC (Attribute-Based Access Control) - defer fine-grained permissions to post-MVP
- Admin role should be rare (only organization admins) - most users are Process Managers or Project Handlers
- Consider adding "read-only" role for auditors/observers (post-MVP)
- After completing this story, proceed to STORY-008 (Multi-Tenant Isolation) to enforce organization-level data separation
