import { auth } from "@/lib/auth"
import { redirect } from "next/navigation"
import { DashboardActions } from "@/app/dashboard/dashboard-actions"
import { TopNav } from "@/components/navigation/TopNav"
import type { UserRoleType } from "@/lib/rbac"

/**
 * Dashboard page (Server Component).
 *
 * Redesigned with professional, minimalistic aesthetic:
 * - Consistent TopNav across all pages
 * - Minimal user info display
 * - Icon-based action cards
 * - Professional typography and spacing
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

  return (
    <div className="min-h-screen bg-gray-50">
      <TopNav />

      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Welcome Section - Minimalistic */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">
            Welcome back{user.name ? `, ${user.name.split(" ")[0]}` : ""}
          </h2>
          <p className="text-gray-600">
            Manage workflows, run assessments, and validate certification documents.
          </p>
        </div>

        {/* Role-based action cards */}
        <DashboardActions />
      </main>
    </div>
  )
}
