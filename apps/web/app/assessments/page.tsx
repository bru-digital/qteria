"use client"

import { useState } from "react"
import Link from "next/link"
import { Plus, ClipboardList } from "lucide-react"
import { TopNav } from "@/components/navigation/TopNav"
import { Breadcrumb } from "@/components/navigation/Breadcrumb"
import { EmptyState } from "@/components/ui/EmptyState"
import { TableSkeleton } from "@/components/ui/LoadingSkeleton"
import { useRouter } from "next/navigation"
import type { Assessment } from "@/types/app"

// TODO(API Integration): Replace with React Query hook when backend is ready
// Expected endpoint: GET /v1/assessments
// Returns: Array of assessments for user's organization with workflow references
// Implementation: Use @tanstack/react-query with proper auth headers
// Reference: apps/api/app/api/v1/endpoints/assessments.py (when implemented)
const useAssessmentsQuery = () => {
  const [isLoading] = useState(false)
  const [assessments] = useState<Assessment[]>([])

  return { data: assessments, isLoading }
}

function StatusBadge({ status }: { status: string }) {
  const colors = {
    pending: "bg-gray-100 text-gray-700",
    processing: "bg-blue-100 text-blue-700",
    completed: "bg-green-100 text-green-700",
    failed: "bg-red-100 text-red-700",
  }

  return (
    <span className={`px-2 py-1 text-xs font-medium rounded-full ${colors[status as keyof typeof colors] || colors.pending}`}>
      {status}
    </span>
  )
}

export default function AssessmentsPage() {
  const router = useRouter()
  const { data: assessments, isLoading } = useAssessmentsQuery()
  const [statusFilter, setStatusFilter] = useState<string>("all")

  const filteredAssessments = assessments?.filter((assessment) =>
    statusFilter === "all" || assessment.status === statusFilter
  )

  return (
    <div className="min-h-screen bg-gray-50">
      <TopNav />

      <main className="max-w-7xl mx-auto px-8 py-6">
        <Breadcrumb
          items={[
            { label: "Dashboard", href: "/dashboard" },
            { label: "Assessments" },
          ]}
        />

        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">Assessments</h1>
            <p className="text-sm text-gray-600 mt-1">
              View validation results and track assessment progress
            </p>
          </div>

          <Link
            href="/assessments/new"
            className="flex items-center space-x-2 px-6 py-3 text-base font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
          >
            <Plus className="h-5 w-5" />
            <span>Start Assessment</span>
          </Link>
        </div>

        {!isLoading && assessments.length > 0 && (
          <div className="mb-6">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="processing">Processing</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
            </select>
          </div>
        )}

        {isLoading ? (
          <TableSkeleton rows={5} />
        ) : assessments.length === 0 ? (
          <EmptyState
            icon={ClipboardList}
            title="No assessments yet"
            description="Start your first assessment to validate documents against your workflows."
            action={{
              label: "Start Assessment",
              onClick: () => router.push("/assessments/new"),
            }}
          />
        ) : (
          <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Workflow
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Result
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Duration
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredAssessments?.map((assessment) => (
                  <tr
                    key={assessment.id}
                    onClick={() => router.push(`/assessments/${assessment.id}`)}
                    className="hover:bg-gray-50 cursor-pointer transition-colors"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{assessment.workflow_name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <StatusBadge status={assessment.status} />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {assessment.status === "completed" ? (
                        <span className={assessment.overall_pass ? "text-green-600" : "text-red-600"}>
                          {assessment.criteria_passed ?? 0}/{(assessment.criteria_passed ?? 0) + (assessment.criteria_failed ?? 0)} passed
                        </span>
                      ) : (
                        <span className="text-gray-400">—</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(assessment.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {assessment.duration_ms ? `${Math.round(assessment.duration_ms / 1000)}s` : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  )
}
