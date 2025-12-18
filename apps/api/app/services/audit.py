"""
Audit logging service for SOC2/ISO 27001 compliance.

This module provides centralized audit logging for security-critical events,
including authentication and authorization events.

Usage:
    from app.services.audit import AuditService, AuditEventType
    from app.core.dependencies import get_db

    async def login_endpoint(request: Request, db: Session = Depends(get_db)):
        # Log successful login
        AuditService.log_auth_event(
            db=db,
            event_type=AuditEventType.AUTH_LOGIN_SUCCESS,
            user_id=user.id,
            organization_id=user.organization_id,
            request=request,
            metadata={"method": "password"}
        )
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import UUID
import logging

from fastapi import Request
from sqlalchemy.orm import Session

from app.models.models import AuditLog

logger = logging.getLogger(__name__)


class AuditEventType(str, Enum):
    """
    Audit event types for auth/authz tracking.

    Categories:
    - AUTH_*: Authentication events (login, logout, token operations)
    - AUTHZ_*: Authorization events (permission checks, role enforcement)
    - SECURITY_*: Security-related events (suspicious activity, rate limits)
    """

    # Authentication events
    AUTH_LOGIN_SUCCESS = "auth.login.success"
    AUTH_LOGIN_FAILURE = "auth.login.failure"
    AUTH_LOGOUT = "auth.logout"
    AUTH_TOKEN_REFRESH = "auth.token.refresh"
    AUTH_TOKEN_INVALID = "auth.token.invalid"
    AUTH_TOKEN_EXPIRED = "auth.token.expired"
    AUTH_TOKEN_MALFORMED = "auth.token.malformed"

    # Authorization events
    AUTHZ_ACCESS_GRANTED = "authz.access.granted"
    AUTHZ_ACCESS_DENIED = "authz.access.denied"
    AUTHZ_ROLE_CHECK_FAILED = "authz.role.check_failed"
    AUTHZ_PERMISSION_CHECK_FAILED = "authz.permission.check_failed"
    AUTHZ_MULTI_TENANCY_VIOLATION = "authz.multi_tenancy.violation"

    # Security events
    SECURITY_SUSPICIOUS_ACTIVITY = "security.suspicious_activity"
    SECURITY_RATE_LIMIT_EXCEEDED = "security.rate_limit.exceeded"
    SECURITY_INVALID_REQUEST = "security.invalid_request"


class AuditService:
    """
    Service for creating immutable audit log entries.

    All audit methods are static for ease of use in dependencies and endpoints.
    Logs are stored in the audit_logs table and cannot be modified or deleted
    (immutable trail for compliance).
    """

    @staticmethod
    def _extract_request_info(request: Optional[Request]) -> tuple[Optional[str], Optional[str]]:
        """Extract IP address and user agent from request."""
        if not request:
            return None, None

        # Get IP address (handle proxied requests)
        ip_address = None
        if request.client:
            ip_address = request.client.host
        # Check for forwarded IP (behind proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            ip_address = forwarded_for.split(",")[0].strip()

        user_agent = request.headers.get("User-Agent")

        return ip_address, user_agent

    @staticmethod
    def log_event(
        db: Session,
        action: str,
        organization_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[UUID] = None,
        metadata: Optional[dict[str, Any]] = None,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """
        Create a generic audit log entry.

        Args:
            db: Database session
            action: Action performed (use AuditEventType values)
            organization_id: Organization context (required for multi-tenant isolation)
            user_id: User who performed the action (if authenticated)
            resource_type: Type of resource affected (e.g., "workflow", "assessment")
            resource_id: ID of the affected resource
            metadata: Additional context as JSON
            request: FastAPI request for IP/User-Agent extraction

        Returns:
            AuditLog: Created audit log entry
        """
        ip_address, user_agent = AuditService._extract_request_info(request)

        audit_entry = AuditLog(
            organization_id=organization_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            action_metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        db.add(audit_entry)
        db.commit()
        db.refresh(audit_entry)

        # Also log to structured logger for real-time monitoring
        logger.info(
            "audit_event",
            extra={
                "audit_id": str(audit_entry.id),
                "action": action,
                "organization_id": str(organization_id) if organization_id else None,
                "user_id": str(user_id) if user_id else None,
                "resource_type": resource_type,
                "resource_id": str(resource_id) if resource_id else None,
                "ip_address": ip_address,
                "metadata": metadata,
            },
        )

        return audit_entry

    @staticmethod
    def log_auth_success(
        db: Session,
        user_id: UUID,
        organization_id: UUID,
        email: str,
        request: Optional[Request] = None,
        auth_method: str = "jwt",
    ) -> AuditLog:
        """
        Log successful authentication.

        Args:
            db: Database session
            user_id: Authenticated user ID
            organization_id: User's organization
            email: User email (for audit trail)
            request: FastAPI request
            auth_method: Authentication method used (e.g., "jwt", "oauth", "password")
        """
        return AuditService.log_event(
            db=db,
            action=AuditEventType.AUTH_LOGIN_SUCCESS.value,
            organization_id=organization_id,
            user_id=user_id,
            resource_type="user",
            resource_id=user_id,
            metadata={
                "email": email,
                "auth_method": auth_method,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            request=request,
        )

    @staticmethod
    def log_auth_failure(
        db: Session,
        email: Optional[str] = None,
        reason: str = "invalid_credentials",
        request: Optional[Request] = None,
        organization_id: Optional[UUID] = None,
    ) -> AuditLog:
        """
        Log failed authentication attempt.

        Args:
            db: Database session
            email: Attempted email (if available)
            reason: Failure reason (e.g., "invalid_credentials", "account_locked")
            request: FastAPI request
            organization_id: Organization context if known
        """
        return AuditService.log_event(
            db=db,
            action=AuditEventType.AUTH_LOGIN_FAILURE.value,
            organization_id=organization_id,
            resource_type="auth_attempt",
            metadata={
                "email": email,
                "reason": reason,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            request=request,
        )

    @staticmethod
    def log_token_invalid(
        db: Session,
        reason: str,
        request: Optional[Request] = None,
        token_snippet: Optional[str] = None,
    ) -> AuditLog:
        """
        Log invalid token attempt (potential attack indicator).

        Args:
            db: Database session
            reason: Why token was invalid (e.g., "signature_mismatch", "malformed")
            request: FastAPI request
            token_snippet: First/last few chars of token (for debugging, not full token)
        """
        return AuditService.log_event(
            db=db,
            action=AuditEventType.AUTH_TOKEN_INVALID.value,
            metadata={
                "reason": reason,
                "token_snippet": token_snippet,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            request=request,
        )

    @staticmethod
    def log_token_expired(
        db: Session,
        user_id: Optional[UUID] = None,
        organization_id: Optional[UUID] = None,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """
        Log expired token usage attempt.

        Args:
            db: Database session
            user_id: User ID from expired token (if extractable)
            organization_id: Organization from expired token
            request: FastAPI request
        """
        return AuditService.log_event(
            db=db,
            action=AuditEventType.AUTH_TOKEN_EXPIRED.value,
            organization_id=organization_id,
            user_id=user_id,
            metadata={
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            request=request,
        )

    @staticmethod
    def log_authz_denied(
        db: Session,
        user_id: UUID,
        organization_id: UUID,
        required_roles: list[str],
        actual_role: str,
        endpoint: str,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """
        Log authorization denial (insufficient role).

        Args:
            db: Database session
            user_id: User who was denied
            organization_id: User's organization
            required_roles: Roles required for access
            actual_role: User's actual role
            endpoint: Endpoint that was denied
            request: FastAPI request
        """
        return AuditService.log_event(
            db=db,
            action=AuditEventType.AUTHZ_ACCESS_DENIED.value,
            organization_id=organization_id,
            user_id=user_id,
            resource_type="endpoint",
            metadata={
                "required_roles": required_roles,
                "actual_role": actual_role,
                "endpoint": endpoint,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            request=request,
        )

    @staticmethod
    def log_multi_tenancy_violation(
        db: Session,
        user_id: UUID,
        user_organization_id: UUID,
        attempted_organization_id: UUID,
        resource_type: str,
        resource_id: Optional[UUID] = None,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """
        Log multi-tenancy violation attempt (user trying to access another org's data).

        This is a critical security event and should trigger alerts.

        Args:
            db: Database session
            user_id: User who attempted violation
            user_organization_id: User's actual organization
            attempted_organization_id: Organization they tried to access
            resource_type: Type of resource attempted
            resource_id: ID of resource attempted
            request: FastAPI request
        """
        logger.warning(
            "MULTI_TENANCY_VIOLATION",
            extra={
                "user_id": str(user_id),
                "user_org": str(user_organization_id),
                "attempted_org": str(attempted_organization_id),
                "resource_type": resource_type,
                "resource_id": str(resource_id) if resource_id else None,
            },
        )

        return AuditService.log_event(
            db=db,
            action=AuditEventType.AUTHZ_MULTI_TENANCY_VIOLATION.value,
            organization_id=user_organization_id,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata={
                "attempted_organization_id": str(attempted_organization_id),
                "severity": "critical",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            request=request,
        )

    @staticmethod
    def log_permission_denied(
        db: Session,
        user_id: UUID,
        organization_id: UUID,
        required_permissions: list[str],
        actual_role: str,
        endpoint: str,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """
        Log permission-based denial.

        Args:
            db: Database session
            user_id: User who was denied
            organization_id: User's organization
            required_permissions: Permissions required for access
            actual_role: User's actual role
            endpoint: Endpoint that was denied
            request: FastAPI request
        """
        return AuditService.log_event(
            db=db,
            action=AuditEventType.AUTHZ_PERMISSION_CHECK_FAILED.value,
            organization_id=organization_id,
            user_id=user_id,
            resource_type="endpoint",
            metadata={
                "required_permissions": required_permissions,
                "actual_role": actual_role,
                "endpoint": endpoint,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            request=request,
        )

    @staticmethod
    def log_access_granted(
        db: Session,
        user_id: UUID,
        organization_id: UUID,
        endpoint: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[UUID] = None,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """
        Log successful authorization (for sensitive operations).

        Note: Only log for sensitive operations to avoid log bloat.

        Args:
            db: Database session
            user_id: User granted access
            organization_id: User's organization
            endpoint: Endpoint accessed
            resource_type: Type of resource accessed
            resource_id: ID of resource accessed
            request: FastAPI request
        """
        return AuditService.log_event(
            db=db,
            action=AuditEventType.AUTHZ_ACCESS_GRANTED.value,
            organization_id=organization_id,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata={
                "endpoint": endpoint,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            request=request,
        )

    @staticmethod
    def log_workflow_created(
        db: Session,
        user_id: UUID,
        organization_id: UUID,
        workflow_id: UUID,
        workflow_name: str,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """
        Log workflow creation event.

        Args:
            db: Database session
            user_id: User who created the workflow
            organization_id: Organization ID
            workflow_id: Created workflow ID
            workflow_name: Workflow name
            request: FastAPI request
        """
        return AuditService.log_event(
            db=db,
            action="workflow.created",
            organization_id=organization_id,
            user_id=user_id,
            resource_type="workflow",
            resource_id=workflow_id,
            metadata={
                "workflow_name": workflow_name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            request=request,
        )

    @staticmethod
    def log_workflow_updated(
        db: Session,
        user_id: UUID,
        organization_id: UUID,
        workflow_id: UUID,
        workflow_name: str,
        buckets_added: int = 0,
        buckets_updated: int = 0,
        buckets_deleted: int = 0,
        criteria_added: int = 0,
        criteria_updated: int = 0,
        criteria_deleted: int = 0,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """
        Log workflow update event.

        Args:
            db: Database session
            user_id: User who updated the workflow
            organization_id: Organization ID
            workflow_id: Updated workflow ID
            workflow_name: Updated workflow name
            buckets_added: Number of buckets added
            buckets_updated: Number of buckets updated
            buckets_deleted: Number of buckets deleted
            criteria_added: Number of criteria added
            criteria_updated: Number of criteria updated
            criteria_deleted: Number of criteria deleted
            request: FastAPI request
        """
        return AuditService.log_event(
            db=db,
            action="workflow.updated",
            organization_id=organization_id,
            user_id=user_id,
            resource_type="workflow",
            resource_id=workflow_id,
            metadata={
                "workflow_name": workflow_name,
                "buckets_added": buckets_added,
                "buckets_updated": buckets_updated,
                "buckets_deleted": buckets_deleted,
                "criteria_added": criteria_added,
                "criteria_updated": criteria_updated,
                "criteria_deleted": criteria_deleted,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            request=request,
        )
