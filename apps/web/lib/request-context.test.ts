import { describe, it, expect, beforeEach } from 'vitest'
import { requestContext, getIpAddress, getUserAgent, getRequestContext } from './request-context'

describe('getIpAddress', () => {
  it('should extract IP from x-forwarded-for header', () => {
    const headers = new Headers({
      'x-forwarded-for': '203.0.113.195'
    })
    expect(getIpAddress(headers)).toBe('203.0.113.195')
  })

  it('should extract first IP from x-forwarded-for with multiple IPs', () => {
    const headers = new Headers({
      'x-forwarded-for': '203.0.113.195, 70.41.3.18, 150.172.238.178'
    })
    expect(getIpAddress(headers)).toBe('203.0.113.195')
  })

  it('should trim whitespace from x-forwarded-for', () => {
    const headers = new Headers({
      'x-forwarded-for': '  203.0.113.195  , 70.41.3.18'
    })
    expect(getIpAddress(headers)).toBe('203.0.113.195')
  })

  it('should fallback to x-real-ip if x-forwarded-for is not present', () => {
    const headers = new Headers({
      'x-real-ip': '203.0.113.195'
    })
    expect(getIpAddress(headers)).toBe('203.0.113.195')
  })

  it('should prefer x-forwarded-for over x-real-ip', () => {
    const headers = new Headers({
      'x-forwarded-for': '203.0.113.195',
      'x-real-ip': '70.41.3.18'
    })
    expect(getIpAddress(headers)).toBe('203.0.113.195')
  })

  it('should return null if no IP headers present', () => {
    const headers = new Headers({
      'user-agent': 'Mozilla/5.0'
    })
    expect(getIpAddress(headers)).toBe(null)
  })

  it('should return null for empty headers', () => {
    const headers = new Headers()
    expect(getIpAddress(headers)).toBe(null)
  })

  it('should handle IPv6 addresses in x-forwarded-for', () => {
    const headers = new Headers({
      'x-forwarded-for': '2001:0db8:85a3:0000:0000:8a2e:0370:7334'
    })
    expect(getIpAddress(headers)).toBe('2001:0db8:85a3:0000:0000:8a2e:0370:7334')
  })

  it('should handle IPv6 addresses with multiple IPs', () => {
    const headers = new Headers({
      'x-forwarded-for': '2001:0db8:85a3::8a2e:0370:7334, 203.0.113.195'
    })
    expect(getIpAddress(headers)).toBe('2001:0db8:85a3::8a2e:0370:7334')
  })

  it('should handle localhost IPv4', () => {
    const headers = new Headers({
      'x-forwarded-for': '127.0.0.1'
    })
    expect(getIpAddress(headers)).toBe('127.0.0.1')
  })

  it('should handle localhost IPv6', () => {
    const headers = new Headers({
      'x-forwarded-for': '::1'
    })
    expect(getIpAddress(headers)).toBe('::1')
  })

  // Vercel-specific scenarios
  it('should handle Vercel x-forwarded-for format', () => {
    const headers = new Headers({
      'x-forwarded-for': '203.0.113.195',
      'x-real-ip': '203.0.113.195'
    })
    expect(getIpAddress(headers)).toBe('203.0.113.195')
  })

  // Railway-specific scenarios
  it('should handle Railway x-real-ip format', () => {
    const headers = new Headers({
      'x-real-ip': '203.0.113.195'
    })
    expect(getIpAddress(headers)).toBe('203.0.113.195')
  })

  // Security: Ensure we take the FIRST IP (client IP, not proxy IPs)
  it('should use first IP to prevent IP spoofing via proxy chain', () => {
    const headers = new Headers({
      'x-forwarded-for': '203.0.113.195, 70.41.3.18, 150.172.238.178'
    })
    // First IP is the actual client, remaining are proxy IPs
    expect(getIpAddress(headers)).toBe('203.0.113.195')
  })
})

