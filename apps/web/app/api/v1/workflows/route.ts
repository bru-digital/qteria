import { NextRequest, NextResponse } from "next/server"
import { auth } from "@/lib/auth"
import { sign } from "jsonwebtoken"

/**
 * API Proxy Route for Workflows
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

const API_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

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
    exp: Math.floor(Date.now() / 1000) + (7 * 24 * 60 * 60), // 7 days
  }

  return sign(payload, JWT_SECRET, { algorithm: "HS256" })
}

/**
 * POST /api/v1/workflows
 * Create a new workflow
 */
export async function POST(request: NextRequest) {
  try {
    // Get authenticated session
    const session = await auth()

    if (!session || !session.user) {
      return NextResponse.json(
        { detail: { code: "UNAUTHORIZED", message: "Authentication required" } },
        { status: 401 }
      )
    }

    // Generate JWT token for FastAPI
    const jwtToken = generateJWTFromSession(session)

    // Get request body
    const body = await request.json()

    // Forward request to FastAPI backend
    const response = await fetch(`${API_URL}/v1/workflows`, {
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
    console.error("[API Proxy] Error:", error)
    return NextResponse.json(
      {
        detail: {
          code: "PROXY_ERROR",
          message: error instanceof Error ? error.message : "Internal server error",
        },
      },
      { status: 500 }
    )
  }
}

/**
 * GET /api/v1/workflows (future: list workflows)
 */
export async function GET(request: NextRequest) {
  try {
    const session = await auth()

    if (!session || !session.user) {
      return NextResponse.json(
        { detail: { code: "UNAUTHORIZED", message: "Authentication required" } },
        { status: 401 }
      )
    }

    const jwtToken = generateJWTFromSession(session)

    // Forward request to FastAPI
    const response = await fetch(`${API_URL}/v1/workflows`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${jwtToken}`,
      },
    })

    const data = await response.json()
    return NextResponse.json(data, { status: response.status })
  } catch (error) {
    console.error("[API Proxy] Error:", error)
    return NextResponse.json(
      {
        detail: {
          code: "PROXY_ERROR",
          message: error instanceof Error ? error.message : "Internal server error",
        },
      },
      { status: 500 }
    )
  }
}
