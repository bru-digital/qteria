import NextAuth from "next-auth"
import { baseAuthConfig } from "./auth-config-base"

/**
 * Auth instance for middleware (Edge Runtime).
 * Uses baseAuthConfig which is Edge-safe (no bcrypt, no Prisma).
 *
 * This instance is ONLY for middleware JWT validation.
 * API routes use the full authOptions from lib/auth.ts.
 */
export const { auth, handlers, signIn, signOut } = NextAuth(baseAuthConfig)
