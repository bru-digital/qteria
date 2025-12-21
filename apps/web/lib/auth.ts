import type { NextAuthConfig } from 'next-auth'
import Credentials from '@auth/core/providers/credentials'
import MicrosoftEntraID from '@auth/core/providers/microsoft-entra-id'
import Google from '@auth/core/providers/google'
import { prisma } from '@/lib/prisma'
import {
  PrismaClientKnownRequestError,
  PrismaClientInitializationError,
} from '@prisma/client/runtime/library'
import bcrypt from 'bcrypt'
import { baseAuthConfig } from './auth-config-base'
import { createAuditLog, AuditAction } from '@/lib/audit'
import { isMicrosoftOAuthConfigured, isGoogleOAuthConfigured } from '@/lib/env'
import { getRequestContext } from '@/lib/request-context'
import { normalizeAndValidateEmail } from '@/lib/email-utils'

/**
 * System organization UUID for audit logging security events.
 * Used when user's organization is unknown (e.g., failed OAuth login for non-existent users).
 *
 * This UUID matches the System organization created in seed data (apps/api/scripts/seed_data.py).
 * Required for SOC2/ISO 27001 compliance - ensures all security events are audited.
 */
const SYSTEM_ORG_ID = '00000000-0000-0000-0000-000000000000'

/**
 * Type definitions for OAuth profiles and providers
 *
 * Note: These type assertions are needed due to version compatibility between
 * next-auth v5 (beta.30) and @auth/core (0.41.0). When next-auth v5 stable
 * releases, these can be replaced with official types.
 */
interface OAuthProfile {
  email?: string
  name?: string
  picture?: string
  sub?: string
}

/**
 * Type compatibility note:
 *
 * Using 'as any' for OAuth providers due to version mismatch between
 * next-auth v5 (beta.30) and @auth/core (0.41.0). The providers work
 * correctly at runtime, but TypeScript cannot reconcile the type differences.
 *
 * Tech debt: Remove type assertions when next-auth v5 stable releases.
 */

