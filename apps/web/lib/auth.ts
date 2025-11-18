import type { NextAuthConfig } from "next-auth"
import Credentials from "next-auth/providers/credentials"
import { prisma } from "@/lib/prisma"
import bcrypt from "bcrypt"
import { baseAuthConfig } from "./auth-config-base"

/**
 * Full Auth.js configuration for API routes (Node.js runtime).
 * Extends baseAuthConfig with credential provider that requires:
 * - bcrypt (for password hashing)
 * - Prisma (for database access)
 *
 * This config is ONLY used by API routes, NOT by middleware.
 */
export const authOptions = {
  ...baseAuthConfig,
  providers: [
    Credentials({
      name: "Email",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null
        }

        // Find user by email
        const user = await prisma.user.findUnique({
          where: { email: credentials.email as string },
          include: { organization: true }
        })

        if (!user || !user.passwordHash) {
          return null
        }

        // Verify password
        const valid = await bcrypt.compare(
          credentials.password as string,
          user.passwordHash
        )

        if (!valid) {
          return null
        }

        return {
          id: user.id,
          email: user.email,
          name: user.name,
          role: user.role,
          organizationId: user.organizationId
        }
      }
    })
  ],
} satisfies NextAuthConfig
