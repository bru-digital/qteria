import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { validateEnv, getEnv, getOptionalEnv, isMicrosoftOAuthConfigured, isGoogleOAuthConfigured } from './env'

describe('validateEnv', () => {
  // Store original env vars to restore after tests
  const originalEnv = { ...process.env }

  beforeEach(() => {
    // Reset environment to clean state before each test
    process.env = { ...originalEnv }
  })

  afterEach(() => {
    // Restore original environment after each test
    process.env = originalEnv
  })

  it('should pass validation when all required env vars are set', () => {
    process.env.NEXTAUTH_SECRET = 'test-secret-key-with-at-least-32-characters-for-security'
    process.env.NEXTAUTH_URL = 'http://localhost:3000'
    process.env.DATABASE_URL = 'postgresql://user:password@localhost:5432/qteria'

    expect(() => validateEnv()).not.toThrow()
  })

  it('should throw error when NEXTAUTH_SECRET is missing', () => {
    delete process.env.NEXTAUTH_SECRET
    process.env.NEXTAUTH_URL = 'http://localhost:3000'
    process.env.DATABASE_URL = 'postgresql://user:password@localhost:5432/qteria'

    expect(() => validateEnv()).toThrow(/NEXTAUTH_SECRET/)
    expect(() => validateEnv()).toThrow(/Used for JWT signing/)
  })

  it('should throw error when NEXTAUTH_URL is missing', () => {
    process.env.NEXTAUTH_SECRET = 'test-secret-key-with-at-least-32-characters-for-security'
    delete process.env.NEXTAUTH_URL
    process.env.DATABASE_URL = 'postgresql://user:password@localhost:5432/qteria'

    expect(() => validateEnv()).toThrow(/NEXTAUTH_URL/)
    expect(() => validateEnv()).toThrow(/Base URL for Auth.js callbacks/)
  })

  it('should throw error when DATABASE_URL is missing', () => {
    process.env.NEXTAUTH_SECRET = 'test-secret-key-with-at-least-32-characters-for-security'
    process.env.NEXTAUTH_URL = 'http://localhost:3000'
    delete process.env.DATABASE_URL

    expect(() => validateEnv()).toThrow(/DATABASE_URL/)
    expect(() => validateEnv()).toThrow(/PostgreSQL connection string/)
  })

  it('should throw error when multiple required vars are missing', () => {
    delete process.env.NEXTAUTH_SECRET
    delete process.env.NEXTAUTH_URL
    delete process.env.DATABASE_URL

    expect(() => validateEnv()).toThrow(/Environment Variable Validation Failed/)
  })

  it('should warn when NEXTAUTH_SECRET is too short', () => {
    process.env.NEXTAUTH_SECRET = 'short-secret' // Less than 32 characters
    process.env.NEXTAUTH_URL = 'http://localhost:3000'
    process.env.DATABASE_URL = 'postgresql://user:password@localhost:5432/qteria'

    expect(() => validateEnv()).toThrow(/NEXTAUTH_SECRET is too short/)
    expect(() => validateEnv()).toThrow(/At least 32 characters/)
  })

  it('should warn when DATABASE_URL is not PostgreSQL', () => {
    process.env.NEXTAUTH_SECRET = 'test-secret-key-with-at-least-32-characters-for-security'
    process.env.NEXTAUTH_URL = 'http://localhost:3000'
    process.env.DATABASE_URL = 'mysql://user:password@localhost:3306/qteria'

    expect(() => validateEnv()).toThrow(/doesn't look like a PostgreSQL/)
  })

  it('should accept DATABASE_URL with postgres:// prefix', () => {
    process.env.NEXTAUTH_SECRET = 'test-secret-key-with-at-least-32-characters-for-security'
    process.env.NEXTAUTH_URL = 'http://localhost:3000'
    process.env.DATABASE_URL = 'postgres://user:password@localhost:5432/qteria'

    expect(() => validateEnv()).not.toThrow()
  })

  it('should accept DATABASE_URL with postgresql:// prefix', () => {
    process.env.NEXTAUTH_SECRET = 'test-secret-key-with-at-least-32-characters-for-security'
    process.env.NEXTAUTH_URL = 'http://localhost:3000'
    process.env.DATABASE_URL = 'postgresql://user:password@localhost:5432/qteria'

    expect(() => validateEnv()).not.toThrow()
  })

  it('should treat empty string as missing env var', () => {
    process.env.NEXTAUTH_SECRET = ''
    process.env.NEXTAUTH_URL = 'http://localhost:3000'
    process.env.DATABASE_URL = 'postgresql://user:password@localhost:5432/qteria'

    expect(() => validateEnv()).toThrow(/NEXTAUTH_SECRET/)
  })

  it('should treat whitespace-only string as missing env var', () => {
    process.env.NEXTAUTH_SECRET = '   '
    process.env.NEXTAUTH_URL = 'http://localhost:3000'
    process.env.DATABASE_URL = 'postgresql://user:password@localhost:5432/qteria'

    expect(() => validateEnv()).toThrow(/NEXTAUTH_SECRET/)
  })
})

describe('validateEnv - OAuth validation', () => {
  const originalEnv = { ...process.env }

  beforeEach(() => {
    process.env = { ...originalEnv }
    // Set required vars for these tests
    process.env.NEXTAUTH_SECRET = 'test-secret-key-with-at-least-32-characters-for-security'
    process.env.NEXTAUTH_URL = 'http://localhost:3000'
    process.env.DATABASE_URL = 'postgresql://user:password@localhost:5432/qteria'
  })

  afterEach(() => {
    process.env = originalEnv
  })

  it('should warn when MICROSOFT_CLIENT_ID is set but MICROSOFT_CLIENT_SECRET is missing', () => {
    process.env.MICROSOFT_CLIENT_ID = 'test-client-id'
    delete process.env.MICROSOFT_CLIENT_SECRET

    expect(() => validateEnv()).toThrow(/MICROSOFT_CLIENT_ID is set but MICROSOFT_CLIENT_SECRET is missing/)
    expect(() => validateEnv()).toThrow(/See docs\/OAUTH_SETUP.md/)
  })

  it('should warn when MICROSOFT_CLIENT_SECRET is set but MICROSOFT_CLIENT_ID is missing', () => {
    delete process.env.MICROSOFT_CLIENT_ID
    process.env.MICROSOFT_CLIENT_SECRET = 'test-client-secret'

    expect(() => validateEnv()).toThrow(/MICROSOFT_CLIENT_SECRET is set but MICROSOFT_CLIENT_ID is missing/)
  })

  it('should pass when both Microsoft OAuth vars are set', () => {
    process.env.MICROSOFT_CLIENT_ID = 'test-client-id'
    process.env.MICROSOFT_CLIENT_SECRET = 'test-client-secret'

    expect(() => validateEnv()).not.toThrow()
  })

  it('should pass when neither Microsoft OAuth var is set', () => {
    delete process.env.MICROSOFT_CLIENT_ID
    delete process.env.MICROSOFT_CLIENT_SECRET

    expect(() => validateEnv()).not.toThrow()
  })

  it('should warn when GOOGLE_CLIENT_ID is set but GOOGLE_CLIENT_SECRET is missing', () => {
    process.env.GOOGLE_CLIENT_ID = 'test-client-id'
    delete process.env.GOOGLE_CLIENT_SECRET

    expect(() => validateEnv()).toThrow(/GOOGLE_CLIENT_ID is set but GOOGLE_CLIENT_SECRET is missing/)
    expect(() => validateEnv()).toThrow(/See docs\/OAUTH_SETUP.md/)
  })

  it('should warn when GOOGLE_CLIENT_SECRET is set but GOOGLE_CLIENT_ID is missing', () => {
    delete process.env.GOOGLE_CLIENT_ID
    process.env.GOOGLE_CLIENT_SECRET = 'test-client-secret'

    expect(() => validateEnv()).toThrow(/GOOGLE_CLIENT_SECRET is set but GOOGLE_CLIENT_ID is missing/)
  })

  it('should pass when both Google OAuth vars are set', () => {
    process.env.GOOGLE_CLIENT_ID = 'test-client-id.apps.googleusercontent.com'
    process.env.GOOGLE_CLIENT_SECRET = 'test-client-secret'

    expect(() => validateEnv()).not.toThrow()
  })

  it('should pass when neither Google OAuth var is set', () => {
    delete process.env.GOOGLE_CLIENT_ID
    delete process.env.GOOGLE_CLIENT_SECRET

    expect(() => validateEnv()).not.toThrow()
  })

  it('should handle both OAuth providers being configured', () => {
    process.env.MICROSOFT_CLIENT_ID = 'microsoft-client-id'
    process.env.MICROSOFT_CLIENT_SECRET = 'microsoft-client-secret'
    process.env.GOOGLE_CLIENT_ID = 'google-client-id.apps.googleusercontent.com'
    process.env.GOOGLE_CLIENT_SECRET = 'google-client-secret'

    expect(() => validateEnv()).not.toThrow()
  })

  it('should warn for both OAuth providers if misconfigured', () => {
    process.env.MICROSOFT_CLIENT_ID = 'microsoft-client-id'
    delete process.env.MICROSOFT_CLIENT_SECRET
    process.env.GOOGLE_CLIENT_ID = 'google-client-id'
    delete process.env.GOOGLE_CLIENT_SECRET

    expect(() => validateEnv()).toThrow(/MICROSOFT_CLIENT_ID is set but MICROSOFT_CLIENT_SECRET is missing/)
    expect(() => validateEnv()).toThrow(/GOOGLE_CLIENT_ID is set but GOOGLE_CLIENT_SECRET is missing/)
  })

  it('should treat empty string OAuth credentials as missing', () => {
    process.env.MICROSOFT_CLIENT_ID = ''
    process.env.MICROSOFT_CLIENT_SECRET = 'test-secret'

    // Empty string CLIENT_ID with set CLIENT_SECRET should warn about mismatch
    expect(() => validateEnv()).toThrow(/MICROSOFT_CLIENT_SECRET is set but MICROSOFT_CLIENT_ID is missing/)
  })

  it('should treat whitespace-only OAuth credentials as missing', () => {
    process.env.MICROSOFT_CLIENT_ID = '   '
    process.env.MICROSOFT_CLIENT_SECRET = 'test-secret'

    // Whitespace-only CLIENT_ID with set CLIENT_SECRET should warn about mismatch
    expect(() => validateEnv()).toThrow(/MICROSOFT_CLIENT_SECRET is set but MICROSOFT_CLIENT_ID is missing/)
  })
})

describe('getEnv', () => {
  const originalEnv = { ...process.env }

  beforeEach(() => {
    process.env = { ...originalEnv }
  })

  afterEach(() => {
    process.env = originalEnv
  })

  it('should return environment variable value', () => {
    process.env.NEXTAUTH_SECRET = 'test-secret-value'
    expect(getEnv('NEXTAUTH_SECRET')).toBe('test-secret-value')
  })

  it('should return environment variable for DATABASE_URL', () => {
    process.env.DATABASE_URL = 'postgresql://user:password@localhost:5432/qteria'
    expect(getEnv('DATABASE_URL')).toBe('postgresql://user:password@localhost:5432/qteria')
  })

  it('should throw error if required variable is missing (non-build phase)', () => {
    delete (process.env as any).NEXTAUTH_SECRET
    delete (process.env as any).NEXT_PHASE // Ensure we're not in build phase
    delete (process.env as any).NODE_ENV

    expect(() => getEnv('NEXTAUTH_SECRET')).toThrow(/NEXTAUTH_SECRET is required/)
  })

  it('should return empty string during build phase if variable missing', () => {
    delete process.env.NEXTAUTH_SECRET
    process.env.NEXT_PHASE = 'phase-production-build'

    const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})

    expect(getEnv('NEXTAUTH_SECRET')).toBe('')
    expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('NEXTAUTH_SECRET not set during build'))

    consoleSpy.mockRestore()
  })

  it('should return empty string in production build if variable missing', () => {
    delete (process.env as any).DATABASE_URL;
    (process.env as any).NODE_ENV = 'production'

    const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})

    expect(getEnv('DATABASE_URL')).toBe('')

    consoleSpy.mockRestore()
  })
})

