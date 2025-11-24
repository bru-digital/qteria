/**
 * Component exports for Qteria web app.
 */

// Role-based access control components
export {
  RequireRole,
  RequirePermission,
  AdminOnly,
  ProcessManagerOnly,
  ProjectHandlerOnly,
  CanCreateWorkflow,
  CanRunAssessment,
  CanUploadDocuments,
  CanManageUsers,
  UserRole,
  Permission,
} from './RoleGuard'

export type { UserRoleType, PermissionType } from './RoleGuard'
