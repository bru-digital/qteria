/**
 * Backend JWT Token Generation Helper
 *
 * This module provides a shared helper for generating JWT tokens that are compatible
 * with the FastAPI backend authentication system.
 *
 * IMPORTANT: This JWT is different from the NextAuth session token!
 * - NextAuth JWT: Used for frontend session management (stays in browser)
 * - Backend JWT: Generated server-side to authenticate requests to FastAPI backend
 *
 * Security Notes:
 * - Backend JWT is NEVER exposed to the client browser
 * - Generated only in Next.js API routes (server-side)
 * - Short-lived (30 minutes) to minimize risk if compromised
 * - Uses HS256 algorithm with JWT_SECRET from environment
 */

import { sign } from 'jsonwebtoken'

/**
 * JWT payload structure expected by the FastAPI backend.
 *
 * MUST match backend TokenPayload model in apps/api/app/core/auth.py:84-94
 *
 * Field naming convention:
 * - Backend expects snake_case (org_id, not organizationId)
 * - TypeScript enforces correct field names at compile time
 */
export interface BackendJWTPayload {
  /** User UUID (matches User.id in database) */
  sub: string

  /** User email address */
  email: string

  /** User role (process_manager, project_handler, admin) */
  role: string

  /** Organization UUID - CRITICAL for multi-tenancy enforcement */
  org_id: string

  /** User display name (optional) */
  name: string | null

  /** Issued at timestamp (Unix epoch seconds) */
  iat: number

  /** Expiration timestamp (Unix epoch seconds, iat + 30 minutes) */
  exp: number
}

/**
 * Session user object from NextAuth.
 * This is the structure returned by getServerSession() in Next.js API routes.
 */
interface SessionUser {
  id: string
  email?: string | null
  role: string
  organizationId: string
  name?: string | null
}

/**
 * Generate a JWT token for authenticating requests to the FastAPI backend.
 *
 * @param session - NextAuth session object (from getServerSession())
 * @returns Signed JWT token string
 * @throws Error if JWT_SECRET environment variable is not set
 *
 * @example
 * ```typescript
 * import { getServerSession } from "next-auth"
 * import { generateBackendJWT } from "@/lib/backend-jwt"
 *
 * const session = await getServerSession(authOptions)
 * if (!session) {
 *   return NextResponse.json({ detail: { code: "UNAUTHORIZED" } }, { status: 401 })
 * }
 *
 * const token = generateBackendJWT(session)
 * const response = await fetch(`${API_URL}/v1/workflows`, {
 *   headers: { Authorization: `Bearer ${token}` }
 * })
 * ```
 */
export function generateBackendJWT(session: { user: SessionUser }): string {
  const secret = process.env.JWT_SECRET
  if (!secret) {
    throw new Error(
      'JWT_SECRET environment variable is required for backend authentication. ' +
        'Generate one with: openssl rand -hex 32'
    )
  }

  const now = Math.floor(Date.now() / 1000)
  const expiresIn = 30 * 60 // 30 minutes

  const payload: BackendJWTPayload = {
    sub: session.user.id,
    email: session.user.email || '',
    role: session.user.role,
    org_id: session.user.organizationId, // ✅ CORRECT: Backend expects snake_case
    name: session.user.name || null,
    iat: now,
    exp: now + expiresIn,
  }

  return sign(payload, secret, { algorithm: 'HS256' })
}

/**
 * Type guard to check if a session object has the required user fields.
 * Useful for validating session before calling generateBackendJWT.
 *
 * @param session - Unknown session object to validate
 * @returns true if session has valid user fields, false otherwise
 */
export function isValidSession(session: unknown): session is { user: SessionUser } {
  if (typeof session !== 'object' || session === null) {
    return false
  }

  if (!('user' in session)) {
    return false
  }

  const user = (session as { user: unknown }).user

  if (typeof user !== 'object' || user === null) {
    return false
  }

  return (
    'id' in user &&
    'role' in user &&
    'organizationId' in user &&
    typeof (user as { id: unknown }).id === 'string' &&
    typeof (user as { role: unknown }).role === 'string' &&
    typeof (user as { organizationId: unknown }).organizationId === 'string'
  )
}
