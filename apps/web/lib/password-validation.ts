/**
 * Password validation utility.
 *
 * Enforces password strength requirements:
 * - Minimum 12 characters
 * - Mix of uppercase, lowercase, numbers, and special characters
 * - Not in common passwords list
 *
 * @note Currently unused - will be integrated in user registration flow (Story 006)
 * and password reset functionality. Created now to establish security requirements.
 */

/**
 * Common weak passwords to reject
 * This is a minimal list - in production, use a comprehensive list like:
 * https://github.com/danielmiessler/SecLists/tree/master/Passwords/Common-Credentials
 */
const COMMON_PASSWORDS = new Set([
  "password",
  "password123",
  "123456",
  "12345678",
  "123456789",
  "1234567890",
  "qwerty",
  "abc123",
  "monkey",
  "letmein",
  "trustno1",
  "dragon",
  "baseball",
  "iloveyou",
  "master",
  "sunshine",
  "ashley",
  "bailey",
  "passw0rd",
  "shadow",
  "123123",
  "654321",
  "superman",
  "qazwsx",
  "michael",
  "football",
  "welcome",
  "admin",
  "login",
  "starwars",
])

/**
 * Password validation result
 */
export interface PasswordValidationResult {
  valid: boolean
  errors: string[]
  strength: "weak" | "fair" | "good" | "strong"
}

/**
 * Validate password strength.
 *
 * @param password - Password to validate
 * @returns Validation result with errors and strength rating
 *
 * @example
 * ```typescript
 * const result = validatePassword("MySecureP@ssw0rd123")
 * if (!result.valid) {
 *   console.log("Validation failed:", result.errors)
 * }
 * ```
 */
export function validatePassword(password: string): PasswordValidationResult {
  const errors: string[] = []

  // Check minimum length
  if (password.length < 12) {
    errors.push("Password must be at least 12 characters long")
  }

  // Check for uppercase letters
  if (!/[A-Z]/.test(password)) {
    errors.push("Password must contain at least one uppercase letter")
  }

  // Check for lowercase letters
  if (!/[a-z]/.test(password)) {
    errors.push("Password must contain at least one lowercase letter")
  }

  // Check for numbers
  if (!/[0-9]/.test(password)) {
    errors.push("Password must contain at least one number")
  }

  // Check for special characters
  if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
    errors.push("Password must contain at least one special character (!@#$%^&* etc.)")
  }

  // Check against common passwords (case-insensitive)
  if (COMMON_PASSWORDS.has(password.toLowerCase())) {
    errors.push("This password is too common. Please choose a more unique password")
  }

  // Check for sequential characters (e.g., "12345", "abcdef")
  if (/(?:abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)/i.test(password)) {
    errors.push("Password should not contain sequential characters")
  }

  if (/(?:012|123|234|345|456|567|678|789|890)/.test(password)) {
    errors.push("Password should not contain sequential numbers")
  }

  // Check for repeated characters (e.g., "aaaa", "1111")
  if (/(.)\1{3,}/.test(password)) {
    errors.push("Password should not contain repeated characters (e.g., 'aaaa')")
  }

  // Calculate password strength
  const strength = calculatePasswordStrength(password)

  return {
    valid: errors.length === 0,
    errors,
    strength,
  }
}

/**
 * Calculate password strength based on various criteria.
 *
 * @param password - Password to evaluate
 * @returns Strength rating
 */
function calculatePasswordStrength(
  password: string
): "weak" | "fair" | "good" | "strong" {
  let score = 0

  // Length scoring
  if (password.length >= 12) score += 1
  if (password.length >= 16) score += 1
  if (password.length >= 20) score += 1

  // Character variety scoring
  if (/[a-z]/.test(password)) score += 1
  if (/[A-Z]/.test(password)) score += 1
  if (/[0-9]/.test(password)) score += 1
  if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) score += 1

  // Bonus for entropy (mix of different character types)
  const uniqueChars = new Set(password.split("")).size
  if (uniqueChars >= 10) score += 1
  if (uniqueChars >= 15) score += 1

  // Penalty for common patterns
  if (COMMON_PASSWORDS.has(password.toLowerCase())) score -= 3
  if (/(.)\1{3,}/.test(password)) score -= 1

  // Map score to strength
  if (score >= 7) return "strong"
  if (score >= 5) return "good"
  if (score >= 3) return "fair"
  return "weak"
}

/**
 * Get user-friendly strength description.
 *
 * @param strength - Password strength rating
 * @returns Human-readable description
 */
export function getStrengthDescription(
  strength: "weak" | "fair" | "good" | "strong"
): string {
  const descriptions = {
    weak: "This password is weak. Please add more characters and variety.",
    fair: "This password is fair, but could be stronger. Consider adding more special characters.",
    good: "This is a good password. It meets security requirements.",
    strong: "This is a strong password. Excellent choice!",
  }

  return descriptions[strength]
}

/**
 * Get password strength color for UI display.
 *
 * @param strength - Password strength rating
 * @returns Color name (for Tailwind CSS classes or similar)
 */
export function getStrengthColor(
  strength: "weak" | "fair" | "good" | "strong"
): "red" | "yellow" | "blue" | "green" {
  const colors = {
    weak: "red" as const,
    fair: "yellow" as const,
    good: "blue" as const,
    strong: "green" as const,
  }

  return colors[strength]
}
