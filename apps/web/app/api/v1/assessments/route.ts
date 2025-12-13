import { NextRequest, NextResponse } from "next/server"
import { auth } from "@/lib/auth"
import { sign } from "jsonwebtoken"
import { randomUUID } from "crypto"

/**
 * API Proxy Route for Assessments
 *
 * This route acts as a proxy between the Next.js frontend and FastAPI backend.
 * It handles:
 * - Authentication via Next Auth session
 * - JWT token generation for FastAPI
 * - Request forwarding with proper headers
 *
 * Security Notes:
 * - JWT_SECRET must match between frontend and backend
 * - Tokens are generated server-side (never exposed to client)
 * - Session validation happens before token generation
 */

// Use API_URL environment variable (server-side only, not NEXT_PUBLIC_*)
// Default to localhost for development
const API_URL = process.env.API_URL || "http://localhost:8000"

/**
 * Get JWT secret with runtime validation
 * This is checked at request time, not build time, to support Vercel deployments
 * where environment variables are only available at runtime.
 */
function getJWTSecret(): string {
  const secret = process.env.JWT_SECRET
  if (!secret) {
    throw new Error("JWT_SECRET environment variable is required for API proxy")
  }
  return secret
}

/**
 * Generate a JWT token from Next Auth session data
 * Format matches what FastAPI backend expects (see apps/api/app/core/auth.py)
 *
 * Token Expiration: 30 minutes
 * - Tokens are regenerated on each request through this proxy
 * - Short expiration reduces risk if token is compromised
 * - User session is managed separately by NextAuth (typically 30 days)
 */
function generateJWTFromSession(session: any): string {
  const JWT_SECRET = getJWTSecret()
  const payload = {
    sub: session.user.id,
    email: session.user.email || "",
    role: session.user.role,
    // IMPORTANT: Backend expects snake_case 'org_id', not camelCase 'organizationId'
    // Session uses organizationId (TypeScript convention), but JWT must use org_id (Python convention)
    // See: apps/api/app/core/auth.py:177, apps/web/types/next-auth.d.ts:39
    org_id: session.user.organizationId,
    name: session.user.name || null,
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + (30 * 60), // 30 minutes
  }

  return sign(payload, JWT_SECRET, { algorithm: "HS256" })
}

/**
 * POST /api/v1/assessments
 * Start a new assessment (validation run)
 *
 * Request: JSON with:
 * - workflow_id: string (required)
 * - documents: AssessmentDocumentMapping[] (required, bucket_id + document_id pairs)
 *
 * Response: Assessment with 201 Created, status "pending"
 *
 * Journey Step 2: After uploading documents, start AI validation
 */
export async function POST(request: NextRequest) {
  try {
    // Get authenticated session
    const session = await auth()

    if (!session || !session.user) {
      return NextResponse.json(
        {
          error: {
            code: "INVALID_TOKEN",
            message: "Authentication required",
            request_id: randomUUID()
          }
        },
        { status: 401 }
      )
    }

    // Generate JWT token for FastAPI
    const jwtToken = generateJWTFromSession(session)

    // Get request body
    const body = await request.json()

    // Forward request to FastAPI backend
    const response = await fetch(`${API_URL}/v1/assessments`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${jwtToken}`,
      },
      body: JSON.stringify(body),
    })

    // Get response data
    const data = await response.json()

    // Return response with same status code
    return NextResponse.json(data, { status: response.status })
  } catch (error) {
    const requestId = randomUUID()
    console.error("[API Proxy - Assessments] Error:", { requestId, error })
    return NextResponse.json(
      {
        error: {
          code: "PROXY_ERROR",
          message: error instanceof Error ? error.message : "Internal server error",
          request_id: requestId,
        },
      },
      { status: 500 }
    )
  }
}

/**
 * GET /api/v1/assessments
 * List assessments for user's organization
 *
 * Query params:
 * - status: filter by status (optional)
 * - workflow_id: filter by workflow (optional)
 * - limit: pagination limit (optional, default 50)
 * - offset: pagination offset (optional, default 0)
 *
 * Response: Assessment[] with 200 OK
 *
 * Journey Step 3+: View assessment history and results
 */
export async function GET(request: NextRequest) {
  try {
    const session = await auth()

    if (!session || !session.user) {
      return NextResponse.json(
        {
          error: {
            code: "INVALID_TOKEN",
            message: "Authentication required",
            request_id: randomUUID()
          }
        },
        { status: 401 }
      )
    }

    const jwtToken = generateJWTFromSession(session)

    // Get query params from URL
    const { searchParams } = new URL(request.url)
    const queryString = searchParams.toString()

    // Forward request to FastAPI
    const apiUrl = queryString
      ? `${API_URL}/v1/assessments?${queryString}`
      : `${API_URL}/v1/assessments`

    const response = await fetch(apiUrl, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${jwtToken}`,
      },
    })

    const data = await response.json()
    return NextResponse.json(data, { status: response.status })
  } catch (error) {
    const requestId = randomUUID()
    console.error("[API Proxy - Assessments] Error:", { requestId, error })
    return NextResponse.json(
      {
        error: {
          code: "PROXY_ERROR",
          message: error instanceof Error ? error.message : "Internal server error",
          request_id: requestId,
        },
      },
      { status: 500 }
    )
  }
}
