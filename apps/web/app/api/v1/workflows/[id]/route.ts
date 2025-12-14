import { NextRequest, NextResponse } from "next/server"
import { auth } from "@/lib/auth"
import { sign } from "jsonwebtoken"
import { randomUUID } from "crypto"

/**
 * API Proxy Route for Single Workflow
 *
 * This route acts as a proxy between the Next.js frontend and FastAPI backend
 * for fetching a single workflow by ID.
 *
 * Endpoint: GET /api/v1/workflows/:id
 * Backend: GET /v1/workflows/:id
 *
 * Security Notes:
 * - JWT_SECRET must match between frontend and backend
 * - Tokens are generated server-side (never exposed to client)
 * - Session validation happens before token generation
 * - Multi-tenancy enforced by backend (returns 404 if workflow not in user's org)
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
    organizationId: session.user.organizationId,
    name: session.user.name || null,
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + (30 * 60), // 30 minutes
  }

  return sign(payload, JWT_SECRET, { algorithm: "HS256" })
}

/**
 * GET /api/v1/workflows/:id
 * Fetch a single workflow with buckets and criteria
 *
 * Response (200 OK):
 * {
 *   "id": "workflow_abc123",
 *   "name": "Medical Device - Class II",
 *   "description": "...",
 *   "buckets": [...],
 *   "criteria": [...],
 *   "created_at": "2024-01-15T10:30:00Z",
 *   "updated_at": "2024-01-15T10:30:00Z"
 * }
 *
 * Errors:
 * - 401: Authentication required
 * - 404: Workflow not found or not in user's organization
 * - 500: Internal server error
 */
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    // Get authenticated session
    const session = await auth()

    if (!session || !session.user) {
      return NextResponse.json(
        {
          error: {
            code: "INVALID_TOKEN",
            message: "Authentication required",
          },
        },
        { status: 401 }
      )
    }

    // Await the params to get the id
    const { id } = await params

    // Generate JWT token for FastAPI
    const jwtToken = generateJWTFromSession(session)

    // Forward request to FastAPI backend
    const response = await fetch(`${API_URL}/v1/workflows/${id}`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${jwtToken}`,
        "Content-Type": "application/json",
      },
    })

    // Get response data
    const data = await response.json()

    // If not OK, return error with original status code
    if (!response.ok) {
      return NextResponse.json(data, { status: response.status })
    }

    // Return successful response
    return NextResponse.json(data)
  } catch (error) {
    const requestId = randomUUID()
    console.error("[API Proxy] Error fetching workflow:", { requestId, error })
    return NextResponse.json(
      {
        error: {
          code: "INTERNAL_ERROR",
          message: "Failed to fetch workflow",
          request_id: requestId,
        },
      },
      { status: 500 }
    )
  }
}
