import { auth } from "@/lib/auth"
import { redirect } from "next/navigation"
import { Settings as SettingsIcon } from "lucide-react"
import { TopNav } from "@/components/navigation/TopNav"
import { Breadcrumb } from "@/components/navigation/Breadcrumb"
import { isAdmin, isProcessManager, type UserRoleType } from "@/lib/rbac"

export default async function AdminSettingsPage() {
  // Server-side authentication check
  const session = await auth()

  // Redirect to login if not authenticated
  if (!session?.user) {
    redirect("/login")
  }

  // Server-side authorization check - admin or process_manager only
  const user = session.user as {
    id: string
    email: string
    name?: string | null
    role: UserRoleType
    organizationId: string
  }

  if (!isAdmin(user.role) && !isProcessManager(user.role)) {
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
            { label: "Settings" },
          ]}
        />

        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-12">
          <div className="text-center">
            <SettingsIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h1 className="text-2xl font-semibold text-gray-900 mb-2">Organization Settings</h1>
            <p className="text-gray-600 max-w-md mx-auto">
              Organization settings functionality will be implemented in a future release.
              This page will allow you to configure organization details, billing, and API keys.
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}