describe('getOptionalEnv', () => {
  const originalEnv = { ...process.env }

  beforeEach(() => {
    process.env = { ...originalEnv }
  })

  afterEach(() => {
    process.env = originalEnv
  })

  it('should return environment variable value if set', () => {
    (process.env as any).NODE_ENV = 'production'
    expect(getOptionalEnv('NODE_ENV', 'development')).toBe('production')
  })

  it('should return default value if environment variable not set', () => {
    delete (process.env as any).NODE_ENV
    expect(getOptionalEnv('NODE_ENV', 'development')).toBe('development')
  })

  it('should return environment variable even if it matches default', () => {
    (process.env as any).NODE_ENV = 'development'
    expect(getOptionalEnv('NODE_ENV', 'development')).toBe('development')
  })

  it('should return default for NEXT_PUBLIC_API_URL if not set', () => {
    delete process.env.NEXT_PUBLIC_API_URL
    expect(getOptionalEnv('NEXT_PUBLIC_API_URL', 'http://localhost:8000/v1')).toBe('http://localhost:8000/v1')
  })

  it('should return actual value for NEXT_PUBLIC_API_URL if set', () => {
    process.env.NEXT_PUBLIC_API_URL = 'https://api.qteria.app/v1'
    expect(getOptionalEnv('NEXT_PUBLIC_API_URL', 'http://localhost:8000/v1')).toBe('https://api.qteria.app/v1')
  })

  it('should handle empty string as falsy and return default', () => {
    (process.env as any).NODE_ENV = ''
    expect(getOptionalEnv('NODE_ENV', 'development')).toBe('development')
  })
})

