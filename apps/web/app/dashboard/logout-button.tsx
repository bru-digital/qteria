'use client'

/**
 * Logout button client component.
 *
 * Separated from the server component dashboard page to allow
 * interactive logout functionality while keeping the page itself
 * as a server component for better security.
 */

import { useRouter } from 'next/navigation'
import { logoutWithAudit } from '@/app/actions/auth'
import { useState } from 'react'

interface LogoutButtonProps {
  userId: string
  organizationId: string
  email: string
}

export function LogoutButton({ userId, organizationId, email }: LogoutButtonProps) {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)

  const handleSignOut = async () => {
    try {
      setIsLoading(true)

      // Logout with audit logging
      await logoutWithAudit(userId, organizationId, email)

      // Redirect to login page
      router.push('/login')
      router.refresh()
    } catch (error) {
      console.error('[LOGOUT] Error during logout:', error)
      // Even if logout fails, redirect to login for safety
      router.push('/login')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <button
      onClick={handleSignOut}
      disabled={isLoading}
      className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {isLoading ? 'Signing out...' : 'Sign out'}
    </button>
  )
}
