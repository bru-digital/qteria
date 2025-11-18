/**
 * Environment variable validation.
 *
 * Validates that all required environment variables are present at startup.
 * Throws helpful error messages if variables are missing or invalid.
 */

/**
 * Required environment variables for the application
 */
const REQUIRED_ENV_VARS = {
  // Auth.js configuration
  NEXTAUTH_SECRET: "Used for JWT signing. Generate with: openssl rand -base64 32",
  NEXTAUTH_URL: "Base URL for Auth.js callbacks (e.g., http://localhost:3000 or https://yourdomain.com)",

  // Database
  DATABASE_URL: "PostgreSQL connection string (e.g., postgresql://user:password@localhost:5432/dbname)",
} as const

/**
 * Optional environment variables with defaults
 */
const OPTIONAL_ENV_VARS = {
  NODE_ENV: "development",
  NEXT_PUBLIC_API_URL: "http://localhost:8000/v1",
} as const

/**
 * Validate environment variables at startup.
 * Throws an error with helpful messages if any required variables are missing.
 */
export function validateEnv(): void {
  const missingVars: string[] = []
  const errorMessages: string[] = []

  // Check required variables
  for (const [key, description] of Object.entries(REQUIRED_ENV_VARS)) {
    const value = process.env[key]

    if (!value || value.trim() === "") {
      missingVars.push(key)
      errorMessages.push(`  ❌ ${key}\n     ${description}`)
    }
  }

  // Additional validation for specific variables
  if (process.env.NEXTAUTH_SECRET) {
    const secret = process.env.NEXTAUTH_SECRET
    if (secret.length < 32) {
      errorMessages.push(
        `  ⚠️  NEXTAUTH_SECRET is too short (${secret.length} characters)\n     Recommended: At least 32 characters for security\n     Generate one with: openssl rand -base64 32`
      )
    }
  }

  if (process.env.DATABASE_URL) {
    const dbUrl = process.env.DATABASE_URL
    if (!dbUrl.startsWith("postgresql://") && !dbUrl.startsWith("postgres://")) {
      errorMessages.push(
        `  ⚠️  DATABASE_URL doesn't look like a PostgreSQL connection string\n     Expected format: postgresql://user:password@host:port/database`
      )
    }
  }

  // If there are any errors, throw with helpful message
  if (missingVars.length > 0 || errorMessages.length > 0) {
    const message = [
      "",
      "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
      "❌ Environment Variable Validation Failed",
      "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
      "",
    ]

    if (missingVars.length > 0) {
      message.push("Missing required environment variables:")
      message.push("")
      message.push(...errorMessages.filter(msg => msg.includes("❌")))
      message.push("")
    }

    const warnings = errorMessages.filter(msg => msg.includes("⚠️"))
    if (warnings.length > 0) {
      message.push("Environment variable warnings:")
      message.push("")
      message.push(...warnings)
      message.push("")
    }

    message.push("To fix this:")
    message.push("  1. Copy .env.template to .env")
    message.push("     cp .env.template .env")
    message.push("")
    message.push("  2. Edit .env and fill in the required values")
    message.push("")
    message.push("  3. Restart the application")
    message.push("")
    message.push("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    message.push("")

    throw new Error(message.join("\n"))
  }
}

/**
 * Get environment variable with type safety.
 * Returns the value or throws if missing (for required vars).
 *
 * During build phase (NEXT_PHASE === 'phase-production-build'), returns empty string
 * to allow the build to complete. Environment variables are validated at runtime.
 *
 * @param key - Environment variable name
 * @returns Environment variable value
 */
export function getEnv(key: keyof typeof REQUIRED_ENV_VARS): string {
  const value = process.env[key]

  // During Next.js build phase, allow missing env vars
  // They will be validated at runtime when the app starts
  if (!value) {
    const isBuilding = process.env.NEXT_PHASE === 'phase-production-build' ||
                       process.env.NODE_ENV === 'production' && !process.env[key]

    if (isBuilding) {
      console.warn(`[ENV] ${key} not set during build - will be required at runtime`)
      return '' // Return empty string during build, will fail at runtime if actually missing
    }

    throw new Error(
      `Environment variable ${key} is required but not set. Run validateEnv() at startup to get detailed error messages.`
    )
  }
  return value
}

/**
 * Get optional environment variable with default value.
 *
 * @param key - Environment variable name
 * @param defaultValue - Default value if not set
 * @returns Environment variable value or default
 */
export function getOptionalEnv(
  key: keyof typeof OPTIONAL_ENV_VARS,
  defaultValue: string
): string {
  return process.env[key] || defaultValue
}

// Export type for environment variables
export type RequiredEnvVar = keyof typeof REQUIRED_ENV_VARS
export type OptionalEnvVar = keyof typeof OPTIONAL_ENV_VARS
