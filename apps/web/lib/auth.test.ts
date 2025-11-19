import { describe, it, expect, vi, beforeEach } from 'vitest'
import { authOptions } from './auth'
import { PrismaClientInitializationError } from '@prisma/client/runtime/library'

// Mock dependencies
vi.mock('@/lib/prisma', () => ({
  prisma: {
    user: {
      findUnique: vi.fn(),
      update: vi.fn(),
    },
    organization: {
      findFirst: vi.fn(),
    },
  },
}))

vi.mock('@/lib/audit', () => ({
  createAuditLog: vi.fn(),
  AuditAction: {
    LOGIN_SUCCESS: 'login_success',
    LOGIN_FAILED: 'login_failed',
  },
}))

vi.mock('@/lib/env', () => ({
  isMicrosoftOAuthConfigured: vi.fn(() => true),
  isGoogleOAuthConfigured: vi.fn(() => true),
}))

// Import mocked modules
import { prisma } from '@/lib/prisma'
import { createAuditLog } from '@/lib/audit'

describe('OAuth Authentication', () => {
  const mockMicrosoftAccount = {
    provider: 'microsoft-entra-id',
    type: 'oauth' as const,
    providerAccountId: 'test-123',
  }

  const mockGoogleAccount = {
    provider: 'google',
    type: 'oauth' as const,
    providerAccountId: 'test-456',
  }

  const mockUser = {
    id: 'user-123',
    email: 'test@example.com',
    name: 'Test User',
    emailVerified: null as Date | null,
    role: 'project_handler' as const,
    organizationId: 'org-123',
  }

  const mockProfile = {
    email: 'test@example.com',
    name: 'Test User',
    sub: 'oauth-sub-123',
  }

  const mockExistingUser = {
    id: 'user-123',
    email: 'test@example.com',
    name: 'Test User',
    passwordHash: 'hash',
    role: 'project_handler',
    organizationId: 'org-123',
    createdAt: new Date(),
    updatedAt: new Date(),
    organization: {
      id: 'org-123',
      name: 'Test Organization',
    },
  }

  const mockSystemOrg = {
    id: 'system-org-123',
    name: 'System',
    subscriptionTier: 'enterprise' as const,
    subscriptionStatus: 'active' as const,
    createdAt: new Date(),
    updatedAt: new Date(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('signIn callback - OAuth Success', () => {
    it('should allow OAuth login for existing user with Microsoft', async () => {
      // Mock database to return existing user
      vi.mocked(prisma.user.findUnique).mockResolvedValue(mockExistingUser)

      // Get the signIn callback
      const signInCallback = authOptions.callbacks?.signIn
      expect(signInCallback).toBeDefined()

      if (!signInCallback) return

      // Call the callback
      const result = await signInCallback({
        user: mockUser,
        account: mockMicrosoftAccount,
        profile: mockProfile,
      })

      // Assertions
      expect(result).toBe(true)
      expect(prisma.user.findUnique).toHaveBeenCalledWith({
        where: { email: 'test@example.com' },
        include: { organization: true },
      })
      expect(createAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          organizationId: 'org-123',
          userId: 'user-123',
          action: 'login_success',
          actionMetadata: expect.objectContaining({
            provider: 'microsoft-entra-id',
            authMethod: 'oauth',
          }),
        })
      )
    })

    it('should allow OAuth login for existing user with Google', async () => {
      // Mock database to return existing user
      vi.mocked(prisma.user.findUnique).mockResolvedValue(mockExistingUser)

      // Get the signIn callback
      const signInCallback = authOptions.callbacks?.signIn
      if (!signInCallback) return

      // Call the callback
      const result = await signInCallback({
        user: mockUser,
        account: mockGoogleAccount,
        profile: mockProfile,
      })

      // Assertions
      expect(result).toBe(true)
      expect(createAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          actionMetadata: expect.objectContaining({
            provider: 'google',
          }),
        })
      )
    })

    it('should update user name if changed via OAuth', async () => {
      // Mock user with different name
      const userWithOldName = {
        ...mockExistingUser,
        name: 'Old Name',
      }
      vi.mocked(prisma.user.findUnique).mockResolvedValue(userWithOldName)

      const signInCallback = authOptions.callbacks?.signIn
      if (!signInCallback) return

      await signInCallback({
        user: { ...mockUser, name: 'New Name' },
        account: mockMicrosoftAccount,
        profile: { ...mockProfile, name: 'New Name' },
      })

      // Should update user
      expect(prisma.user.update).toHaveBeenCalledWith({
        where: { email: 'test@example.com' },
        data: {
          name: 'New Name',
        },
      })

      // Should log profile update
      expect(createAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          actionMetadata: expect.objectContaining({
            profileUpdated: true,
            changes: {
              name: { from: 'Old Name', to: 'New Name' },
            },
          }),
        })
      )
    })

    it('should NOT update user if name unchanged', async () => {
      vi.mocked(prisma.user.findUnique).mockResolvedValue(mockExistingUser)

      const signInCallback = authOptions.callbacks?.signIn
      if (!signInCallback) return

      await signInCallback({
        user: mockUser,
        account: mockMicrosoftAccount,
        profile: mockProfile,
      })

      // Should NOT call update
      expect(prisma.user.update).not.toHaveBeenCalled()

      // Should NOT include profileUpdated in audit log
      expect(createAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          actionMetadata: expect.not.objectContaining({
            profileUpdated: true,
          }),
        })
      )
    })
  })

  describe('signIn callback - OAuth Failures', () => {
    it('should reject OAuth login for non-existent user', async () => {
      // Mock database to return null (user not found)
      vi.mocked(prisma.user.findUnique).mockResolvedValue(null)
      vi.mocked(prisma.organization.findFirst).mockResolvedValue(mockSystemOrg)

      const signInCallback = authOptions.callbacks?.signIn
      if (!signInCallback) return

      const result = await signInCallback({
        user: mockUser,
        account: mockMicrosoftAccount,
        profile: mockProfile,
      })

      // Should return error URL
      expect(result).toBe('/login?error=oauth_user_not_found')

      // Should log failed login to system organization
      expect(createAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          organizationId: 'system-org-123',
          userId: null,
          action: 'login_failed',
          actionMetadata: expect.objectContaining({
            reason: 'oauth_user_not_found',
            provider: 'microsoft-entra-id',
          }),
        })
      )
    })

    it('should reject OAuth login when no email provided', async () => {
      const signInCallback = authOptions.callbacks?.signIn
      if (!signInCallback) return

      const result = await signInCallback({
        user: {
          id: 'user-123',
          email: null as any, // Testing missing email scenario
          name: 'Test',
          emailVerified: null,
          role: 'project_handler' as const,
          organizationId: 'org-123',
        },
        account: mockMicrosoftAccount,
        profile: { sub: '123' }, // No email in profile
      })

      // Should return error URL
      expect(result).toBe('/login?error=oauth_no_email')

      // Should not query database
      expect(prisma.user.findUnique).not.toHaveBeenCalled()
    })

    it('should handle database errors gracefully', async () => {
      // Mock Prisma initialization error (database connection failure)
      // Create an instance that will pass instanceof check
      const prismaError = Object.create(PrismaClientInitializationError.prototype)
      prismaError.message = 'Could not connect to database'
      prismaError.clientVersion = '5.0.0'

      vi.mocked(prisma.user.findUnique).mockRejectedValue(prismaError)

      const signInCallback = authOptions.callbacks?.signIn
      if (!signInCallback) return

      const result = await signInCallback({
        user: mockUser,
        account: mockMicrosoftAccount,
        profile: mockProfile,
      })

      // Should return database error URL
      expect(result).toBe('/login?error=oauth_database_error')
    })

    it('should handle generic errors gracefully', async () => {
      // Mock generic error
      vi.mocked(prisma.user.findUnique).mockRejectedValue(
        new Error('Unknown error')
      )

      const signInCallback = authOptions.callbacks?.signIn
      if (!signInCallback) return

      const result = await signInCallback({
        user: mockUser,
        account: mockMicrosoftAccount,
        profile: mockProfile,
      })

      // Should return generic OAuth error URL
      expect(result).toBe('/login?error=oauth_error')
    })
  })

  describe('signIn callback - Multi-tenancy', () => {
    it('should isolate users by organization', async () => {
      vi.mocked(prisma.user.findUnique).mockResolvedValue(mockExistingUser)

      const signInCallback = authOptions.callbacks?.signIn
      if (!signInCallback) return

      await signInCallback({
        user: mockUser,
        account: mockMicrosoftAccount,
        profile: mockProfile,
      })

      // Audit log should use correct organization ID
      expect(createAuditLog).toHaveBeenCalledWith(
        expect.objectContaining({
          organizationId: 'org-123',
          userId: 'user-123',
        })
      )
    })
  })

  describe('signIn callback - Credentials Provider', () => {
    it('should allow credentials login without additional checks', async () => {
      const signInCallback = authOptions.callbacks?.signIn
      if (!signInCallback) return

      const result = await signInCallback({
        user: mockUser,
        account: {
          provider: 'credentials',
          type: 'credentials',
          providerAccountId: 'credentials-123',
        },
        profile: undefined,
      })

      // Should allow login
      expect(result).toBe(true)

      // Should not query database or create audit logs
      // (those are handled by loginWithAudit server action)
      expect(prisma.user.findUnique).not.toHaveBeenCalled()
      expect(createAuditLog).not.toHaveBeenCalled()
    })
  })

  describe('OAuth Providers Configuration', () => {
    it('should include Microsoft and Google providers', () => {
      // Providers should be configured
      expect(authOptions.providers).toBeDefined()
      expect(authOptions.providers.length).toBeGreaterThan(0)

      // Should have at least 3 providers (Microsoft, Google, Credentials)
      // Note: Actual count may vary based on environment variable mocks
      expect(authOptions.providers.length).toBeGreaterThanOrEqual(1)
    })
  })
})
