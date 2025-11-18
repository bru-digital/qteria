/**
 * Rate limiting utility using Redis.
 *
 * Implements brute-force protection for authentication:
 * - Max 5 failed login attempts per email per 15 minutes
 * - Max 20 total login attempts per IP per hour
 */

import Redis from "ioredis"

/**
 * Redis client singleton
 */
let redis: Redis | null = null

function getRedisClient(): Redis {
  if (!redis) {
    const redisUrl = process.env.REDIS_URL || "redis://localhost:6379/0"

    redis = new Redis(redisUrl, {
      maxRetriesPerRequest: 3,
      retryStrategy(times) {
        const delay = Math.min(times * 50, 2000)
        return delay
      },
      lazyConnect: true, // Don't connect immediately
    })

    redis.on("error", (err) => {
      console.error("[REDIS] Connection error:", err)
    })

    redis.on("connect", () => {
      console.log("[REDIS] Connected successfully")
    })

    // Attempt to connect
    redis.connect().catch((err) => {
      console.error("[REDIS] Failed to connect:", err)
      console.warn("[REDIS] Rate limiting will be disabled")
    })
  }

  return redis
}

/**
 * Rate limit configuration
 */
export const RateLimitConfig = {
  // Failed login attempts per email
  FAILED_LOGIN_MAX_ATTEMPTS: 5,
  FAILED_LOGIN_WINDOW_SECONDS: 15 * 60, // 15 minutes

  // Total login attempts per IP
  TOTAL_LOGIN_MAX_ATTEMPTS: 20,
  TOTAL_LOGIN_WINDOW_SECONDS: 60 * 60, // 1 hour
} as const

/**
 * Result of a rate limit check
 */
export interface RateLimitResult {
  allowed: boolean
  remainingAttempts: number
  resetInSeconds: number
}

/**
 * Check if failed login attempts for an email are within rate limit.
 *
 * @param email - User email address
 * @returns Rate limit result
 */
export async function checkFailedLoginRateLimit(
  email: string
): Promise<RateLimitResult> {
  const client = getRedisClient()

  // If Redis is not connected, allow the request (fail open for availability)
  if (client.status !== "ready") {
    console.warn("[RATE_LIMIT] Redis not ready, allowing request")
    return {
      allowed: true,
      remainingAttempts: RateLimitConfig.FAILED_LOGIN_MAX_ATTEMPTS,
      resetInSeconds: 0,
    }
  }

  const key = `rate_limit:failed_login:${email.toLowerCase()}`

  try {
    // Get current count
    const currentCount = await client.get(key)
    const count = currentCount ? parseInt(currentCount, 10) : 0

    if (count >= RateLimitConfig.FAILED_LOGIN_MAX_ATTEMPTS) {
      // Rate limit exceeded
      const ttl = await client.ttl(key)
      return {
        allowed: false,
        remainingAttempts: 0,
        resetInSeconds: ttl > 0 ? ttl : RateLimitConfig.FAILED_LOGIN_WINDOW_SECONDS,
      }
    }

    // Rate limit not exceeded
    return {
      allowed: true,
      remainingAttempts: RateLimitConfig.FAILED_LOGIN_MAX_ATTEMPTS - count,
      resetInSeconds: RateLimitConfig.FAILED_LOGIN_WINDOW_SECONDS,
    }
  } catch (error) {
    console.error("[RATE_LIMIT] Error checking failed login rate limit:", error)
    // On error, fail open (allow the request)
    return {
      allowed: true,
      remainingAttempts: RateLimitConfig.FAILED_LOGIN_MAX_ATTEMPTS,
      resetInSeconds: 0,
    }
  }
}

/**
 * Record a failed login attempt for an email.
 *
 * @param email - User email address
 */
