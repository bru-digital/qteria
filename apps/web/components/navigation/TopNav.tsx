"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useSession, signOut } from "next-auth/react"
import { LogOut, User, Settings } from "lucide-react"
import { useState, useCallback, useEffect } from "react"

export function TopNav() {
  const pathname = usePathname()
  const { data: session } = useSession()
  const [showUserMenu, setShowUserMenu] = useState(false)

  const isActive = useCallback(
    (path: string) => {
      if (path === "/dashboard") {
        return pathname === "/dashboard"
      }
      return pathname.startsWith(path)
    },
    [pathname]
  )

  const isAdmin = session?.user?.role === "admin" || session?.user?.role === "process_manager"

  // Handle Escape key to close dropdown
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape" && showUserMenu) {
        setShowUserMenu(false)
      }
    }

    document.addEventListener("keydown", handleEscape)
    return () => document.removeEventListener("keydown", handleEscape)
  }, [showUserMenu])

  return (
    <header className="h-16 border-b border-gray-200 bg-white">
      <div className="max-w-7xl mx-auto px-8 h-full flex items-center justify-between">
        <div className="flex items-center space-x-8">
          <Link href="/dashboard" className="text-xl font-semibold text-gray-900">
            Qteria
          </Link>

          <nav className="flex items-center space-x-1">
            <Link
              href="/workflows"
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive("/workflows")
                  ? "bg-gray-100 text-gray-900"
                  : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
              }`}
            >
              Workflows
            </Link>

            <Link
              href="/assessments"
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive("/assessments")
                  ? "bg-gray-100 text-gray-900"
                  : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
              }`}
            >
              Assessments
            </Link>

            {isAdmin && (
              <Link
                href="/admin/users"
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive("/admin")
                    ? "bg-gray-100 text-gray-900"
                    : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
                }`}
              >
                Admin
              </Link>
            )}
          </nav>
        </div>

        <div className="relative">
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <User className="h-4 w-4" />
            <span>{session?.user?.name || session?.user?.email}</span>
          </button>

          {showUserMenu && (
            <>
              <div
                className="fixed inset-0 z-10"
                onClick={() => setShowUserMenu(false)}
              />
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-20">
                <Link
                  href="/admin/settings"
                  className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                  onClick={() => setShowUserMenu(false)}
                >
                  <Settings className="h-4 w-4" />
                  <span>Settings</span>
                </Link>
                <button
                  onClick={() => signOut({ callbackUrl: "/login" })}
                  className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  <LogOut className="h-4 w-4" />
                  <span>Logout</span>
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
