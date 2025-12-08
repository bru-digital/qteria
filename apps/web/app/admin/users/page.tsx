import { auth } from "@/lib/auth"
import { redirect } from "next/navigation"
import { Users as UsersIcon } from "lucide-react"
import { TopNav } from "@/components/navigation/TopNav"
import { Breadcrumb } from "@/components/navigation/Breadcrumb"
import { isAdmin, isProcessManager } from "@/lib/rbac"

export default async function AdminUsersPage() {
  // Server-side authentication check
  const session = await auth()

  // Redirect to login if not authenticated
  if (!session?.user) {
    redirect("/login")
  }

  // Server-side authorization check - admin or process_manager only
  if (!isAdmin(session.user.role) && !isProcessManager(session.user.role)) {
    redirect("/dashboard")
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <TopNav />

      <main className="max-w-7xl mx-auto px-8 py-6">
        <Breadcrumb
          items={[
            { label: "Dashboard", href: "/dashboard" },
            { label: "Admin" },
            { label: "Users" },
          ]}
        />

        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-12">
          <div className="text-center">
            <UsersIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h1 className="text-2xl font-semibold text-gray-900 mb-2">User Management</h1>
            <p className="text-gray-600 max-w-md mx-auto">
              User management functionality will be implemented in a future release.
              This page will allow you to invite, manage, and deactivate users in your organization.
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}