describe('isMicrosoftOAuthConfigured', () => {
  const originalEnv = { ...process.env }

  beforeEach(() => {
    process.env = { ...originalEnv }
  })

  afterEach(() => {
    process.env = originalEnv
  })

  it('should return true when both Microsoft OAuth credentials are set', () => {
    process.env.MICROSOFT_CLIENT_ID = 'test-client-id'
    process.env.MICROSOFT_CLIENT_SECRET = 'test-client-secret'

    expect(isMicrosoftOAuthConfigured()).toBe(true)
  })

  it('should return false when only MICROSOFT_CLIENT_ID is set', () => {
    process.env.MICROSOFT_CLIENT_ID = 'test-client-id'
    delete process.env.MICROSOFT_CLIENT_SECRET

    expect(isMicrosoftOAuthConfigured()).toBe(false)
  })

  it('should return false when only MICROSOFT_CLIENT_SECRET is set', () => {
    delete process.env.MICROSOFT_CLIENT_ID
    process.env.MICROSOFT_CLIENT_SECRET = 'test-client-secret'

    expect(isMicrosoftOAuthConfigured()).toBe(false)
  })

  it('should return false when neither credential is set', () => {
    delete process.env.MICROSOFT_CLIENT_ID
    delete process.env.MICROSOFT_CLIENT_SECRET

    expect(isMicrosoftOAuthConfigured()).toBe(false)
  })

  it('should return false when MICROSOFT_CLIENT_ID is empty string', () => {
    process.env.MICROSOFT_CLIENT_ID = ''
    process.env.MICROSOFT_CLIENT_SECRET = 'test-client-secret'

    expect(isMicrosoftOAuthConfigured()).toBe(false)
  })

  it('should return false when MICROSOFT_CLIENT_SECRET is empty string', () => {
    process.env.MICROSOFT_CLIENT_ID = 'test-client-id'
    process.env.MICROSOFT_CLIENT_SECRET = ''

    expect(isMicrosoftOAuthConfigured()).toBe(false)
  })

  it('should return false when MICROSOFT_CLIENT_ID is whitespace only', () => {
    process.env.MICROSOFT_CLIENT_ID = '   '
    process.env.MICROSOFT_CLIENT_SECRET = 'test-client-secret'

    expect(isMicrosoftOAuthConfigured()).toBe(false)
  })

  it('should return false when MICROSOFT_CLIENT_SECRET is whitespace only', () => {
    process.env.MICROSOFT_CLIENT_ID = 'test-client-id'
    process.env.MICROSOFT_CLIENT_SECRET = '   '

    expect(isMicrosoftOAuthConfigured()).toBe(false)
  })

  it('should return false when both are empty strings', () => {
    process.env.MICROSOFT_CLIENT_ID = ''
    process.env.MICROSOFT_CLIENT_SECRET = ''

    expect(isMicrosoftOAuthConfigured()).toBe(false)
  })
})

