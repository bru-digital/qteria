import { auth } from "@/lib/auth"
import { redirect } from "next/navigation"
import { LogoutButton } from "@/app/dashboard/logout-button"
import { DashboardActions } from "@/app/dashboard/dashboard-actions"
import { getRoleTitle, getRoleColor } from "@/lib/rbac"
import type { UserRoleType } from "@/lib/rbac"

/**
 * Dashboard page (Server Component).
 *
 * Uses server-side authentication check via auth() from Auth.js.
 * This provides true server-side protection without client-side flash.
 */
export default async function DashboardPage() {
  // Server-side authentication check
  const session = await auth()

  // Redirect to login if not authenticated
  if (!session?.user) {
    redirect("/login")
  }

  // TypeScript type guard for session.user
  const user = session.user as {
    id: string
    email: string
    name?: string | null
    role: UserRoleType
    organizationId: string
  }

  const roleTitle = getRoleTitle(user.role)
  const roleColor = getRoleColor(user.role)

  // Role badge colors
  const roleBadgeClasses: Record<string, string> = {
    blue: "bg-blue-100 text-blue-800",
    green: "bg-green-100 text-green-800",
    purple: "bg-purple-100 text-purple-800",
    gray: "bg-gray-100 text-gray-800",
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">Qteria Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${roleBadgeClasses[roleColor] || roleBadgeClasses.gray}`}>
                {roleTitle}
              </span>
              <span className="text-sm text-gray-700">
                {user.email}
              </span>
              <LogoutButton
                userId={user.id}
                organizationId={user.organizationId}
                email={user.email}
              />
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Welcome to Qteria
            </h2>
            <div className="space-y-4">
              <div>
                <p className="text-sm font-medium text-gray-500">User Information</p>
                <div className="mt-2 space-y-2">
                  <p className="text-sm text-gray-700">
                    <span className="font-medium">Email:</span> {user.email}
                  </p>
                  <p className="text-sm text-gray-700">
                    <span className="font-medium">Name:</span> {user.name || "Not set"}
                  </p>
                  <p className="text-sm text-gray-700">
                    <span className="font-medium">Role:</span>{" "}
                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${roleBadgeClasses[roleColor] || roleBadgeClasses.gray}`}>
                      {roleTitle}
                    </span>
                  </p>
                  <p className="text-sm text-gray-700">
                    <span className="font-medium">Organization ID:</span> {user.organizationId}
                  </p>
                </div>
              </div>
              <div className="pt-4 border-t border-gray-200">
                <p className="text-sm text-gray-500">
                  You are successfully authenticated. This is a protected route that requires
                  login to access.
                </p>
              </div>
            </div>
          </div>

          {/* Role-based action buttons */}
          <DashboardActions />
        </div>
      </main>
    </div>
  )
}