export async function recordFailedLoginAttempt(email: string): Promise<void> {
  const client = getRedisClient()

  if (client.status !== "ready") {
    console.warn("[RATE_LIMIT] Redis not ready, skipping failed login recording")
    return
  }

  const key = `rate_limit:failed_login:${email.toLowerCase()}`

  try {
    const count = await client.incr(key)

    // Set expiry only on first attempt
    if (count === 1) {
      await client.expire(key, RateLimitConfig.FAILED_LOGIN_WINDOW_SECONDS)
    }
  } catch (error) {
    console.error("[RATE_LIMIT] Error recording failed login attempt:", error)
  }
}

/**
 * Reset failed login attempts for an email (called on successful login).
 *
 * @param email - User email address
 */
export async function resetFailedLoginAttempts(email: string): Promise<void> {
  const client = getRedisClient()

  if (client.status !== "ready") {
    return
  }

  const key = `rate_limit:failed_login:${email.toLowerCase()}`

  try {
    await client.del(key)
  } catch (error) {
    console.error("[RATE_LIMIT] Error resetting failed login attempts:", error)
  }
}

/**
 * Check if total login attempts for an IP are within rate limit.
 *
 * @param ipAddress - Client IP address
 * @returns Rate limit result
 */
export async function checkTotalLoginRateLimit(
  ipAddress: string
): Promise<RateLimitResult> {
  const client = getRedisClient()

  // If Redis is not connected, allow the request (fail open)
  if (client.status !== "ready") {
    console.warn("[RATE_LIMIT] Redis not ready, allowing request")
    return {
      allowed: true,
      remainingAttempts: RateLimitConfig.TOTAL_LOGIN_MAX_ATTEMPTS,
      resetInSeconds: 0,
    }
  }

  const key = `rate_limit:total_login:${ipAddress}`

  try {
    // Get current count
    const currentCount = await client.get(key)
    const count = currentCount ? parseInt(currentCount, 10) : 0

    if (count >= RateLimitConfig.TOTAL_LOGIN_MAX_ATTEMPTS) {
      // Rate limit exceeded
      const ttl = await client.ttl(key)
      return {
        allowed: false,
        remainingAttempts: 0,
        resetInSeconds: ttl > 0 ? ttl : RateLimitConfig.TOTAL_LOGIN_WINDOW_SECONDS,
      }
    }

    // Rate limit not exceeded
    return {
      allowed: true,
      remainingAttempts: RateLimitConfig.TOTAL_LOGIN_MAX_ATTEMPTS - count,
      resetInSeconds: RateLimitConfig.TOTAL_LOGIN_WINDOW_SECONDS,
    }
  } catch (error) {
    console.error("[RATE_LIMIT] Error checking total login rate limit:", error)
    // On error, fail open (allow the request)
    return {
      allowed: true,
      remainingAttempts: RateLimitConfig.TOTAL_LOGIN_MAX_ATTEMPTS,
      resetInSeconds: 0,
    }
  }
}

/**
 * Record a login attempt for an IP address.
 *
 * @param ipAddress - Client IP address
 */
export async function recordLoginAttempt(ipAddress: string): Promise<void> {
  const client = getRedisClient()

  if (client.status !== "ready") {
    console.warn("[RATE_LIMIT] Redis not ready, skipping login attempt recording")
    return
  }

  const key = `rate_limit:total_login:${ipAddress}`

  try {
    const count = await client.incr(key)

    // Set expiry only on first attempt
    if (count === 1) {
      await client.expire(key, RateLimitConfig.TOTAL_LOGIN_WINDOW_SECONDS)
    }
  } catch (error) {
    console.error("[RATE_LIMIT] Error recording login attempt:", error)
  }
}

/**
 * Helper function to format remaining time in human-readable format.
 *
 * @param seconds - Seconds remaining
 * @returns Human-readable string (e.g., "5 minutes", "1 hour")
 */
export function formatRateLimitReset(seconds: number): string {
  if (seconds < 60) {
    return `${seconds} second${seconds !== 1 ? "s" : ""}`
  }

  const minutes = Math.ceil(seconds / 60)
  if (minutes < 60) {
    return `${minutes} minute${minutes !== 1 ? "s" : ""}`
  }

  const hours = Math.ceil(minutes / 60)
  return `${hours} hour${hours !== 1 ? "s" : ""}`
}