describe('getUserAgent', () => {
  it('should extract user agent from header', () => {
    const headers = new Headers({
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    expect(getUserAgent(headers)).toBe('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
  })

  it('should return null if user-agent header not present', () => {
    const headers = new Headers({
      'x-forwarded-for': '203.0.113.195'
    })
    expect(getUserAgent(headers)).toBe(null)
  })

  it('should return null for empty headers', () => {
    const headers = new Headers()
    expect(getUserAgent(headers)).toBe(null)
  })

  it('should handle Chrome user agent', () => {
    const chromeUA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    const headers = new Headers({
      'user-agent': chromeUA
    })
    expect(getUserAgent(headers)).toBe(chromeUA)
  })

  it('should handle Firefox user agent', () => {
    const firefoxUA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
    const headers = new Headers({
      'user-agent': firefoxUA
    })
    expect(getUserAgent(headers)).toBe(firefoxUA)
  })

  it('should handle Safari user agent', () => {
    const safariUA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
    const headers = new Headers({
      'user-agent': safariUA
    })
    expect(getUserAgent(headers)).toBe(safariUA)
  })

  it('should handle mobile user agents', () => {
    const mobileUA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1'
    const headers = new Headers({
      'user-agent': mobileUA
    })
    expect(getUserAgent(headers)).toBe(mobileUA)
  })

  it('should handle bot user agents', () => {
    const botUA = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
    const headers = new Headers({
      'user-agent': botUA
    })
    expect(getUserAgent(headers)).toBe(botUA)
  })

  it('should handle empty user agent string', () => {
    const headers = new Headers({
      'user-agent': ''
    })
    expect(getUserAgent(headers)).toBe('')
  })
})

describe('getRequestContext', () => {
  beforeEach(() => {
    // Clear any existing context before each test
    // AsyncLocalStorage doesn't have a built-in clear, so we just ensure
    // we're testing outside of any requestContext.run() scope
  })

  it('should return null values when called outside AsyncLocalStorage scope', () => {
    const context = getRequestContext()
    expect(context).toEqual({
      ipAddress: null,
      userAgent: null
    })
  })

  it('should return stored context when called inside AsyncLocalStorage scope', () => {
    const expectedContext = {
      ipAddress: '203.0.113.195',
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    requestContext.run(expectedContext, () => {
      const context = getRequestContext()
      expect(context).toEqual(expectedContext)
    })
  })

  it('should return null IP and user agent inside scope with null values', () => {
    const expectedContext = {
      ipAddress: null,
      userAgent: null
    }

    requestContext.run(expectedContext, () => {
      const context = getRequestContext()
      expect(context).toEqual(expectedContext)
    })
  })

  it('should handle partial context (IP only)', () => {
    const expectedContext = {
      ipAddress: '203.0.113.195',
      userAgent: null
    }

    requestContext.run(expectedContext, () => {
      const context = getRequestContext()
      expect(context).toEqual(expectedContext)
    })
  })

  it('should handle partial context (user agent only)', () => {
    const expectedContext = {
      ipAddress: null,
      userAgent: 'Mozilla/5.0'
    }

    requestContext.run(expectedContext, () => {
      const context = getRequestContext()
      expect(context).toEqual(expectedContext)
    })
  })

  it('should maintain context through async operations', async () => {
    const expectedContext = {
      ipAddress: '203.0.113.195',
      userAgent: 'Mozilla/5.0'
    }

    await requestContext.run(expectedContext, async () => {
      // Simulate async operation
      await new Promise(resolve => setTimeout(resolve, 10))

      const context = getRequestContext()
      expect(context).toEqual(expectedContext)
    })
  })

  it('should maintain separate contexts for concurrent requests', async () => {
    const context1 = {
      ipAddress: '203.0.113.195',
      userAgent: 'Mozilla/5.0 Chrome'
    }

    const context2 = {
      ipAddress: '70.41.3.18',
      userAgent: 'Mozilla/5.0 Firefox'
    }

    // Simulate two concurrent requests
    const promise1 = requestContext.run(context1, async () => {
      await new Promise(resolve => setTimeout(resolve, 20))
      return getRequestContext()
    })

    const promise2 = requestContext.run(context2, async () => {
      await new Promise(resolve => setTimeout(resolve, 10))
      return getRequestContext()
    })

    const [result1, result2] = await Promise.all([promise1, promise2])

    expect(result1).toEqual(context1)
    expect(result2).toEqual(context2)
  })

  it('should handle nested AsyncLocalStorage contexts correctly', () => {
    const outerContext = {
      ipAddress: '203.0.113.195',
      userAgent: 'Mozilla/5.0 Outer'
    }

    const innerContext = {
      ipAddress: '70.41.3.18',
      userAgent: 'Mozilla/5.0 Inner'
    }

    requestContext.run(outerContext, () => {
      const outer = getRequestContext()
      expect(outer).toEqual(outerContext)

      requestContext.run(innerContext, () => {
        const inner = getRequestContext()
        expect(inner).toEqual(innerContext)
      })

      // Should be back to outer context
      const outerAgain = getRequestContext()
      expect(outerAgain).toEqual(outerContext)
    })
  })

  // SOC2/ISO 27001 compliance test
  it('should preserve audit log metadata through authentication flow', async () => {
    const auditContext = {
      ipAddress: '203.0.113.195',
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    await requestContext.run(auditContext, async () => {
      // Simulate OAuth callback with multiple async operations
      await new Promise(resolve => setTimeout(resolve, 5))
      const context1 = getRequestContext()

      await new Promise(resolve => setTimeout(resolve, 5))
      const context2 = getRequestContext()

      // Context should be preserved throughout
      expect(context1).toEqual(auditContext)
      expect(context2).toEqual(auditContext)
    })
  })
})

describe('Integration: Full request flow', () => {
  it('should extract IP and user agent from headers and provide via context', () => {
    const headers = new Headers({
      'x-forwarded-for': '203.0.113.195',
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    const context = {
      ipAddress: getIpAddress(headers),
      userAgent: getUserAgent(headers)
    }

    requestContext.run(context, () => {
      const retrieved = getRequestContext()
      expect(retrieved.ipAddress).toBe('203.0.113.195')
      expect(retrieved.userAgent).toBe('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    })
  })

  it('should handle missing headers gracefully', () => {
    const headers = new Headers()

    const context = {
      ipAddress: getIpAddress(headers),
      userAgent: getUserAgent(headers)
    }

    requestContext.run(context, () => {
      const retrieved = getRequestContext()
      expect(retrieved.ipAddress).toBe(null)
      expect(retrieved.userAgent).toBe(null)
    })
  })
})
