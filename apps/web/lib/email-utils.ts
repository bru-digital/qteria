/**
 * Email normalization utilities for consistent email handling across authentication flows.
 *
 * Ensures emails are consistently formatted when:
 * - Users log in with email/password
 * - Users log in with OAuth
 * - Users are created or updated
 * - Email lookups are performed
 */

/**
 * Normalize an email address to ensure consistent formatting.
 *
 * Normalization rules:
 * 1. Trim whitespace
 * 2. Convert to lowercase
 * 3. Handle null/undefined gracefully
 *
 * @param email - Email address to normalize (can be null/undefined)
 * @returns Normalized email address, or null if input was null/undefined
 *
 * @example
 * normalizeEmail("  User@Example.COM  ") // => "user@example.com"
 * normalizeEmail("test@domain.com") // => "test@domain.com"
 * normalizeEmail(null) // => null
 */
export function normalizeEmail(email: string | null | undefined): string | null {
  if (!email) {
    return null
  }

  return email.trim().toLowerCase()
}

/**
 * Validate email format (basic check).
 * For comprehensive validation, use a library like validator.js or zod.
 *
 * @param email - Email address to validate
 * @returns True if email has a valid format
 *
 * @example
 * isValidEmail("user@example.com") // => true
 * isValidEmail("invalid") // => false
 * isValidEmail("") // => false
 */
export function isValidEmail(email: string | null | undefined): boolean {
  if (!email) {
    return false
  }

  // Basic email regex - not comprehensive but catches obvious invalid formats
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * Normalize and validate email in one step.
 * Returns normalized email if valid, null otherwise.
 *
 * @param email - Email address to normalize and validate
 * @returns Normalized email if valid, null otherwise
 *
 * @example
 * normalizeAndValidateEmail("  User@Example.COM  ") // => "user@example.com"
 * normalizeAndValidateEmail("invalid") // => null
 */
export function normalizeAndValidateEmail(email: string | null | undefined): string | null {
  const normalized = normalizeEmail(email)

  if (!normalized || !isValidEmail(normalized)) {
    return null
  }

  return normalized
}
