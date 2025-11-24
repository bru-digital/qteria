/**
 * React hook for role-based access control.
 *
 * Provides easy access to the current user's role and permission checks.
 *
 * IMPORTANT: This hook is for UX only. Always enforce permissions on the backend!
 */
'use client'

import { useSession } from 'next-auth/react'
import {
  UserRoleType,
  hasPermission,
  hasRole,
  isAdmin,
  isProcessManager,
  isProjectHandler,
  canCreateWorkflow,
  canRunAssessment,
  canUploadDocuments,
  canManageUsers,
  getRoleTitle,
  getRoleColor,
  PermissionType,
} from '@/lib/rbac'

export interface UseRoleReturn {
  /** The current user's role */
  role: UserRoleType | undefined
  /** Whether the user is authenticated */
  isAuthenticated: boolean
  /** Whether authentication is still loading */
  isLoading: boolean
  /** Check if user has a specific permission */
  hasPermission: (permission: PermissionType) => boolean
  /** Check if user has one of the allowed roles */
  hasRole: (allowedRoles: UserRoleType[]) => boolean
  /** Whether user is an admin */
  isAdmin: boolean
  /** Whether user is a process manager (or admin) */
  isProcessManager: boolean
  /** Whether user is a project handler (or admin) */
  isProjectHandler: boolean
  /** Whether user can create workflows */
  canCreateWorkflow: boolean
  /** Whether user can run assessments */
  canRunAssessment: boolean
  /** Whether user can upload documents */
  canUploadDocuments: boolean
  /** Whether user can manage users */
  canManageUsers: boolean
  /** Display-friendly role title */
  roleTitle: string
  /** Role badge color for UI */
  roleColor: string
}

/**
 * Hook to access current user's role and permissions.
 *
 * @example
 * ```tsx
 * function WorkflowActions() {
 *   const { canCreateWorkflow, isAdmin } = useRole()
 *
 *   return (
 *     <div>
 *       {canCreateWorkflow && <Button>Create Workflow</Button>}
 *       {isAdmin && <Button variant="danger">Delete All</Button>}
 *     </div>
 *   )
 * }
 * ```
 */
export function useRole(): UseRoleReturn {
  const { data: session, status } = useSession()

  const role = session?.user?.role as UserRoleType | undefined
  const isLoading = status === 'loading'
  const isAuthenticated = status === 'authenticated' && !!session?.user

  return {
    role,
    isAuthenticated,
    isLoading,
    hasPermission: (permission: PermissionType) => hasPermission(role, permission),
    hasRole: (allowedRoles: UserRoleType[]) => hasRole(role, allowedRoles),
    isAdmin: isAdmin(role),
    isProcessManager: isProcessManager(role),
    isProjectHandler: isProjectHandler(role),
    canCreateWorkflow: canCreateWorkflow(role),
    canRunAssessment: canRunAssessment(role),
    canUploadDocuments: canUploadDocuments(role),
    canManageUsers: canManageUsers(role),
    roleTitle: getRoleTitle(role),
    roleColor: getRoleColor(role),
  }
}

export default useRole
