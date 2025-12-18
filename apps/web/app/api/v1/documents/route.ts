import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/lib/auth'
import { generateBackendJWT } from '@/lib/backend-jwt'
import { randomUUID } from 'crypto'

/**
 * API Proxy Route for Document Uploads
 *
 * This route acts as a proxy between the Next.js frontend and FastAPI backend.
 * It handles:
 * - Authentication via Next Auth session
 * - JWT token generation for FastAPI
 * - FormData forwarding for file uploads
 * - Request forwarding with proper headers
 *
 * Security Notes:
 * - JWT_SECRET must match between frontend and backend
 * - Tokens are generated server-side (never exposed to client)
 * - Session validation happens before token generation
 * - File size and type validation happens on backend
 */

// Use API_URL environment variable (server-side only, not NEXT_PUBLIC_*)
// Default to localhost for development
const API_URL = process.env.API_URL || 'http://localhost:8000'

/**
 * POST /api/v1/documents
 * Upload one or more documents to Vercel Blob storage
 *
 * Request: multipart/form-data with:
 * - file: File (required, PDF/DOCX, max 50MB)
 * - bucket_id: string (optional, for validation)
 *
 * Response: DocumentMetadata[] with 201 Created
 *
 * Journey Step 2: Project Handler uploads documents to workflow buckets
 */
export async function POST(request: NextRequest) {
  try {
    // Get authenticated session
    const session = await auth()

    if (!session || !session.user) {
      return NextResponse.json(
        {
          error: {
            code: 'UNAUTHORIZED',
            message: 'Authentication required',
            request_id: randomUUID(),
          },
        },
        { status: 401 }
      )
    }

    // Generate JWT token for FastAPI
    const jwtToken = generateBackendJWT(session)

    // Get FormData from request (contains file upload)
    const formData = await request.formData()

    // Forward request to FastAPI backend
    // Note: We pass FormData directly - fetch will set correct Content-Type with boundary
    const response = await fetch(`${API_URL}/v1/documents`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${jwtToken}`,
        // Don't set Content-Type - let fetch set it with multipart boundary
      },
      body: formData,
    })

    // Get response data
    const data = await response.json()

    // Return response with same status code
    return NextResponse.json(data, { status: response.status })
  } catch (error) {
    const requestId = randomUUID()
    console.error('[API Proxy - Documents] Error:', { requestId, error })
    return NextResponse.json(
      {
        error: {
          code: 'INTERNAL_ERROR',
          message: error instanceof Error ? error.message : 'Internal server error',
          request_id: requestId,
        },
      },
      { status: 500 }
    )
  }
}
