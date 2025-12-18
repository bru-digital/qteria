import NextAuth, { DefaultSession } from 'next-auth'
import { JWT } from 'next-auth/jwt'
import { UserRoleType } from '@/lib/rbac'

/**
 * NAMING CONVENTION MAPPING:
 *
 * This file demonstrates the intentional naming convention mapping between
 * frontend (TypeScript/camelCase) and backend (Python/snake_case):
 *
 * - JWT token field: org_id (snake_case) - matches backend API contract
 * - Session/User fields: organizationId (camelCase) - matches TypeScript conventions
 *
 * The auth callbacks in auth-config-base.ts handle the conversion between these
 * conventions, ensuring type safety and consistency with language best practices.
 */

declare module 'next-auth' {
  interface Session {
    user: {
      id: string
      role: UserRoleType
      organizationId: string // CamelCase for TypeScript conventions
    } & DefaultSession['user']
  }

  interface User {
    id: string
    email: string
    name: string | null
    role: UserRoleType
    organizationId: string // CamelCase for TypeScript conventions
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    role?: UserRoleType
    org_id?: string // Snake_case to match backend API contract
  }
}
