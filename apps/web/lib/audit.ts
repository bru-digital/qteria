/**
 * Audit logging utility for SOC2/ISO 27001 compliance.
 *
 * Logs security-relevant events to the audit_logs table including:
 * - Authentication events (login, logout, failed attempts)
 * - Resource access and modifications
 * - Administrative actions
 */

import { prisma } from "@/lib/prisma"

/**
 * Audit log action types
 */
export const AuditAction = {
  // Authentication
  LOGIN_SUCCESS: "login_success",
  LOGIN_FAILED: "login_failed",
  LOGOUT: "logout",

  // Resource actions (for future use)
  WORKFLOW_CREATE: "workflow_create",
  WORKFLOW_UPDATE: "workflow_update",
  WORKFLOW_DELETE: "workflow_delete",
  ASSESSMENT_CREATE: "assessment_create",
  ASSESSMENT_VIEW: "assessment_view",
  DOCUMENT_UPLOAD: "document_upload",
} as const

export type AuditActionType = typeof AuditAction[keyof typeof AuditAction]

/**
 * Parameters for creating an audit log entry
 */
export interface CreateAuditLogParams {
  organizationId: string
  userId?: string | null
  action: AuditActionType
  resourceType?: string | null
  resourceId?: string | null
  actionMetadata?: Record<string, any> | null
  ipAddress?: string | null
  userAgent?: string | null
}

/**
 * Create an audit log entry in the database.
 *
 * @param params - Audit log parameters
 * @returns The created audit log entry
 *
 * @example
 * ```typescript
 * await createAuditLog({
 *   organizationId: user.organizationId,
 *   userId: user.id,
 *   action: AuditAction.LOGIN_SUCCESS,
 *   actionMetadata: { email: user.email },
 *   ipAddress: "192.168.1.1",
 *   userAgent: "Mozilla/5.0..."
 * })
 * ```
 */
export async function createAuditLog(params: CreateAuditLogParams) {
  try {
    const auditLog = await prisma.auditLog.create({
      data: {
        organizationId: params.organizationId,
        userId: params.userId ?? null,
        action: params.action,
        resourceType: params.resourceType ?? null,
        resourceId: params.resourceId ?? null,
        actionMetadata: params.actionMetadata ? params.actionMetadata : undefined,
        ipAddress: params.ipAddress ?? null,
        userAgent: params.userAgent ?? null,
      },
    })

    return auditLog
  } catch (error) {
    // Log error but don't throw - audit logging should not break the main flow
    console.error("[AUDIT] Failed to create audit log:", error)
    return null
  }
}

/**
 * Extract IP address from request headers.
 * Checks common proxy headers first, then falls back to direct connection IP.
 *
 * @param headers - Request headers (from Next.js request or headers())
 * @returns IP address or null if not available
 */
export function extractIpAddress(headers: Headers): string | null {
  // Check common proxy headers in order of priority
  const xForwardedFor = headers.get("x-forwarded-for")
  if (xForwardedFor) {
    // x-forwarded-for can contain multiple IPs (client, proxy1, proxy2, ...)
    // The first one is the original client IP
    const ips = xForwardedFor.split(",").map(ip => ip.trim())
    return ips[0] || null
  }

  const xRealIp = headers.get("x-real-ip")
  if (xRealIp) {
    return xRealIp
  }

  // Vercel-specific header
  const cfConnectingIp = headers.get("cf-connecting-ip")
  if (cfConnectingIp) {
    return cfConnectingIp
  }

  // Note: In serverless environments (Vercel, etc), direct socket IP is not available
  // If none of the headers are present, return null
  return null
}

/**
 * Extract user agent from request headers.
 *
 * @param headers - Request headers (from Next.js request or headers())
 * @returns User agent string or null if not available
 */
export function extractUserAgent(headers: Headers): string | null {
  return headers.get("user-agent")
}

/**
 * Helper to extract both IP and user agent from headers
 *
 * @param headers - Request headers
 * @returns Object with ipAddress and userAgent
 */
export function extractRequestMetadata(headers: Headers) {
  return {
    ipAddress: extractIpAddress(headers),
    userAgent: extractUserAgent(headers),
  }
}
