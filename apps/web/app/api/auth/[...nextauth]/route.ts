import NextAuth from "next-auth"
import { authOptions } from "@/lib/auth"

/**
 * Auth.js API route handlers (Node.js runtime).
 * Uses full authOptions with credential provider (bcrypt + Prisma).
 *
 * This is separate from middleware which uses baseAuthConfig.
 *
 * Note: Type assertion used due to @auth/core version mismatch between
 * next-auth v5 beta and direct @auth/core imports for OAuth providers.
 */
const { handlers } = NextAuth(authOptions as any)

export const { GET, POST } = handlers
