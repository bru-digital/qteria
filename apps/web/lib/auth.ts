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

        // Always perform bcrypt comparison to prevent timing attacks
        // This ensures constant-time response whether user exists or not
        const passwordToCheck = credentials.password as string

        if (!user || !user.passwordHash) {
          // Perform hash comparison with dummy hash to maintain constant-time response
          // This prevents attackers from using timing differences to enumerate valid emails
          await bcrypt.compare(
            passwordToCheck,
            '$2b$12$dummyhashtopreventtimingattackKKpP3jW8vN.XjGZQqH7K8e1QfyGu'
          )
          return null
        }

        // Verify password
        const valid = await bcrypt.compare(passwordToCheck, user.passwordHash)

        if (!valid) {
          return null
        }

        // Validate user role before adding to JWT
        const allowedRoles = ['process_manager', 'project_handler', 'admin']
        if (!allowedRoles.includes(user.role)) {
          console.error(`[AUTH] Invalid user role detected: ${user.role} for user ${user.id}`)
          throw new Error('Invalid user role configuration. Please contact support.')
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
