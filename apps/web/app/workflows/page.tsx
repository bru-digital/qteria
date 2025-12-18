'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Plus, FileText, Search } from 'lucide-react'
import { TopNav } from '@/components/navigation/TopNav'
import { Breadcrumb } from '@/components/navigation/Breadcrumb'
import { EmptyState } from '@/components/ui/EmptyState'
import { TableSkeleton } from '@/components/ui/LoadingSkeleton'
import { useRouter } from 'next/navigation'
import type { Workflow } from '@/types/app'

// TODO(API Integration): Replace with React Query hook when backend is ready
// Expected endpoint: GET /v1/workflows
// Returns: Array of workflows for user's organization
// Implementation: Use @tanstack/react-query with proper auth headers
// Reference: apps/api/app/api/v1/endpoints/workflows.py (when implemented)
const useWorkflowsQuery = () => {
  const [isLoading] = useState(false)
  const [workflows] = useState<Workflow[]>([])

  return { data: workflows, isLoading }
}

export default function WorkflowsPage() {
  const router = useRouter()
  const { data: workflows, isLoading } = useWorkflowsQuery()
  const [searchQuery, setSearchQuery] = useState('')

  const filteredWorkflows = workflows?.filter(workflow =>
    workflow.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="min-h-screen bg-gray-50">
      <TopNav />

      <main className="max-w-7xl mx-auto px-8 py-6">
        <Breadcrumb items={[{ label: 'Dashboard', href: '/dashboard' }, { label: 'Workflows' }]} />

        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">Workflows</h1>
            <p className="text-sm text-gray-600 mt-1">
              Manage validation workflows for different certification types
            </p>
          </div>

          <Link
            href="/workflows/new"
            className="flex items-center space-x-2 px-6 py-3 text-base font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
          >
            <Plus className="h-5 w-5" />
            <span>Create Workflow</span>
          </Link>
        </div>

        {!isLoading && workflows.length > 0 && (
          <div className="mb-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search workflows..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        )}

        {isLoading ? (
          <TableSkeleton rows={5} />
        ) : workflows.length === 0 ? (
          <EmptyState
            icon={FileText}
            title="No workflows yet"
            description="Create your first validation workflow to start assessing documents."
            action={{
              label: 'Create Workflow',
              onClick: () => router.push('/workflows/new'),
            }}
          />
        ) : (
          <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Buckets
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Criteria
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Assessments
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredWorkflows?.map(workflow => (
                  <tr
                    key={workflow.id}
                    onClick={() => router.push(`/workflows/${workflow.id}`)}
                    className="hover:bg-gray-50 cursor-pointer transition-colors"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{workflow.name}</div>
                      {workflow.description && (
                        <div className="text-sm text-gray-500">{workflow.description}</div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {workflow.buckets_count || 0}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {workflow.criteria_count || 0}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {workflow.assessments_count || 0}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(workflow.created_at).toLocaleDateString()}
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
