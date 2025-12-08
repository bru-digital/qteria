import type { NextAuthConfig } from "next-auth"
import type { JWT } from "next-auth/jwt"
import type { Session, User } from "next-auth"
import type { UserRoleType } from "./rbac"

// Get NEXTAUTH_SECRET from environment
// During build, this might be empty - it will be validated at runtime
const NEXTAUTH_SECRET = process.env.NEXTAUTH_SECRET || ''

// Validate at runtime (not during build)
if (typeof window === 'undefined' && process.env.NEXT_PHASE !== 'phase-production-build') {
  if (!NEXTAUTH_SECRET) {
    throw new Error(
      'NEXTAUTH_SECRET environment variable is required. Generate one with: openssl rand -base64 32'
    )
  }
  if (NEXTAUTH_SECRET.length < 32) {
    console.warn('[AUTH] NEXTAUTH_SECRET should be at least 32 characters for security')
  }
}

/**
 * Extended JWT type with custom fields
 *
 * NAMING CONVENTION: JWT uses snake_case (org_id) to match backend API contract.
 * The backend API (FastAPI/Python) uses snake_case throughout, so JWT tokens
 * use org_id for consistency with API responses and authentication flows.
 */
interface ExtendedJWT extends JWT {
  role?: UserRoleType
  org_id?: string  // Snake_case to match backend API contract
}

/**
 * Extended Session type with custom user fields
 *
 * NAMING CONVENTION: Session uses camelCase (organizationId) to match frontend
 * TypeScript conventions. This aligns with Prisma schema and frontend codebase.
 *
 * MAPPING: The JWT callback converts between these conventions:
 * - Backend/JWT: org_id (snake_case)
 * - Frontend/Session: organizationId (camelCase)
 */
interface ExtendedSession extends Session {
  user: {
    id: string
    email: string
    name: string | null
    role: UserRoleType
    organizationId: string  // CamelCase to match TypeScript conventions
  }
}

/**
 * Base Auth.js configuration for Edge Runtime (middleware).
 * Contains ONLY JWT validation logic - NO database, NO bcrypt.
 *
 * This config is safe to use in Edge Runtime because it doesn't import:
 * - bcrypt (Node.js native modules)
 * - Prisma (Node.js runtime dependencies)
 * - Any other Node.js-specific libraries
 */
export const baseAuthConfig = {
  providers: [], // Empty array - providers added in full config
  session: {
    strategy: "jwt" as const,
    maxAge: 7 * 24 * 60 * 60 // 7 days
  },
  callbacks: {
    async jwt({ token, user }: { token: JWT; user?: User }): Promise<JWT> {
      // Add custom fields to JWT on sign in
      if (user) {
        const extendedToken = token as ExtendedJWT
        extendedToken.role = (user as any).role as UserRoleType
        // Map frontend organizationId (camelCase) to JWT org_id (snake_case)
        // This ensures JWT matches backend API contract (FastAPI uses snake_case)
        extendedToken.org_id = (user as any).organizationId
        return extendedToken
      }
      return token
    },
    async session({ session, token }: { session: Session; token: JWT }): Promise<Session> {
      const extendedToken = token as ExtendedJWT

      // Add custom fields to session
      if (session.user) {
        (session.user as any).id = token.sub as string
        ;(session.user as any).role = extendedToken.role as UserRoleType
        // Map JWT org_id (snake_case) back to Session organizationId (camelCase)
        // This ensures frontend code follows TypeScript naming conventions
        ;(session.user as any).organizationId = extendedToken.org_id as string
      }
      return session
    }
  },
  pages: {
    signIn: "/login",
    error: "/login"
  },
  secret: NEXTAUTH_SECRET,
} satisfies NextAuthConfig
