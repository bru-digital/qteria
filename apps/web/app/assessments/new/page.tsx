"use client"

import { useState, useCallback, useEffect } from "react"
import { useDropzone } from "react-dropzone"
import { useRouter } from "next/navigation"
import { useSession } from "next-auth/react"
import type {
  Workflow,
  Bucket,
  DocumentMetadata,
  UploadedDocumentsByBucket,
  UploadStatesByBucket,
  AssessmentDocumentMapping,
} from "@/lib/types/assessment"

/**
 * Document Upload Page
 *
 * Journey Step 2: Project Handler uploads documents to workflow buckets and starts assessment
 *
 * This page provides an intuitive drag-drop interface for uploading documents:
 * - Workflow selector (dropdown showing org's workflows)
 * - Dynamic bucket sections based on selected workflow
 * - Drag-drop zones with visual feedback
 * - File type/size validation (PDF/DOCX, <50MB)
 * - Upload progress indicators
 * - "Start Assessment" button enabled when all required buckets have documents
 *
 * Target: Fast, intuitive upload experience with clear progress indicators
 */

const MAX_FILE_SIZE = 50 * 1024 * 1024 // 50MB
const ALLOWED_TYPES = {
  "application/pdf": [".pdf"],
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
}

export default function NewAssessmentPage() {
  const router = useRouter()
  const { data: session, status } = useSession()

  // Workflow state
  const [workflows, setWorkflows] = useState<Workflow[]>([])
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null)
  const [loadingWorkflows, setLoadingWorkflows] = useState(true)

  // Upload state
  const [uploadedDocs, setUploadedDocs] = useState<UploadedDocumentsByBucket>({})
  const [uploadStates, setUploadStates] = useState<UploadStatesByBucket>({})
  const [error, setError] = useState("")
  const [isStarting, setIsStarting] = useState(false)

  // Handle authentication redirects
  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login")
    }
  }, [status, router])

  // Fetch workflows on mount
  useEffect(() => {
    if (status === "authenticated") {
      fetchWorkflows()
    }
  }, [status])

  // Fetch workflows from API
  const fetchWorkflows = async () => {
    try {
      setLoadingWorkflows(true)
      const response = await fetch("/api/v1/workflows")

      if (!response.ok) {
        throw new Error("Failed to fetch workflows")
      }

      const data = await response.json()
      setWorkflows(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load workflows")
    } finally {
      setLoadingWorkflows(false)
    }
  }

  // Upload document to bucket
  const uploadDocument = async (file: File, bucketId: string) => {
    setUploadStates((prev) => ({
      ...prev,
      [bucketId]: { isUploading: true },
    }))
    setError("")

    try {
      const formData = new FormData()
      formData.append("file", file)
      formData.append("bucket_id", bucketId)

      const response = await fetch("/api/v1/documents", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({
          error: { message: "Upload failed" },
        }))
        throw new Error(errorData.error?.message || "Upload failed")
      }

      const data = await response.json()

      // Validate response structure
      if (!Array.isArray(data) || data.length === 0) {
        throw new Error("No document data returned from upload")
      }

      const document = data[0]

      // Add uploaded document to state
      setUploadedDocs((prev) => ({
        ...prev,
        [bucketId]: [...(prev[bucketId] || []), document],
      }))

      setUploadStates((prev) => ({
        ...prev,
        [bucketId]: { isUploading: false },
      }))
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Upload failed"
      setError(errorMessage)
      setUploadStates((prev) => ({
        ...prev,
        [bucketId]: { isUploading: false, error: errorMessage },
      }))
    }
  }

  // Check if all required buckets have documents
  const canStartAssessment = (): boolean => {
    if (!selectedWorkflow) return false

    const requiredBuckets = selectedWorkflow.buckets.filter((b) => b.required)
    return requiredBuckets.every((bucket) => uploadedDocs[bucket.id]?.length > 0)
  }

  // Start assessment
  const startAssessment = async () => {
    if (!selectedWorkflow) return

    setIsStarting(true)
    setError("")

    try {
      // Build document-bucket mappings
      const documents: AssessmentDocumentMapping[] = []
      Object.entries(uploadedDocs).forEach(([bucketId, docs]) => {
        docs.forEach((doc) => {
          documents.push({
            bucket_id: bucketId,
            document_id: doc.id,
            file_name: doc.file_name,
            storage_key: doc.storage_key,
            file_size: doc.file_size_bytes,
          })
        })
      })

      const response = await fetch("/api/v1/assessments", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          workflow_id: selectedWorkflow.id,
          documents,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({
          error: { message: "Failed to start assessment" },
        }))
        throw new Error(errorData.error?.message || "Failed to start assessment")
      }

      const assessment = await response.json()
      router.push(`/assessments/${assessment.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start assessment")
      setIsStarting(false)
    }
  }

  // Loading state
  if (status === "loading" || loadingWorkflows) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div
            className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"
            role="status"
            aria-label="Loading"
          ></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  // Unauthenticated state (will redirect)
  if (status === "unauthenticated") {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <button
                onClick={() => router.push("/dashboard")}
                className="text-gray-600 hover:text-gray-900 mr-4"
              >
                ← Back
              </button>
              <h1 className="text-xl font-bold text-gray-900">New Assessment</h1>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {/* Workflow Selector */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Select Workflow
          </h2>
          <WorkflowSelector
            workflows={workflows}
            selectedWorkflow={selectedWorkflow}
            onSelect={setSelectedWorkflow}
          />
        </div>

        {/* Document Buckets */}
        {selectedWorkflow && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Upload Documents
              </h2>
              <p className="text-sm text-gray-600 mb-6">
                Upload documents to each bucket. Required buckets are marked with{" "}
                <span className="text-red-500">*</span>
              </p>

              {selectedWorkflow.buckets
                .sort((a, b) => a.order_index - b.order_index)
                .map((bucket) => (
                  <BucketUploadZone
                    key={bucket.id}
                    bucket={bucket}
                    uploadedDocs={uploadedDocs[bucket.id] || []}
                    uploadState={uploadStates[bucket.id]}
                    onUpload={(file) => uploadDocument(file, bucket.id)}
                  />
                ))}
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mt-6">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg
                  className="h-5 w-5 text-red-400"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Start Assessment Button */}
        {selectedWorkflow && (
          <div className="mt-8 flex justify-end">
            <button
              onClick={startAssessment}
              disabled={!canStartAssessment() || isStarting}
              className="px-6 py-3 bg-blue-600 text-white rounded-md font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              {isStarting && (
                <div
                  className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"
                  role="status"
                  aria-label="Starting assessment"
                ></div>
              )}
              {isStarting ? "Starting..." : "Start Assessment"}
            </button>
          </div>
        )}
      </main>
    </div>
  )
}

/**
 * Workflow Selector Component
 * Dropdown for selecting a workflow
 */
interface WorkflowSelectorProps {
  workflows: Workflow[]
  selectedWorkflow: Workflow | null
  onSelect: (workflow: Workflow | null) => void
}

function WorkflowSelector({
  workflows,
  selectedWorkflow,
  onSelect,
}: WorkflowSelectorProps) {
  if (workflows.length === 0) {
    return (
      <div className="text-gray-500 text-sm">
        No workflows available. Please create a workflow first.
      </div>
    )
  }

  return (
    <div>
      <select
        value={selectedWorkflow?.id || ""}
        onChange={(e) => {
          const workflow = workflows.find((w) => w.id === e.target.value)
          onSelect(workflow || null)
        }}
        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-500"
      >
        <option value="">Select a workflow...</option>
        {workflows.map((workflow) => (
          <option key={workflow.id} value={workflow.id}>
            {workflow.name}
            {workflow.description && ` - ${workflow.description}`}
          </option>
        ))}
      </select>
    </div>
  )
}

/**
 * Bucket Upload Zone Component
 * Drag-drop zone for uploading documents to a specific bucket
 */
interface BucketUploadZoneProps {
  bucket: Bucket
  uploadedDocs: DocumentMetadata[]
  uploadState?: { isUploading: boolean; error?: string }
  onUpload: (file: File) => void
}

function BucketUploadZone({
  bucket,
  uploadedDocs,
  uploadState,
  onUpload,
}: BucketUploadZoneProps) {
  const [validationError, setValidationError] = useState<string>("")

  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: any[]) => {
      setValidationError("")

      if (rejectedFiles.length > 0) {
        const rejection = rejectedFiles[0]
        if (rejection.errors[0].code === "file-too-large") {
          setValidationError("File too large. Maximum 50MB.")
        } else if (rejection.errors[0].code === "file-invalid-type") {
          setValidationError("Invalid file type. Only PDF and DOCX allowed.")
        } else {
          setValidationError("File validation failed. Please try again.")
        }
        return
      }

      if (acceptedFiles.length > 0) {
        onUpload(acceptedFiles[0])
      }
    },
    [onUpload]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ALLOWED_TYPES,
    maxSize: MAX_FILE_SIZE,
    multiple: false,
  })

  return (
    <div className="border border-gray-200 rounded-lg p-4 mb-4 last:mb-0">
      <h3 className="text-base font-semibold text-gray-900 mb-2">
        {bucket.name}
        {bucket.required && <span className="text-red-500 ml-2">*</span>}
      </h3>

      {/* Drag-Drop Zone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition ${
          isDragActive
            ? "border-blue-500 bg-blue-50"
            : uploadState?.isUploading
            ? "border-gray-300 bg-gray-50 cursor-not-allowed"
            : "border-gray-300 hover:border-blue-400 hover:bg-gray-50"
        }`}
      >
        <input {...getInputProps()} disabled={uploadState?.isUploading} />
        {uploadState?.isUploading ? (
          <div>
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
            <p className="text-gray-600">Uploading...</p>
          </div>
        ) : (
          <>
            <svg
              className="mx-auto h-12 w-12 text-gray-400 mb-2"
              stroke="currentColor"
              fill="none"
              viewBox="0 0 48 48"
              aria-hidden="true"
            >
              <path
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <p className="text-base text-gray-700 mb-1">
              Drag & drop PDF or DOCX here, or click to browse
            </p>
            <p className="text-sm text-gray-500">Max 50MB</p>
          </>
        )}
      </div>

      {/* Validation Error */}
      {validationError && (
        <p className="text-red-500 text-sm mt-2">{validationError}</p>
      )}

      {/* Upload State Error */}
      {uploadState?.error && (
        <p className="text-red-500 text-sm mt-2">{uploadState.error}</p>
      )}

      {/* Uploaded Documents */}
      {uploadedDocs.length > 0 && (
        <div className="mt-4 space-y-2">
          {uploadedDocs.map((doc) => (
            <div
              key={doc.id}
              className="flex items-center gap-2 p-2 bg-green-50 rounded"
            >
              <span className="text-green-600 font-bold">✓</span>
              <span className="flex-1 text-sm text-gray-900">{doc.file_name}</span>
              <span className="text-xs text-gray-500">
                {(doc.file_size_bytes / 1024 / 1024).toFixed(2)} MB
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
