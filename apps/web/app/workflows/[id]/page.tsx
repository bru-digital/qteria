"use client"

import { use } from "react"
import { useRouter } from "next/navigation"
import { Archive, Trash2, ChevronLeft } from "lucide-react"
import { TopNav } from "@/components/navigation/TopNav"
import { Breadcrumb } from "@/components/navigation/Breadcrumb"
import { CardSkeleton } from "@/components/ui/LoadingSkeleton"
import { useToast } from "@/components/ui/Toast"
import { useState, useEffect } from "react"
import type { Workflow, Bucket, Criterion } from "@/types/app"

/**
 * useWorkflowQuery Hook
 *
 * Fetches a single workflow by ID from the Next.js API proxy route.
 * The proxy route handles authentication and forwards the request to FastAPI backend.
 *
 * Endpoint: GET /api/v1/workflows/:id
 * Backend: GET /v1/workflows/:id (via proxy)
 *
 * States:
 * - isLoading: true while fetching data
 * - data: Workflow object when loaded, null if not found
 * - error: Error message if request fails
 */
const useWorkflowQuery = (id: string) => {
  const [workflow, setWorkflow] = useState<Workflow | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    const fetchWorkflow = async () => {
      try {
        setIsLoading(true)
        setError(null)
        const response = await fetch(`/api/v1/workflows/${id}`)

        if (cancelled) return

        if (!response.ok) {
          if (response.status === 404) {
            setWorkflow(null)
            return
          }
          // Extract error message from backend response
          const errorData = await response.json()
          throw new Error(errorData.error?.message || "Failed to fetch workflow")
        }

        const data = await response.json()

        if (!cancelled) {
          setWorkflow(data)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Unknown error")
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false)
        }
      }
    }

    fetchWorkflow()

    return () => {
      cancelled = true
    }
  }, [id])

  return { data: workflow, isLoading, error }
}

interface Props {
  params: Promise<{ id: string }>
}

export default function WorkflowDetailPage({ params }: Props) {
  const { id } = use(params)
  const router = useRouter()
  const { showToast } = useToast()
  const { data: workflow, isLoading, error } = useWorkflowQuery(id)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [isArchiving, setIsArchiving] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)

  const handleArchive = async () => {
    setIsArchiving(true)
    try {
      // TODO: Implement archive API call (connects to PATCH /v1/workflows/:id/archive)
      // GitHub Issue: TBD
      await new Promise((resolve) => setTimeout(resolve, 1000)) // Simulate API call
      showToast("success", "Workflow archived successfully")
      router.push("/workflows")
    } catch (error) {
      showToast("error", "Failed to archive workflow")
      setIsArchiving(false)
    }
  }

  const handleDelete = async () => {
    setIsDeleting(true)
    try {
      // TODO: Implement delete API call (connects to DELETE /v1/workflows/:id)
      // GitHub Issue: TBD
      await new Promise((resolve) => setTimeout(resolve, 1000)) // Simulate API call
      showToast("success", "Workflow deleted successfully")
      setShowDeleteDialog(false)
      router.push("/workflows")
    } catch (error) {
      showToast("error", "Failed to delete workflow")
      setIsDeleting(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <TopNav />
        <main className="max-w-7xl mx-auto px-8 py-6">
          <div className="text-center py-12">
            <p className="text-gray-600">Loading workflow...</p>
          </div>
        </main>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <TopNav />
        <main className="max-w-7xl mx-auto px-8 py-6">
          <div className="text-center py-12">
            <h2 className="text-xl font-semibold text-red-900">Error Loading Workflow</h2>
            <p className="text-sm text-gray-600 mt-2">
              {error}
            </p>
            <div className="flex items-center justify-center space-x-4 mt-4">
              <button
                onClick={() => router.push("/workflows")}
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                Back to Workflows
              </button>
              <button
                onClick={() => window.location.reload()}
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                Try Again
              </button>
            </div>
          </div>
        </main>
      </div>
    )
  }

  if (!workflow) {
    return (
      <div className="min-h-screen bg-gray-50">
        <TopNav />
        <main className="max-w-7xl mx-auto px-8 py-6">
          <div className="text-center py-12">
            <h2 className="text-xl font-semibold text-gray-900">Workflow not found</h2>
            <p className="text-sm text-gray-600 mt-2">
              The workflow you&apos;re looking for doesn&apos;t exist or you don&apos;t have access to it.
            </p>
            <button
              onClick={() => router.push("/workflows")}
              className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
            >
              Back to Workflows
            </button>
          </div>
        </main>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <TopNav />

      <main className="max-w-7xl mx-auto px-8 py-6">
        <Breadcrumb
          items={[
            { label: "Dashboard", href: "/dashboard" },
            { label: "Workflows", href: "/workflows" },
            { label: workflow.name },
          ]}
        />

        <div className="flex items-center justify-between mb-6">
          <button
            onClick={() => router.back()}
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
          >
            <ChevronLeft className="h-5 w-5" />
            <span>Back</span>
          </button>

          <div className="flex items-center space-x-3">
            <button
              onClick={handleArchive}
              disabled={isArchiving || isDeleting}
              className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Archive className={`h-4 w-4 ${isArchiving ? "animate-pulse" : ""}`} />
              <span>{isArchiving ? "Archiving..." : "Archive"}</span>
            </button>

            <button
              onClick={() => setShowDeleteDialog(true)}
              disabled={isArchiving || isDeleting}
              className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Trash2 className="h-4 w-4" />
              <span>Delete</span>
            </button>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
          <h1 className="text-2xl font-semibold text-gray-900">{workflow.name}</h1>
          {workflow.description && (
            <p className="text-base text-gray-600 mt-2">{workflow.description}</p>
          )}

          <div className="mt-6 grid grid-cols-3 gap-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-sm text-gray-500">Buckets</div>
              <div className="text-2xl font-semibold text-gray-900 mt-1">
                {workflow.buckets?.length || 0}
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-sm text-gray-500">Criteria</div>
              <div className="text-2xl font-semibold text-gray-900 mt-1">
                {workflow.criteria?.length || 0}
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-sm text-gray-500">Assessments</div>
              <div className="text-2xl font-semibold text-gray-900 mt-1">
                {workflow.assessments_count || 0}
              </div>
            </div>
          </div>

          <div className="mt-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Document Buckets</h2>
            <div className="space-y-3">
              {workflow.buckets?.map((bucket) => (
                <div key={bucket.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium text-gray-900">{bucket.name}</h3>
                      {bucket.description && (
                        <p className="text-sm text-gray-600 mt-1">{bucket.description}</p>
                      )}
                    </div>
                    {bucket.required && (
                      <span className="px-2 py-1 text-xs font-medium text-blue-700 bg-blue-50 rounded">
                        Required
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Validation Criteria</h2>
            <div className="space-y-3">
              {workflow.criteria?.map((criterion) => (
                <div key={criterion.id} className="border border-gray-200 rounded-lg p-4">
                  <h3 className="font-medium text-gray-900">{criterion.name}</h3>
                  {criterion.description && (
                    <p className="text-sm text-gray-600 mt-1">{criterion.description}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>

      {showDeleteDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900">Delete Workflow</h3>
            <p className="text-sm text-gray-600 mt-2">
              Are you sure you want to delete this workflow? This action cannot be undone.
            </p>
            <div className="flex items-center justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowDeleteDialog(false)}
                disabled={isDeleting}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={isDeleting}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isDeleting ? "Deleting..." : "Delete"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