import NextAuth from 'next-auth'

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
      if (account?.provider === 'microsoft-entra-id' || account?.provider === 'google') {
        const oauthProfile = profile as OAuthProfile
        const rawEmail = user.email || oauthProfile?.email

        // Check if email was provided
        if (!rawEmail) {
          console.error('[AUTH] OAuth login failed: no email provided', {
            provider: account.provider,
            hasUser: !!user,
            hasProfile: !!profile,
          })
          return '/login?error=oauth_no_email'
        }

        // Normalize and validate email format
        const email = normalizeAndValidateEmail(rawEmail)
        if (!email) {
          console.error('[AUTH] OAuth login failed: invalid email format', {
            provider: account.provider,
            rawEmail,
          })
          return '/login?error=oauth_invalid_email'
        }

        try {
          // Check if user exists
          const existingUser = await prisma.user.findUnique({
            where: { email },
            include: { organization: true },
          })

          if (!existingUser) {
            // For MVP: OAuth users need to be invited first
            // Future: implement organization assignment logic
            console.log(`[AUTH] OAuth login attempt for non-existent user: ${email}`)

            // Audit log: OAuth login failed (user not found)
            // Note: We don't have organizationId since user doesn't exist
            // Log to System organization for security monitoring
            try {
              const { ipAddress, userAgent } = getRequestContext()
              await createAuditLog({
                organizationId: SYSTEM_ORG_ID,
                userId: null,
                action: AuditAction.LOGIN_FAILED,
                actionMetadata: {
                  email,
                  provider: account.provider,
                  reason: 'oauth_user_not_found',
                },
                ipAddress,
                userAgent,
              })
            } catch (auditError) {
              console.error('[AUTH] Failed to create audit log for OAuth failure:', auditError)
            }

            return '/login?error=oauth_user_not_found'
          }

          // Update user with OAuth provider info only if data has changed
          const oauthName = user.name || oauthProfile?.name
          const nameChanged = oauthName && oauthName !== existingUser.name
          const profileChanges: Record<string, any> = {}

          if (nameChanged) {
            try {
              await prisma.user.update({
                where: { email },
                data: {
                  name: oauthName,
                },
              })

              // Only set profileChanges if update succeeded
              // This ensures audit log accuracy (profileUpdated will only be true if update actually worked)
              profileChanges.name = { from: existingUser.name, to: oauthName }
            } catch (updateError) {
              // Log error but don't fail login due to profile update issues
              // This prevents race conditions from blocking authentication
              console.error('[AUTH] Failed to update user profile during OAuth login:', {
                error: updateError,
                email,
                attemptedName: oauthName,
              })
              // profileChanges remains empty, so audit log won't claim profile was updated
              // Login will still succeed with existing user data
            }
          }

          // Audit log: OAuth login successful (with optional profile update info)
          const { ipAddress, userAgent } = getRequestContext()
          await createAuditLog({
            organizationId: existingUser.organizationId,
            userId: existingUser.id,
            action: AuditAction.LOGIN_SUCCESS,
            actionMetadata: {
              email: existingUser.email,
              name: existingUser.name,
              provider: account.provider,
              authMethod: 'oauth',
              ...(nameChanged && {
                profileUpdated: true,
                changes: profileChanges,
              }),
            },
            ipAddress,
            userAgent,
          })

          return true
        } catch (error) {
          console.error('[AUTH] OAuth signIn callback error:', {
            error,
            provider: account.provider,
            email,
            errorMessage: error instanceof Error ? error.message : 'Unknown error',
            errorType: error?.constructor?.name,
          })

          // Return specific error based on error type
          if (error instanceof PrismaClientInitializationError) {
            // Database connection/initialization errors
            console.error('[AUTH] Database connection failed during OAuth login:', error)
            return '/login?error=oauth_database_error'
          }

          if (error instanceof PrismaClientKnownRequestError) {
            // Known Prisma errors (constraint violations, record not found, etc.)
            console.error('[AUTH] Prisma error during OAuth login:', {
              code: error.code,
              meta: error.meta,
            })
            return '/login?error=oauth_database_error'
          }

          // Generic OAuth error for other cases (network, auth provider errors, etc.)
          return '/login?error=oauth_error'
        }
      }

      // Credentials provider - no additional checks needed
      return true
    },
  },
  providers: [
    // Conditionally add OAuth providers only if configured
    ...(isMicrosoftOAuthConfigured()
      ? [
          // Primary: Microsoft OAuth (TÜV SÜD and most TIC notified bodies use Microsoft 365)
          // Type assertion needed for next-auth v5 beta compatibility (tech debt: remove when v5 stable releases)
          // Using 'as unknown as any' to make the type bypass explicit and intentional
          MicrosoftEntraID({
            clientId: process.env.MICROSOFT_CLIENT_ID || '',
            clientSecret: process.env.MICROSOFT_CLIENT_SECRET || '',
            issuer: `https://login.microsoftonline.com/${
              process.env.MICROSOFT_TENANT_ID || 'common'
            }/v2.0`,
            authorization: {
              params: {
                prompt: 'select_account',
                scope: 'openid profile email',
              },
            },
          }) as unknown as any,
        ]
      : []),

    ...(isGoogleOAuthConfigured()
      ? [
          // Secondary: Google OAuth (some organizations use Google Workspace)
          // Type assertion needed for next-auth v5 beta compatibility (tech debt: remove when v5 stable releases)
          // Using 'as unknown as any' to make the type bypass explicit and intentional
          Google({
            clientId: process.env.GOOGLE_CLIENT_ID || '',
            clientSecret: process.env.GOOGLE_CLIENT_SECRET || '',
            authorization: {
              params: {
                prompt: 'select_account',
                access_type: 'offline',
                response_type: 'code',
              },
            },
          }) as unknown as any,
        ]
      : []),

    // Email/Password authentication (always available)
    Credentials({
      name: 'Email',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null
        }

        // Normalize and validate email for consistent lookup
        const email = normalizeAndValidateEmail(credentials.email as string)

        if (!email) {
          return null
        }

        // Find user by email
        const user = await prisma.user.findUnique({
          where: { email },
          include: { organization: true },
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
          organizationId: user.organizationId,
        }
      },
    }),
  ],
} satisfies NextAuthConfig

/**
 * Export Auth.js handlers and helpers with full configuration.
 * These should be used by:
 * - Server actions (signIn, signOut)
 * - Server components (auth)
 *
 * The API route at app/api/auth/[...nextauth]/route.ts handles HTTP requests.
 */
export const { handlers, signIn, signOut, auth } = NextAuth(authOptions)
