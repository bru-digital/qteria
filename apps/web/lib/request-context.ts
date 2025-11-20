import { AsyncLocalStorage } from 'async_hooks'

/**
 * Request context for storing IP address and user agent
 * throughout the authentication flow.
 *
 * This uses Node.js AsyncLocalStorage to maintain request context
 * through async callbacks, allowing audit logs to capture complete metadata.
 */
interface RequestContext {
  ipAddress: string | null
  userAgent: string | null
}

export const requestContext = new AsyncLocalStorage<RequestContext>()

/**
 * Extract IP address from Next.js request headers.
 * Checks x-forwarded-for (proxy), x-real-ip (nginx), then falls back to remoteAddress.
 */
export function getIpAddress(headers: Headers): string | null {
  const forwardedFor = headers.get('x-forwarded-for')
  if (forwardedFor) {
    // x-forwarded-for can contain multiple IPs, take the first (client IP)
    return forwardedFor.split(',')[0].trim()
  }

  const realIp = headers.get('x-real-ip')
  if (realIp) {
    return realIp
  }

  // In local development, these headers might not be set
  return null
}

/**
 * Extract user agent from request headers
 */
export function getUserAgent(headers: Headers): string | null {
  return headers.get('user-agent')
}

/**
 * Get current request context (IP and user agent)
 * Returns null values if called outside of request context.
 */
export function getRequestContext(): RequestContext {
  return requestContext.getStore() || {
    ipAddress: null,
    userAgent: null
  }
}
