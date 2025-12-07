// Application types for Qteria dashboard

export interface Workflow {
  id: string
  name: string
  description?: string
  buckets?: Bucket[]
  criteria?: Criterion[]
  assessments_count?: number
  created_at: string
  updated_at: string
}

export interface Bucket {
  id: string
  workflow_id: string
  name: string
  description?: string
  required: boolean
  display_order: number
}

export interface Criterion {
  id: string
  workflow_id: string
  name: string
  description?: string
  validation_prompt: string
  display_order: number
}

export interface Assessment {
  id: string
  workflow_id: string
  workflow_name: string
  status: "pending" | "processing" | "completed" | "failed"
  overall_pass?: boolean
  criteria_passed?: number
  criteria_failed?: number
  progress_percent?: number
  progress_message?: string
  duration_ms?: number
  created_at: string
  updated_at: string
}

export interface AssessmentEvidence {
  document_id: string
  document_name: string
  page: number
  section?: string
  text_snippet?: string
}

export interface AssessmentResult {
  criteria_id: string
  criteria_name: string
  pass: boolean
  confidence: "high" | "medium" | "low"
  reasoning: string
  evidence?: AssessmentEvidence
}

export interface AssessmentResultsResponse {
  assessment_id: string
  results: AssessmentResult[]
}
