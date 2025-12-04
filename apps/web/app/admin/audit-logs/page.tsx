"use client"

import { FileText } from "lucide-react"
import { TopNav } from "@/components/navigation/TopNav"
import { Breadcrumb } from "@/components/navigation/Breadcrumb"

export default function AdminAuditLogsPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <TopNav />

      <main className="max-w-7xl mx-auto px-8 py-6">
        <Breadcrumb
          items={[
            { label: "Dashboard", href: "/dashboard" },
            { label: "Admin", href: "/admin/users" },
            { label: "Audit Logs" },
          ]}
        />

        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-12">
          <div className="text-center">
            <FileText className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h1 className="text-2xl font-semibold text-gray-900 mb-2">Audit Logs</h1>
            <p className="text-gray-600 max-w-md mx-auto">
              Audit log functionality will be implemented in a future release.
              This page will display all user actions for SOC2/ISO 27001 compliance.
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}
