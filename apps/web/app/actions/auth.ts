"use server"

/**
 * Server actions for authentication with audit logging.
 *
 * These actions wrap Auth.js signIn/signOut with audit logging
 * to ensure SOC2/ISO 27001 compliance.
 */

import { signIn, signOut } from "@/lib/auth"
import { createAuditLog, AuditAction, extractRequestMetadata } from "@/lib/audit"
import { prisma } from "@/lib/prisma"
import { headers } from "next/headers"
import { AuthError } from "next-auth"
import {
  checkFailedLoginRateLimit,
  checkTotalLoginRateLimit,
  recordFailedLoginAttempt,
  recordLoginAttempt,
  resetFailedLoginAttempts,
  formatRateLimitReset,
} from "@/lib/rate-limit"

export interface LoginResult {
  success: boolean
  error?: string
  redirectTo?: string
  rateLimitExceeded?: boolean
  retryAfterSeconds?: number
}

/**
 * Login action with audit logging.
 *
 * @param email - User email
 * @param password - User password
 * @param callbackUrl - URL to redirect after login (optional)
 * @returns Login result with success status and optional error message
 */
export async function loginWithAudit(
  email: string,
  password: string,
  callbackUrl?: string
): Promise<LoginResult> {
  const headersList = await headers()
  const { ipAddress, userAgent } = extractRequestMetadata(headersList)

  // Check rate limits before attempting authentication
  const failedLoginCheck = await checkFailedLoginRateLimit(email)
  if (!failedLoginCheck.allowed) {
    return {
      success: false,
      error: `Too many failed login attempts. Please try again in ${formatRateLimitReset(
        failedLoginCheck.resetInSeconds
      )}.`,
      rateLimitExceeded: true,
      retryAfterSeconds: failedLoginCheck.resetInSeconds,
    }
  }

  // Check IP-based rate limit
  if (ipAddress) {
    const ipCheck = await checkTotalLoginRateLimit(ipAddress)
    if (!ipCheck.allowed) {
      return {
        success: false,
        error: `Too many login attempts from your network. Please try again in ${formatRateLimitReset(
          ipCheck.resetInSeconds
        )}.`,
        rateLimitExceeded: true,
        retryAfterSeconds: ipCheck.resetInSeconds,
      }
    }

    // Record this login attempt (for IP-based tracking)
    await recordLoginAttempt(ipAddress)
  }

  try {
    // Attempt sign in
    await signIn("credentials", {
      email,
      password,
      redirect: false,
    })

    // If we reach here, login was successful
    // Reset failed login attempts for this email
    await resetFailedLoginAttempts(email)

    // Fetch user to get organization ID for audit log
    const user = await prisma.user.findUnique({
      where: { email },
      select: {
        id: true,
        organizationId: true,
        email: true,
        name: true,
      },
    })

    if (user) {
      // Create success audit log
      await createAuditLog({
        organizationId: user.organizationId,
        userId: user.id,
        action: AuditAction.LOGIN_SUCCESS,
        actionMetadata: {
          email: user.email,
          name: user.name,
        },
        ipAddress,
        userAgent,
      })
    }

    return {
      success: true,
      redirectTo: callbackUrl || "/dashboard",
    }
  } catch (error) {
    // Record failed login attempt for rate limiting
    await recordFailedLoginAttempt(email)
    // Login failed - could be wrong password or non-existent user
    // For security, we don't distinguish between these cases in the error message

    // Try to get organization ID for audit log
    // If user doesn't exist, we'll use a default/placeholder
    const user = await prisma.user.findUnique({
      where: { email },
      select: {
        id: true,
        organizationId: true,
      },
    })

    if (user) {
      // User exists but wrong password
      await createAuditLog({
        organizationId: user.organizationId,
        userId: user.id,
        action: AuditAction.LOGIN_FAILED,
        actionMetadata: {
          email,
          reason: "invalid_credentials",
        },
        ipAddress,
        userAgent,
      })
    } else {
      // User doesn't exist - log without organization/user ID
      // We'll create a "system" audit log for security monitoring
      // Note: This requires a system organization to exist in the database
      try {
        const systemOrg = await prisma.organization.findFirst({
          where: { name: "System" },
        })

        if (systemOrg) {
          await createAuditLog({
            organizationId: systemOrg.id,
            userId: null,
            action: AuditAction.LOGIN_FAILED,
            actionMetadata: {
              email,
              reason: "user_not_found",
            },
            ipAddress,
            userAgent,
          })
        }
      } catch (auditError) {
        // If we can't log to audit (e.g., no system org), just console log
        console.error("[AUTH] Failed to create audit log for failed login:", auditError)
      }
    }

    // Determine error message
    let errorMessage = "Invalid email or password"

    if (error instanceof AuthError) {
      // Handle specific Auth.js errors
      if (error.type === "CredentialsSignin") {
        errorMessage = "Invalid email or password"
      } else if (error.type === "CallbackRouteError") {
        errorMessage = "Authentication error. Please try again."
      }
    }

    return {
      success: false,
      error: errorMessage,
    }
  }
}

/**
 * Logout action with audit logging.
 *
 * @param userId - User ID (from session)
 * @param organizationId - Organization ID (from session)
 * @param email - User email (from session)
 */
export async function logoutWithAudit(
  userId: string,
  organizationId: string,
  email: string
): Promise<void> {
  const headersList = await headers()
  const { ipAddress, userAgent } = extractRequestMetadata(headersList)

  // Create audit log before signing out
  await createAuditLog({
    organizationId,
    userId,
    action: AuditAction.LOGOUT,
    actionMetadata: {
      email,
    },
    ipAddress,
    userAgent,
  })

  // Sign out
  await signOut({ redirect: false })
}
