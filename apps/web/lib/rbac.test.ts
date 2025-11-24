/**
 * Tests for RBAC utilities.
 */
import { describe, it, expect } from 'vitest'
import {
  UserRole,
  Permission,
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
  ROLE_PERMISSIONS,
} from './rbac'

describe('UserRole enum', () => {
  it('should have correct role values', () => {
    expect(UserRole.PROCESS_MANAGER).toBe('process_manager')
    expect(UserRole.PROJECT_HANDLER).toBe('project_handler')
    expect(UserRole.ADMIN).toBe('admin')
  })
})

describe('Permission enum', () => {
  it('should have workflow permissions', () => {
    expect(Permission.WORKFLOWS_CREATE).toBe('workflows:create')
    expect(Permission.WORKFLOWS_READ).toBe('workflows:read')
    expect(Permission.WORKFLOWS_UPDATE).toBe('workflows:update')
    expect(Permission.WORKFLOWS_DELETE).toBe('workflows:delete')
  })

  it('should have assessment permissions', () => {
    expect(Permission.ASSESSMENTS_CREATE).toBe('assessments:create')
    expect(Permission.ASSESSMENTS_READ).toBe('assessments:read')
  })

  it('should have document permissions', () => {
    expect(Permission.DOCUMENTS_UPLOAD).toBe('documents:upload')
    expect(Permission.DOCUMENTS_READ).toBe('documents:read')
  })

  it('should have wildcard permission', () => {
    expect(Permission.ALL).toBe('*')
  })
})

describe('ROLE_PERMISSIONS mapping', () => {
  it('should grant process manager workflow permissions', () => {
    const perms = ROLE_PERMISSIONS[UserRole.PROCESS_MANAGER]
    expect(perms.has(Permission.WORKFLOWS_CREATE)).toBe(true)
    expect(perms.has(Permission.WORKFLOWS_READ)).toBe(true)
    expect(perms.has(Permission.WORKFLOWS_UPDATE)).toBe(true)
    expect(perms.has(Permission.WORKFLOWS_DELETE)).toBe(true)
  })

  it('should not grant process manager assessment create', () => {
    const perms = ROLE_PERMISSIONS[UserRole.PROCESS_MANAGER]
    expect(perms.has(Permission.ASSESSMENTS_CREATE)).toBe(false)
  })

  it('should grant project handler assessment create', () => {
    const perms = ROLE_PERMISSIONS[UserRole.PROJECT_HANDLER]
    expect(perms.has(Permission.ASSESSMENTS_CREATE)).toBe(true)
  })

  it('should not grant project handler workflow create', () => {
    const perms = ROLE_PERMISSIONS[UserRole.PROJECT_HANDLER]
    expect(perms.has(Permission.WORKFLOWS_CREATE)).toBe(false)
  })

  it('should grant admin wildcard permission', () => {
    const perms = ROLE_PERMISSIONS[UserRole.ADMIN]
    expect(perms.has(Permission.ALL)).toBe(true)
  })
})

describe('hasPermission', () => {
  it('should return false for undefined role', () => {
    expect(hasPermission(undefined, Permission.WORKFLOWS_CREATE)).toBe(false)
  })

  it('should return true for admin on any permission', () => {
    expect(hasPermission(UserRole.ADMIN, Permission.WORKFLOWS_CREATE)).toBe(true)
    expect(hasPermission(UserRole.ADMIN, Permission.USERS_DELETE)).toBe(true)
    expect(hasPermission(UserRole.ADMIN, Permission.DOCUMENTS_UPLOAD)).toBe(true)
  })

  it('should return true for process manager on workflow permissions', () => {
    expect(hasPermission(UserRole.PROCESS_MANAGER, Permission.WORKFLOWS_CREATE)).toBe(true)
    expect(hasPermission(UserRole.PROCESS_MANAGER, Permission.WORKFLOWS_DELETE)).toBe(true)
  })

  it('should return false for process manager on assessment create', () => {
    expect(hasPermission(UserRole.PROCESS_MANAGER, Permission.ASSESSMENTS_CREATE)).toBe(false)
  })

  it('should return true for project handler on assessment create', () => {
    expect(hasPermission(UserRole.PROJECT_HANDLER, Permission.ASSESSMENTS_CREATE)).toBe(true)
  })

  it('should return false for project handler on workflow create', () => {
    expect(hasPermission(UserRole.PROJECT_HANDLER, Permission.WORKFLOWS_CREATE)).toBe(false)
  })
})

describe('hasRole', () => {
  it('should return false for undefined role', () => {
    expect(hasRole(undefined, [UserRole.ADMIN])).toBe(false)
  })

  it('should return true if role is in allowed list', () => {
    expect(hasRole(UserRole.PROCESS_MANAGER, [UserRole.PROCESS_MANAGER, UserRole.ADMIN])).toBe(true)
  })

  it('should return false if role is not in allowed list', () => {
    expect(hasRole(UserRole.PROJECT_HANDLER, [UserRole.PROCESS_MANAGER])).toBe(false)
  })

  it('should always return true for admin', () => {
    expect(hasRole(UserRole.ADMIN, [UserRole.PROCESS_MANAGER])).toBe(true)
    expect(hasRole(UserRole.ADMIN, [UserRole.PROJECT_HANDLER])).toBe(true)
  })
})

