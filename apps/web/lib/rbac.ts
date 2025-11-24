/**
 * Role-Based Access Control (RBAC) utilities for frontend.
 *
 * This module provides TypeScript types and utilities for role-based
 * UI rendering and permission checks.
 *
 * IMPORTANT: Frontend RBAC is for UX only - always enforce on backend!
 */

/**
 * User roles matching backend UserRole enum.
 * These values must match apps/api/app/models/enums.py
 */
export const UserRole = {
  PROCESS_MANAGER: 'process_manager',
  PROJECT_HANDLER: 'project_handler',
  ADMIN: 'admin',
} as const

export type UserRoleType = (typeof UserRole)[keyof typeof UserRole]

/**
 * Permission types for fine-grained access control.
 * Format: resource:action
 */
export const Permission = {
  // Workflow permissions
  WORKFLOWS_CREATE: 'workflows:create',
  WORKFLOWS_READ: 'workflows:read',
  WORKFLOWS_UPDATE: 'workflows:update',
  WORKFLOWS_DELETE: 'workflows:delete',

  // Assessment permissions
  ASSESSMENTS_CREATE: 'assessments:create',
  ASSESSMENTS_READ: 'assessments:read',
  ASSESSMENTS_UPDATE: 'assessments:update',
  ASSESSMENTS_DELETE: 'assessments:delete',

  // Document permissions
  DOCUMENTS_UPLOAD: 'documents:upload',
  DOCUMENTS_READ: 'documents:read',
  DOCUMENTS_DELETE: 'documents:delete',

  // Organization permissions (admin only)
  ORGANIZATIONS_READ: 'organizations:read',
  ORGANIZATIONS_UPDATE: 'organizations:update',

  // User management permissions (admin only)
  USERS_CREATE: 'users:create',
  USERS_READ: 'users:read',
  USERS_UPDATE: 'users:update',
  USERS_DELETE: 'users:delete',

  // Wildcard for admin
  ALL: '*',
} as const

export type PermissionType = (typeof Permission)[keyof typeof Permission]

/**
 * Role-to-Permission mapping.
 * Must stay in sync with backend ROLE_PERMISSIONS.
 */
export const ROLE_PERMISSIONS: Record<UserRoleType, Set<PermissionType>> = {
  [UserRole.PROCESS_MANAGER]: new Set([
    Permission.WORKFLOWS_CREATE,
    Permission.WORKFLOWS_READ,
    Permission.WORKFLOWS_UPDATE,
    Permission.WORKFLOWS_DELETE,
    Permission.ASSESSMENTS_READ,
    Permission.DOCUMENTS_READ,
  ]),
  [UserRole.PROJECT_HANDLER]: new Set([
    Permission.WORKFLOWS_READ,
    Permission.ASSESSMENTS_CREATE,
    Permission.ASSESSMENTS_READ,
    Permission.DOCUMENTS_UPLOAD,
    Permission.DOCUMENTS_READ,
  ]),
  [UserRole.ADMIN]: new Set([Permission.ALL]),
}

/**
 * Check if a role has a specific permission.
 *
 * @param role - The user's role
 * @param permission - The permission to check
 * @returns true if the role has the permission
 */
export function hasPermission(
  role: UserRoleType | undefined,
  permission: PermissionType
): boolean {
  if (!role) return false

  const rolePerms = ROLE_PERMISSIONS[role]
  if (!rolePerms) return false

  // Admin has all permissions
  if (rolePerms.has(Permission.ALL)) return true

  return rolePerms.has(permission)
}

/**
 * Check if a role is one of the allowed roles.
 *
 * @param role - The user's role
 * @param allowedRoles - Array of allowed roles
 * @returns true if the user's role is in the allowed list
 */
export function hasRole(
  role: UserRoleType | undefined,
  allowedRoles: UserRoleType[]
): boolean {
  if (!role) return false

  // Admin always has access
  if (role === UserRole.ADMIN) return true

  return allowedRoles.includes(role)
}

/**
 * Check if user is an admin.
 */
export function isAdmin(role: UserRoleType | undefined): boolean {
  return role === UserRole.ADMIN
}

/**
 * Check if user is a process manager (or admin).
 */
export function isProcessManager(role: UserRoleType | undefined): boolean {
  return role === UserRole.PROCESS_MANAGER || role === UserRole.ADMIN
}

/**
 * Check if user is a project handler (or admin).
 */
export function isProjectHandler(role: UserRoleType | undefined): boolean {
  return role === UserRole.PROJECT_HANDLER || role === UserRole.ADMIN
}

/**
 * Check if user can create workflows.
 */
export function canCreateWorkflow(role: UserRoleType | undefined): boolean {
  return hasPermission(role, Permission.WORKFLOWS_CREATE)
}

/**
 * Check if user can run assessments.
 */
export function canRunAssessment(role: UserRoleType | undefined): boolean {
  return hasPermission(role, Permission.ASSESSMENTS_CREATE)
}

/**
 * Check if user can upload documents.
 */
export function canUploadDocuments(role: UserRoleType | undefined): boolean {
  return hasPermission(role, Permission.DOCUMENTS_UPLOAD)
}

/**
 * Check if user can manage users.
 */
export function canManageUsers(role: UserRoleType | undefined): boolean {
  return hasPermission(role, Permission.USERS_CREATE)
}

/**
 * Role display information for UI.
 */
export const ROLE_DISPLAY: Record<
  UserRoleType,
  { title: string; description: string; color: string }
> = {
  [UserRole.PROCESS_MANAGER]: {
    title: 'Process Manager',
    description: 'Creates and manages validation workflows',
    color: 'blue',
  },
  [UserRole.PROJECT_HANDLER]: {
    title: 'Project Handler',
    description: 'Runs assessments and validates documents',
    color: 'green',
  },
  [UserRole.ADMIN]: {
    title: 'Administrator',
    description: 'Full access to all features',
    color: 'purple',
  },
}

/**
 * Get display-friendly role title.
 */
export function getRoleTitle(role: UserRoleType | undefined): string {
  if (!role) return 'Unknown'
  return ROLE_DISPLAY[role]?.title || role
}

/**
 * Get role badge color for UI.
 */
export function getRoleColor(role: UserRoleType | undefined): string {
  if (!role) return 'gray'
  return ROLE_DISPLAY[role]?.color || 'gray'
}
