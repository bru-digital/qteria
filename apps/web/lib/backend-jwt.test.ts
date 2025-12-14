import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { generateBackendJWT, isValidSession } from './backend-jwt'
import { verify } from 'jsonwebtoken'

describe('Backend JWT Helper', () => {
  const mockJWTSecret = 'test-secret-key-32-characters-long'
  const originalEnv = process.env.JWT_SECRET

  beforeEach(() => {
    vi.useFakeTimers()
    process.env.JWT_SECRET = mockJWTSecret
  })

  afterEach(() => {
    vi.useRealTimers()
    process.env.JWT_SECRET = originalEnv
  })

  describe('generateBackendJWT', () => {
    const mockSession = {
      user: {
        id: 'user-123',
        email: 'test@example.com',
        role: 'process_manager',
        organizationId: 'org-456',
        name: 'Test User',
      },
    }

    it('should generate a valid JWT token with correct payload structure', () => {
      const now = Date.now()
      vi.setSystemTime(now)

      const token = generateBackendJWT(mockSession)

      // Verify it's a valid JWT token
      expect(token).toBeTruthy()
      expect(typeof token).toBe('string')
      expect(token.split('.')).toHaveLength(3) // JWT format: header.payload.signature

      // Decode and verify payload
      const decoded = verify(token, mockJWTSecret) as any
      expect(decoded.sub).toBe('user-123')
      expect(decoded.email).toBe('test@example.com')
      expect(decoded.role).toBe('process_manager')
      expect(decoded.org_id).toBe('org-456') // ✅ Critical: snake_case field name
      expect(decoded.name).toBe('Test User')
      expect(decoded.iat).toBe(Math.floor(now / 1000))
      expect(decoded.exp).toBe(Math.floor(now / 1000) + 30 * 60)
    })

    it('should use snake_case org_id field (not camelCase organizationId)', () => {
      const token = generateBackendJWT(mockSession)
      const decoded = verify(token, mockJWTSecret) as any

      // ✅ CRITICAL: Backend expects org_id (snake_case)
      expect(decoded.org_id).toBe('org-456')
      expect(decoded.organizationId).toBeUndefined()
    })

    it('should set expiration to 30 minutes from now', () => {
      const now = Date.now()
      vi.setSystemTime(now)

      const token = generateBackendJWT(mockSession)
      const decoded = verify(token, mockJWTSecret) as any

      const expectedExp = Math.floor(now / 1000) + 30 * 60
      expect(decoded.exp).toBe(expectedExp)
    })

    it('should handle missing optional fields (email, name)', () => {
      const sessionWithoutOptionals = {
        user: {
          id: 'user-123',
          email: null,
          role: 'project_handler',
          organizationId: 'org-456',
          name: null,
        },
      }

      const token = generateBackendJWT(sessionWithoutOptionals)
      const decoded = verify(token, mockJWTSecret) as any

      expect(decoded.email).toBe('')
      expect(decoded.name).toBeNull()
    })

    it('should throw error when JWT_SECRET is not set', () => {
      delete process.env.JWT_SECRET

      expect(() => generateBackendJWT(mockSession)).toThrow(
        'JWT_SECRET environment variable is required for backend authentication'
      )
      expect(() => generateBackendJWT(mockSession)).toThrow(/openssl rand -hex 32/)
    })

    it('should use HS256 algorithm', () => {
      const token = generateBackendJWT(mockSession)
      const [headerBase64] = token.split('.')
      const header = JSON.parse(Buffer.from(headerBase64, 'base64').toString())

      expect(header.alg).toBe('HS256')
    })

    it('should generate different tokens at different times', () => {
      const now = Date.now()
      vi.setSystemTime(now)
      const token1 = generateBackendJWT(mockSession)

      vi.setSystemTime(now + 1000) // 1 second later
      const token2 = generateBackendJWT(mockSession)

      expect(token1).not.toBe(token2) // iat will differ
    })

    it('should include all required fields for backend authentication', () => {
      const token = generateBackendJWT(mockSession)
      const decoded = verify(token, mockJWTSecret) as any

      // All required fields per backend TokenPayload model
      expect(decoded).toHaveProperty('sub')
      expect(decoded).toHaveProperty('email')
      expect(decoded).toHaveProperty('role')
      expect(decoded).toHaveProperty('org_id') // ✅ Critical for multi-tenancy
      expect(decoded).toHaveProperty('name')
      expect(decoded).toHaveProperty('iat')
      expect(decoded).toHaveProperty('exp')
    })
  })

  describe('isValidSession', () => {
    it('should return true for valid session object', () => {
      const validSession = {
        user: {
          id: 'user-123',
          email: 'test@example.com',
          role: 'process_manager',
          organizationId: 'org-456',
          name: 'Test User',
        },
      }

      expect(isValidSession(validSession)).toBe(true)
    })

    it('should return true for valid session with optional null fields', () => {
      const validSession = {
        user: {
          id: 'user-123',
          role: 'project_handler',
          organizationId: 'org-456',
          email: null,
          name: null,
        },
      }

      expect(isValidSession(validSession)).toBe(true)
    })

    it('should return false for null', () => {
      expect(isValidSession(null)).toBe(false)
    })

    it('should return false for undefined', () => {
      expect(isValidSession(undefined)).toBe(false)
    })

    it('should return false for non-object values', () => {
      expect(isValidSession('string')).toBe(false)
      expect(isValidSession(123)).toBe(false)
      expect(isValidSession(true)).toBe(false)
    })

    it('should return false when user field is missing', () => {
      const invalidSession = {
        notUser: {},
      }

      expect(isValidSession(invalidSession)).toBe(false)
    })

    it('should return false when user is null', () => {
      const invalidSession = {
        user: null,
      }

      expect(isValidSession(invalidSession)).toBe(false)
    })

    it('should return false when user is not an object', () => {
      const invalidSession = {
        user: 'not-an-object',
      }

      expect(isValidSession(invalidSession)).toBe(false)
    })

    it('should return false when required id field is missing', () => {
      const invalidSession = {
        user: {
          role: 'process_manager',
          organizationId: 'org-456',
        },
      }

      expect(isValidSession(invalidSession)).toBe(false)
    })

    it('should return false when required role field is missing', () => {
      const invalidSession = {
        user: {
          id: 'user-123',
          organizationId: 'org-456',
        },
      }

      expect(isValidSession(invalidSession)).toBe(false)
    })

    it('should return false when required organizationId field is missing', () => {
      const invalidSession = {
        user: {
          id: 'user-123',
          role: 'process_manager',
        },
      }

      expect(isValidSession(invalidSession)).toBe(false)
    })

    it('should return false when id is not a string', () => {
      const invalidSession = {
        user: {
          id: 123,
          role: 'process_manager',
          organizationId: 'org-456',
        },
      }

      expect(isValidSession(invalidSession)).toBe(false)
    })

    it('should return false when role is not a string', () => {
      const invalidSession = {
        user: {
          id: 'user-123',
          role: 123,
          organizationId: 'org-456',
        },
      }

      expect(isValidSession(invalidSession)).toBe(false)
    })

    it('should return false when organizationId is not a string', () => {
      const invalidSession = {
        user: {
          id: 'user-123',
          role: 'process_manager',
          organizationId: 123,
        },
      }

      expect(isValidSession(invalidSession)).toBe(false)
    })

    it('should return false for empty object', () => {
      expect(isValidSession({})).toBe(false)
    })

    it('should return false for array', () => {
      expect(isValidSession([])).toBe(false)
    })
  })

  describe('Multi-tenancy Security', () => {
    it('should correctly map organizationId to org_id for backend', () => {
      const session = {
        user: {
          id: 'user-123',
          email: 'test@example.com',
          role: 'process_manager',
          organizationId: 'org-correct-tenant',
          name: 'Test User',
        },
      }

      const token = generateBackendJWT(session)
      const decoded = verify(token, mockJWTSecret) as any

      // ✅ CRITICAL: Backend uses org_id for multi-tenancy enforcement
      expect(decoded.org_id).toBe('org-correct-tenant')
    })

    it('should generate different tokens for different organizations', () => {
      const now = Date.now()
      vi.setSystemTime(now)

      const session1 = {
        user: {
          id: 'user-123',
          email: 'test@example.com',
          role: 'process_manager',
          organizationId: 'org-tenant-1',
          name: 'User 1',
        },
      }

      const session2 = {
        user: {
          id: 'user-123',
          email: 'test@example.com',
          role: 'process_manager',
          organizationId: 'org-tenant-2',
          name: 'User 1',
        },
      }

      const token1 = generateBackendJWT(session1)
      const token2 = generateBackendJWT(session2)

      const decoded1 = verify(token1, mockJWTSecret) as any
      const decoded2 = verify(token2, mockJWTSecret) as any

      expect(decoded1.org_id).toBe('org-tenant-1')
      expect(decoded2.org_id).toBe('org-tenant-2')
      expect(token1).not.toBe(token2)
    })
  })
})
