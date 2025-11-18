import NextAuth from "next-auth"
import { authOptions } from "@/lib/auth"

/**
 * Auth.js API route handlers (Node.js runtime).
 * Uses full authOptions with credential provider (bcrypt + Prisma).
 *
 * This is separate from middleware which uses baseAuthConfig.
 */
const { handlers } = NextAuth(authOptions)

export const { GET, POST } = handlers
