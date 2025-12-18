'use client'

import { useState, FormEvent, Suspense, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { signIn } from 'next-auth/react'
import { loginWithAudit } from '@/app/actions/auth'

function LoginForm() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isMicrosoftLoading, setIsMicrosoftLoading] = useState(false)
  const [isGoogleLoading, setIsGoogleLoading] = useState(false)
  const router = useRouter()
  const searchParams = useSearchParams()

  // Reset loading states on mount (handles OAuth redirect failures)
  useEffect(() => {
    setIsLoading(false)
    setIsMicrosoftLoading(false)
    setIsGoogleLoading(false)
  }, [])

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      // Get callback URL from query params or default to dashboard
      const callbackUrl = searchParams.get('callbackUrl') || undefined

      // Use server action with audit logging
      const result = await loginWithAudit(
        email.trim().toLowerCase(), // Sanitize email input
        password,
        callbackUrl
      )

      if (result.success) {
        // Redirect to callback URL or dashboard
        router.push(result.redirectTo || '/dashboard')
        router.refresh()
      } else {
        setError(result.error || 'Invalid email or password')
      }
    } catch (err) {
      console.error('[LOGIN] Error during login:', err)
      const errorMessage = err instanceof Error ? err.message : 'An error occurred during login'
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const handleMicrosoftLogin = async () => {
    setIsMicrosoftLoading(true)
    setError('')
    await signIn('microsoft-entra-id', { callbackUrl: '/dashboard' })
  }

  const handleGoogleLogin = async () => {
    setIsGoogleLoading(true)
    setError('')
    await signIn('google', { callbackUrl: '/dashboard' })
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow-md">
        <div>
          <h2 className="text-center text-3xl font-bold text-gray-900">Qteria</h2>
          <p className="mt-2 text-center text-sm text-gray-600">Sign in to your account</p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="you@example.com"
                disabled={isLoading}
              />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="••••••••"
                disabled={isLoading}
              />
            </div>
          </div>

          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <div className="flex">
                <div className="text-sm text-red-800">{error}</div>
              </div>
            </div>
          )}

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Signing in...' : 'Sign in'}
            </button>
          </div>
        </form>

        {/* OAuth Divider */}
        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-gray-500">OR</span>
          </div>
        </div>

        {/* OAuth Buttons */}
        <div className="space-y-3">
          {/* Primary: Microsoft OAuth */}
          <button
            onClick={handleMicrosoftLogin}
            disabled={isLoading || isMicrosoftLoading || isGoogleLoading}
            type="button"
            aria-label="Sign in with Microsoft account"
            className="w-full flex items-center justify-center gap-3 py-2.5 px-4 border border-gray-300 rounded-md shadow-sm bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isMicrosoftLoading ? (
              <svg
                className="animate-spin h-5 w-5 text-gray-700"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
            ) : (
              <svg className="w-5 h-5" viewBox="0 0 23 23" fill="none" aria-hidden="true">
                <path d="M0 0h11v11H0z" fill="#f25022" />
                <path d="M12 0h11v11H12z" fill="#00a4ef" />
                <path d="M0 12h11v11H0z" fill="#7fba00" />
                <path d="M12 12h11v11H12z" fill="#ffb900" />
              </svg>
            )}
            <span className="text-sm font-medium text-gray-700">
              {isMicrosoftLoading ? 'Signing in...' : 'Sign in with Microsoft'}
            </span>
          </button>

          {/* Secondary: Google OAuth */}
          <button
            onClick={handleGoogleLogin}
            disabled={isLoading || isMicrosoftLoading || isGoogleLoading}
            type="button"
            aria-label="Sign in with Google account"
            className="w-full flex items-center justify-center gap-3 py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isGoogleLoading ? (
              <svg
                className="animate-spin h-5 w-5 text-gray-700"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
            ) : (
              <svg className="w-5 h-5" viewBox="0 0 24 24" aria-hidden="true">
                <path
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  fill="#4285F4"
                />
                <path
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  fill="#34A853"
                />
                <path
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  fill="#FBBC05"
                />
                <path
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  fill="#EA4335"
                />
              </svg>
            )}
            <span className="text-sm font-medium text-gray-700">
              {isGoogleLoading ? 'Signing in...' : 'Sign in with Google'}
            </span>
          </button>
        </div>

        {/* OAuth Error Display */}
        {searchParams.get('error') && (
          <div
            className={`rounded-md p-4 ${
              searchParams.get('error') === 'oauth_user_not_found' ? 'bg-yellow-50' : 'bg-red-50'
            }`}
          >
            <div
              className={`text-sm ${
                searchParams.get('error') === 'oauth_user_not_found'
                  ? 'text-yellow-800'
                  : 'text-red-800'
              }`}
            >
              {searchParams.get('error') === 'oauth_user_not_found' && (
                <>
                  No account found with this email. Please contact your administrator to get
                  invited.
                </>
              )}
              {searchParams.get('error') === 'oauth_invalid_email' && (
                <>
                  Invalid email address provided by the authentication provider. Please try again or
                  contact support.
                </>
              )}
              {searchParams.get('error') === 'oauth_no_email' && (
                <>
                  OAuth login failed: no email address provided by the authentication provider.
                  Please try again or contact support.
                </>
              )}
              {searchParams.get('error') === 'oauth_database_error' && (
                <>
                  Database connection error during login. Please try again in a few moments or
                  contact support if the issue persists.
                </>
              )}
              {searchParams.get('error') === 'oauth_error' && (
                <>
                  An error occurred during OAuth authentication. Please try again or contact support
                  if the issue persists.
                </>
              )}
              {![
                'oauth_user_not_found',
                'oauth_invalid_email',
                'oauth_no_email',
                'oauth_database_error',
                'oauth_error',
              ].includes(searchParams.get('error') || '') && (
                <>Authentication error. Please try again or contact support.</>
              )}
            </div>
          </div>
        )}

        {/* Footer Links */}
        <div className="mt-6 text-center text-sm text-gray-500 space-x-4">
          <a
            href="/terms"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-gray-700 hover:underline"
          >
            Terms of Service
          </a>
          <span className="text-gray-400">•</span>
          <a
            href="/privacy"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-gray-700 hover:underline"
          >
            Privacy Policy
          </a>
        </div>
      </div>
    </div>
  )
}

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="text-gray-600">Loading...</div>
        </div>
      }
    >
      <LoginForm />
    </Suspense>
  )
}
