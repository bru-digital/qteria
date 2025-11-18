"use client"

import { useSession, signOut } from "next-auth/react"
import { useRouter } from "next/navigation"

export default function DashboardPage() {
  const { data: session, status } = useSession()
  const router = useRouter()

  if (status === "loading") {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-600">Loading...</div>
      </div>
    )
  }

  if (status === "unauthenticated") {
    router.push("/login")
    return null
  }

  const handleSignOut = async () => {
    await signOut({ redirect: false })
    router.push("/login")
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
              <span className="text-sm text-gray-700">
                {session?.user?.email}
              </span>
              <button
                onClick={handleSignOut}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md"
              >
                Sign out
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Welcome to Qteria
            </h2>
            <div className="space-y-4">
              <div>
                <p className="text-sm font-medium text-gray-500">User Information</p>
                <div className="mt-2 space-y-2">
                  <p className="text-sm text-gray-700">
                    <span className="font-medium">Email:</span> {session?.user?.email}
                  </p>
                  <p className="text-sm text-gray-700">
                    <span className="font-medium">Name:</span> {session?.user?.name || "Not set"}
                  </p>
                  <p className="text-sm text-gray-700">
                    <span className="font-medium">Role:</span> {session?.user?.role}
                  </p>
                  <p className="text-sm text-gray-700">
                    <span className="font-medium">Organization ID:</span> {session?.user?.organizationId}
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
        </div>
      </main>
    </div>
  )
}