describe('isAdmin', () => {
  it('should return true for admin', () => {
    expect(isAdmin(UserRole.ADMIN)).toBe(true)
  })

  it('should return false for other roles', () => {
    expect(isAdmin(UserRole.PROCESS_MANAGER)).toBe(false)
    expect(isAdmin(UserRole.PROJECT_HANDLER)).toBe(false)
  })

  it('should return false for undefined', () => {
    expect(isAdmin(undefined)).toBe(false)
  })
})

describe('isProcessManager', () => {
  it('should return true for process manager', () => {
    expect(isProcessManager(UserRole.PROCESS_MANAGER)).toBe(true)
  })

  it('should return true for admin (has all roles)', () => {
    expect(isProcessManager(UserRole.ADMIN)).toBe(true)
  })

  it('should return false for project handler', () => {
    expect(isProcessManager(UserRole.PROJECT_HANDLER)).toBe(false)
  })

  it('should return false for undefined', () => {
    expect(isProcessManager(undefined)).toBe(false)
  })
})

describe('isProjectHandler', () => {
  it('should return true for project handler', () => {
    expect(isProjectHandler(UserRole.PROJECT_HANDLER)).toBe(true)
  })

  it('should return true for admin (has all roles)', () => {
    expect(isProjectHandler(UserRole.ADMIN)).toBe(true)
  })

  it('should return false for process manager', () => {
    expect(isProjectHandler(UserRole.PROCESS_MANAGER)).toBe(false)
  })

  it('should return false for undefined', () => {
    expect(isProjectHandler(undefined)).toBe(false)
  })
})

describe('canCreateWorkflow', () => {
  it('should return true for process manager', () => {
    expect(canCreateWorkflow(UserRole.PROCESS_MANAGER)).toBe(true)
  })

  it('should return true for admin', () => {
    expect(canCreateWorkflow(UserRole.ADMIN)).toBe(true)
  })

  it('should return false for project handler', () => {
    expect(canCreateWorkflow(UserRole.PROJECT_HANDLER)).toBe(false)
  })

  it('should return false for undefined', () => {
    expect(canCreateWorkflow(undefined)).toBe(false)
  })
})

describe('canRunAssessment', () => {
  it('should return true for project handler', () => {
    expect(canRunAssessment(UserRole.PROJECT_HANDLER)).toBe(true)
  })

  it('should return true for admin', () => {
    expect(canRunAssessment(UserRole.ADMIN)).toBe(true)
  })

  it('should return false for process manager', () => {
    expect(canRunAssessment(UserRole.PROCESS_MANAGER)).toBe(false)
  })

  it('should return false for undefined', () => {
    expect(canRunAssessment(undefined)).toBe(false)
  })
})

describe('canUploadDocuments', () => {
  it('should return true for project handler', () => {
    expect(canUploadDocuments(UserRole.PROJECT_HANDLER)).toBe(true)
  })

  it('should return true for admin', () => {
    expect(canUploadDocuments(UserRole.ADMIN)).toBe(true)
  })

  it('should return false for process manager', () => {
    expect(canUploadDocuments(UserRole.PROCESS_MANAGER)).toBe(false)
  })

  it('should return false for undefined', () => {
    expect(canUploadDocuments(undefined)).toBe(false)
  })
})

describe('canManageUsers', () => {
  it('should return true for admin', () => {
    expect(canManageUsers(UserRole.ADMIN)).toBe(true)
  })

  it('should return false for process manager', () => {
    expect(canManageUsers(UserRole.PROCESS_MANAGER)).toBe(false)
  })

  it('should return false for project handler', () => {
    expect(canManageUsers(UserRole.PROJECT_HANDLER)).toBe(false)
  })

  it('should return false for undefined', () => {
    expect(canManageUsers(undefined)).toBe(false)
  })
})

describe('getRoleTitle', () => {
  it('should return display title for valid roles', () => {
    expect(getRoleTitle(UserRole.PROCESS_MANAGER)).toBe('Process Manager')
    expect(getRoleTitle(UserRole.PROJECT_HANDLER)).toBe('Project Handler')
    expect(getRoleTitle(UserRole.ADMIN)).toBe('Administrator')
  })

  it('should return Unknown for undefined role', () => {
    expect(getRoleTitle(undefined)).toBe('Unknown')
  })
})

describe('getRoleColor', () => {
  it('should return correct colors for roles', () => {
    expect(getRoleColor(UserRole.PROCESS_MANAGER)).toBe('blue')
    expect(getRoleColor(UserRole.PROJECT_HANDLER)).toBe('green')
    expect(getRoleColor(UserRole.ADMIN)).toBe('purple')
  })

  it('should return gray for undefined role', () => {
    expect(getRoleColor(undefined)).toBe('gray')
  })
})
