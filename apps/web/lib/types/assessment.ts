/**
 * TypeScript types for assessment data structures
 *
 * These types match the backend API contracts defined in:
 * - apps/api/app/schemas/workflow.py
 * - apps/api/app/schemas/assessment.py
 * - apps/api/app/schemas/document.py
 */

/**
 * Document bucket within a workflow
 * Represents a category for organizing uploaded documents
 */
export interface Bucket {
  id: string
  name: string
  required: boolean
  order_index: number
}

/**
 * Validation criterion within a workflow
 * Defines rules that AI will check against documents
 */
export interface Criteria {
  id: string
  name: string
  description: string
  applies_to_bucket_ids: string[]
}

/**
 * Workflow definition
 * Template for document validation with buckets and criteria
 */
export interface Workflow {
  id: string
  name: string
  description: string
  organization_id: string
  created_by: string
  created_at: string
  updated_at: string
  is_archived: boolean
  buckets: Bucket[]
  criteria: Criteria[]
}

/**
 * Uploaded document metadata
 * Returned from POST /v1/documents endpoint
 */
export interface DocumentMetadata {
  id: string
  file_name: string
  file_size_bytes: number
  content_type: string
  storage_key: string
  bucket_id?: string
  uploaded_at: string
}

/**
 * Document-bucket mapping for assessment creation
 * Used in POST /v1/assessments request body
 */
export interface AssessmentDocumentMapping {
  bucket_id: string
  document_id: string
}

/**
 * Assessment status enum
 */
export type AssessmentStatus = "pending" | "processing" | "completed" | "failed"

/**
 * Assessment response from API
 * Returned from POST /v1/assessments and GET /v1/assessments/:id
 */
export interface Assessment {
  id: string
  workflow_id: string
  organization_id: string
  created_by: string
  status: AssessmentStatus
  created_at: string
  started_at: string | null
  completed_at: string | null
  duration_ms: number | null
  estimated_completion_time?: string
  workflow?: Workflow
  assessment_documents?: AssessmentDocument[]
}

/**
 * Assessment document with bucket information
 * Used in assessment details display
 */
export interface AssessmentDocument {
  id: string
  assessment_id: string
  bucket_id: string
  file_name: string
  storage_key: string
  file_size_bytes: number
  uploaded_at: string
  bucket?: Bucket
}

/**
 * API error response structure
 * Consistent error format from backend
 */
export interface APIError {
  error: {
    code: string
    message: string
    details?: Record<string, unknown>
    request_id: string
  }
}

/**
 * Upload state for tracking file uploads per bucket
 */
export interface UploadState {
  isUploading: boolean
  progress?: number
  error?: string
}

/**
 * Uploaded documents organized by bucket ID
 * Used in component state management
 */
export type UploadedDocumentsByBucket = Record<string, DocumentMetadata[]>

/**
 * Upload states organized by bucket ID
 * Used in component state management
 */
export type UploadStatesByBucket = Record<string, UploadState>
