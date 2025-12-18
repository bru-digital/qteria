/**
 * Role-based access control components for conditional UI rendering.
 *
 * These components provide declarative role-based UI visibility.
 *
 * IMPORTANT: These are for UX only - always enforce permissions on the backend!
 */
'use client'

import { ReactNode } from 'react'
import { useRole } from '@/lib/hooks/useRole'
import { UserRoleType, PermissionType, UserRole, Permission } from '@/lib/rbac'

interface RoleGuardProps {
  /** Content to render if user has the required role/permission */
  children: ReactNode
  /** Fallback content when user doesn't have access (optional) */
  fallback?: ReactNode
}

interface RequireRoleProps extends RoleGuardProps {
  /** Required role(s) - user must have one of these */
  roles: UserRoleType | UserRoleType[]
}

interface RequirePermissionProps extends RoleGuardProps {
  /** Required permission(s) - user must have all of these */
  permissions: PermissionType | PermissionType[]
}

/**
 * Renders children only if user has one of the required roles.
 *
 * @example
 * ```tsx
 * <RequireRole roles={['process_manager', 'admin']}>
 *   <CreateWorkflowButton />
 * </RequireRole>
 * ```
 */
export function RequireRole({ roles, children, fallback = null }: RequireRoleProps) {
  const { hasRole, isLoading, isAuthenticated } = useRole()

  if (isLoading) return null

  if (!isAuthenticated) return <>{fallback}</>

  const roleArray = Array.isArray(roles) ? roles : [roles]

  if (!hasRole(roleArray)) return <>{fallback}</>

  return <>{children}</>
}

/**
 * Renders children only if user has all required permissions.
 *
 * @example
 * ```tsx
 * <RequirePermission permissions="workflows:create">
 *   <CreateWorkflowButton />
 * </RequirePermission>
 * ```
 */
export function RequirePermission({
  permissions,
  children,
  fallback = null,
}: RequirePermissionProps) {
  const { hasPermission, isLoading, isAuthenticated } = useRole()

  if (isLoading) return null

  if (!isAuthenticated) return <>{fallback}</>

  const permArray = Array.isArray(permissions) ? permissions : [permissions]

  // User must have ALL specified permissions
  const hasAllPermissions = permArray.every(perm => hasPermission(perm))

  if (!hasAllPermissions) return <>{fallback}</>

  return <>{children}</>
}

/**
 * Renders children only for admin users.
 *
 * @example
 * ```tsx
 * <AdminOnly>
 *   <DangerZone />
 * </AdminOnly>
 * ```
 */
export function AdminOnly({ children, fallback = null }: RoleGuardProps) {
  const { isAdmin, isLoading, isAuthenticated } = useRole()

  if (isLoading) return null

  if (!isAuthenticated || !isAdmin) return <>{fallback}</>

  return <>{children}</>
}

/**
 * Renders children only for process managers (or admin).
 *
 * @example
 * ```tsx
 * <ProcessManagerOnly>
 *   <WorkflowManagement />
 * </ProcessManagerOnly>
 * ```
 */
export function ProcessManagerOnly({ children, fallback = null }: RoleGuardProps) {
  const { isProcessManager, isLoading, isAuthenticated } = useRole()

  if (isLoading) return null

  if (!isAuthenticated || !isProcessManager) return <>{fallback}</>

  return <>{children}</>
}

/**
 * Renders children only for project handlers (or admin).
 *
 * @example
 * ```tsx
 * <ProjectHandlerOnly>
 *   <RunAssessmentButton />
 * </ProjectHandlerOnly>
 * ```
 */
export function ProjectHandlerOnly({ children, fallback = null }: RoleGuardProps) {
  const { isProjectHandler, isLoading, isAuthenticated } = useRole()

  if (isLoading) return null

  if (!isAuthenticated || !isProjectHandler) return <>{fallback}</>

  return <>{children}</>
}

/**
 * Renders children only if user can create workflows.
 */
export function CanCreateWorkflow({ children, fallback = null }: RoleGuardProps) {
  const { canCreateWorkflow, isLoading, isAuthenticated } = useRole()

  if (isLoading) return null

  if (!isAuthenticated || !canCreateWorkflow) return <>{fallback}</>

  return <>{children}</>
}

/**
 * Renders children only if user can run assessments.
 */
export function CanRunAssessment({ children, fallback = null }: RoleGuardProps) {
  const { canRunAssessment, isLoading, isAuthenticated } = useRole()

  if (isLoading) return null

  if (!isAuthenticated || !canRunAssessment) return <>{fallback}</>

  return <>{children}</>
}

/**
 * Renders children only if user can upload documents.
 */
export function CanUploadDocuments({ children, fallback = null }: RoleGuardProps) {
  const { canUploadDocuments, isLoading, isAuthenticated } = useRole()

  if (isLoading) return null

  if (!isAuthenticated || !canUploadDocuments) return <>{fallback}</>

  return <>{children}</>
}

/**
 * Renders children only if user can manage users.
 */
export function CanManageUsers({ children, fallback = null }: RoleGuardProps) {
  const { canManageUsers, isLoading, isAuthenticated } = useRole()

  if (isLoading) return null

  if (!isAuthenticated || !canManageUsers) return <>{fallback}</>

  return <>{children}</>
}

// Re-export for convenience
export { UserRole, Permission }
export type { UserRoleType, PermissionType }
