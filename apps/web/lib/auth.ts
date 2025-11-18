import type { NextAuthConfig } from "next-auth"
import Credentials from "@auth/core/providers/credentials"
import MicrosoftEntraID from "@auth/core/providers/microsoft-entra-id"
import Google from "@auth/core/providers/google"
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
  callbacks: {
    ...baseAuthConfig.callbacks,
    async signIn({ user, account, profile }) {
      // OAuth providers (Microsoft Entra ID or Google)
      if (account?.provider === "microsoft-entra-id" || account?.provider === "google") {
        const email = user.email || (profile as any)?.email

        if (!email) {
          console.error('[AUTH] OAuth login failed: no email provided')
          return false
        }

        try {
          // Check if user exists
          const existingUser = await prisma.user.findUnique({
            where: { email }
          })

          if (!existingUser) {
            // For MVP: OAuth users need to be invited first
            // Future: implement organization assignment logic
            console.log(`[AUTH] OAuth login attempt for non-existent user: ${email}`)
            return "/login?error=oauth_user_not_found"
          }

          // Update user with OAuth provider info
          await prisma.user.update({
            where: { email },
            data: {
              name: user.name || existingUser.name,
              // Store OAuth avatar URL if available
              // Note: This assumes we add an avatarUrl field to the User model
            }
          })

          return true
        } catch (error) {
          console.error('[AUTH] OAuth signIn callback error:', error)
          return false
        }
      }

      // Credentials provider - no additional checks needed
      return true
    }
  },
  providers: [
    // Primary: Microsoft OAuth (TÜV SÜD and most TIC notified bodies use Microsoft 365)
    MicrosoftEntraID({
      clientId: process.env.MICROSOFT_CLIENT_ID!,
      clientSecret: process.env.MICROSOFT_CLIENT_SECRET!,
      authorization: {
        params: {
          prompt: "select_account",
          scope: "openid profile email"
        }
      }
    }) as any,

    // Secondary: Google OAuth (some organizations use Google Workspace)
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      authorization: {
        params: {
          prompt: "select_account",
          access_type: "offline",
          response_type: "code"
        }
      }
    }) as any,

    // Email/Password authentication (backwards compatibility)
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
