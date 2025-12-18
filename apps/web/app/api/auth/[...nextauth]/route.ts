import { handlers } from '@/lib/auth'
import { requestContext, getIpAddress, getUserAgent } from '@/lib/request-context'
import { NextRequest } from 'next/server'

/**
 * Auth.js API route handlers (Node.js runtime).
 * Uses full authOptions with credential provider (bcrypt + Prisma).
 *
 * This is separate from middleware which uses baseAuthConfig.
 */
const { GET: authGET, POST: authPOST } = handlers

/**
 * Wrap GET handler to capture request context (IP, user agent) for audit logging.
 * Uses AsyncLocalStorage to pass context through Auth.js callbacks.
 */
export async function GET(request: NextRequest) {
  const ipAddress = getIpAddress(request.headers)
  const userAgent = getUserAgent(request.headers)

  return requestContext.run({ ipAddress, userAgent }, () => {
    return authGET(request)
  })
}

/**
 * Wrap POST handler to capture request context (IP, user agent) for audit logging.
 * Uses AsyncLocalStorage to pass context through Auth.js callbacks.
 */
export async function POST(request: NextRequest) {
  const ipAddress = getIpAddress(request.headers)
  const userAgent = getUserAgent(request.headers)

  return requestContext.run({ ipAddress, userAgent }, () => {
    return authPOST(request)
  })
}