describe('isGoogleOAuthConfigured', () => {
  const originalEnv = { ...process.env }

  beforeEach(() => {
    process.env = { ...originalEnv }
  })

  afterEach(() => {
    process.env = originalEnv
  })

  it('should return true when both Google OAuth credentials are set', () => {
    process.env.GOOGLE_CLIENT_ID = 'test-client-id.apps.googleusercontent.com'
    process.env.GOOGLE_CLIENT_SECRET = 'test-client-secret'

    expect(isGoogleOAuthConfigured()).toBe(true)
  })

  it('should return false when only GOOGLE_CLIENT_ID is set', () => {
    process.env.GOOGLE_CLIENT_ID = 'test-client-id'
    delete process.env.GOOGLE_CLIENT_SECRET

    expect(isGoogleOAuthConfigured()).toBe(false)
  })

  it('should return false when only GOOGLE_CLIENT_SECRET is set', () => {
    delete process.env.GOOGLE_CLIENT_ID
    process.env.GOOGLE_CLIENT_SECRET = 'test-client-secret'

    expect(isGoogleOAuthConfigured()).toBe(false)
  })

  it('should return false when neither credential is set', () => {
    delete process.env.GOOGLE_CLIENT_ID
    delete process.env.GOOGLE_CLIENT_SECRET

    expect(isGoogleOAuthConfigured()).toBe(false)
  })

  it('should return false when GOOGLE_CLIENT_ID is empty string', () => {
    process.env.GOOGLE_CLIENT_ID = ''
    process.env.GOOGLE_CLIENT_SECRET = 'test-client-secret'

    expect(isGoogleOAuthConfigured()).toBe(false)
  })

  it('should return false when GOOGLE_CLIENT_SECRET is empty string', () => {
    process.env.GOOGLE_CLIENT_ID = 'test-client-id'
    process.env.GOOGLE_CLIENT_SECRET = ''

    expect(isGoogleOAuthConfigured()).toBe(false)
  })

  it('should return false when GOOGLE_CLIENT_ID is whitespace only', () => {
    process.env.GOOGLE_CLIENT_ID = '   '
    process.env.GOOGLE_CLIENT_SECRET = 'test-client-secret'

    expect(isGoogleOAuthConfigured()).toBe(false)
  })

  it('should return false when GOOGLE_CLIENT_SECRET is whitespace only', () => {
    process.env.GOOGLE_CLIENT_ID = 'test-client-id'
    process.env.GOOGLE_CLIENT_SECRET = '   '

    expect(isGoogleOAuthConfigured()).toBe(false)
  })

  it('should return false when both are empty strings', () => {
    process.env.GOOGLE_CLIENT_ID = ''
    process.env.GOOGLE_CLIENT_SECRET = ''

    expect(isGoogleOAuthConfigured()).toBe(false)
  })
})

describe('Integration: OAuth provider configuration', () => {
  const originalEnv = { ...process.env }

  beforeEach(() => {
    process.env = { ...originalEnv }
  })

  afterEach(() => {
    process.env = originalEnv
  })

  it('should enable both OAuth providers when all credentials are set', () => {
    process.env.MICROSOFT_CLIENT_ID = 'microsoft-client-id'
    process.env.MICROSOFT_CLIENT_SECRET = 'microsoft-client-secret'
    process.env.GOOGLE_CLIENT_ID = 'google-client-id'
    process.env.GOOGLE_CLIENT_SECRET = 'google-client-secret'

    expect(isMicrosoftOAuthConfigured()).toBe(true)
    expect(isGoogleOAuthConfigured()).toBe(true)
  })

  it('should enable only Microsoft OAuth when Google credentials missing', () => {
    process.env.MICROSOFT_CLIENT_ID = 'microsoft-client-id'
    process.env.MICROSOFT_CLIENT_SECRET = 'microsoft-client-secret'
    delete process.env.GOOGLE_CLIENT_ID
    delete process.env.GOOGLE_CLIENT_SECRET

    expect(isMicrosoftOAuthConfigured()).toBe(true)
    expect(isGoogleOAuthConfigured()).toBe(false)
  })

  it('should enable only Google OAuth when Microsoft credentials missing', () => {
    delete process.env.MICROSOFT_CLIENT_ID
    delete process.env.MICROSOFT_CLIENT_SECRET
    process.env.GOOGLE_CLIENT_ID = 'google-client-id'
    process.env.GOOGLE_CLIENT_SECRET = 'google-client-secret'

    expect(isMicrosoftOAuthConfigured()).toBe(false)
    expect(isGoogleOAuthConfigured()).toBe(true)
  })

  it('should disable both OAuth providers when no credentials are set', () => {
    delete process.env.MICROSOFT_CLIENT_ID
    delete process.env.MICROSOFT_CLIENT_SECRET
    delete process.env.GOOGLE_CLIENT_ID
    delete process.env.GOOGLE_CLIENT_SECRET

    expect(isMicrosoftOAuthConfigured()).toBe(false)
    expect(isGoogleOAuthConfigured()).toBe(false)
  })
})
