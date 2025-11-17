# [STORY-017] Document Upload UI with Drag-Drop

**Type**: Story
**Epic**: EPIC-04 (Document Processing)
**Journey Step**: Step 2 - Upload Documents Interface
**Priority**: P0 (MVP Critical - User-Facing)
**RICE Score**: 90 (R:100 × I:2 × C:90% ÷ E:2)

---

## User Value

**Job-to-Be-Done**: When Project Handlers need to upload certification documents, they want an intuitive drag-drop interface with progress indicators, so they can quickly upload multiple documents without technical friction.

**Value Delivered**: Beautiful, intuitive document upload experience that makes uploading PDFs feel effortless, achieving high user satisfaction and reducing support requests.

**Success Metric**: Upload task completion rate >95%, user satisfaction score >4/5.

---

## Acceptance Criteria

- [ ] Document upload page at `/assessments/new`
- [ ] Workflow selector (dropdown showing org's workflows)
- [ ] Bucket sections showing workflow's document buckets
- [ ] Drag-drop zone for each bucket
- [ ] Click to browse files (alternative to drag-drop)
- [ ] File type validation (PDF/DOCX only) with error message
- [ ] File size validation (<50MB) with error message
- [ ] Upload progress indicator (percentage + loading spinner)
- [ ] Success message when upload completes
- [ ] Error handling (network errors, API errors)
- [ ] "Start Assessment" button enabled when required buckets filled
- [ ] Responsive design (works on desktop, tablet)

---

## Technical Approach

**Tech Stack Components Used**:
- Frontend: Next.js 14+ (App Router), React
- Drag-Drop: react-dropzone
- UI Library: Tailwind CSS, Shadcn UI
- State Management: React useState

**Upload Page** (`app/assessments/new/page.tsx`):
```typescript
"use client"
import { useState, useCallback } from "react"
import { useDropzone } from "react-dropzone"
import { useRouter } from "next/navigation"

const MAX_FILE_SIZE = 50 * 1024 * 1024 // 50MB
const ALLOWED_TYPES = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]

export default function NewAssessmentPage() {
  const router = useRouter()
  const [selectedWorkflow, setSelectedWorkflow] = useState(null)
  const [uploadedDocs, setUploadedDocs] = useState({})
  const [uploading, setUploading] = useState({})
  const [error, setError] = useState("")

  const uploadDocument = async (file: File, bucketId: string) => {
    setUploading(prev => ({ ...prev, [bucketId]: true }))
    setError("")

    try {
      const formData = new FormData()
      formData.append("file", file)
      formData.append("bucket_id", bucketId)

      const response = await fetch("/api/v1/documents", {
        method: "POST",
        body: formData
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || "Upload failed")
      }

      const document = await response.json()

      // Store uploaded document
      setUploadedDocs(prev => ({
        ...prev,
        [bucketId]: [...(prev[bucketId] || []), document]
      }))

    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(prev => ({ ...prev, [bucketId]: false }))
    }
  }

  const canStartAssessment = () => {
    if (!selectedWorkflow) return false

    const requiredBuckets = selectedWorkflow.buckets.filter(b => b.required)
    return requiredBuckets.every(bucket => uploadedDocs[bucket.id]?.length > 0)
  }

  const startAssessment = async () => {
    try {
      const documents = Object.entries(uploadedDocs).flatMap(([bucketId, docs]) =>
        docs.map(doc => ({
          bucket_id: bucketId,
          document_id: doc.id
        }))
      )

      const response = await fetch("/api/v1/assessments", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          workflow_id: selectedWorkflow.id,
          documents
        })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail)
      }

      const assessment = await response.json()
      router.push(`/assessments/${assessment.id}`)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">New Assessment</h1>

      {/* Workflow Selector */}
      <div className="mb-8">
        <label className="block font-medium mb-2">Select Workflow</label>
        {/* Workflow dropdown component */}
      </div>

      {/* Document Buckets */}
      {selectedWorkflow && (
        <div className="space-y-6">
          {selectedWorkflow.buckets.map(bucket => (
            <BucketUploadZone
              key={bucket.id}
              bucket={bucket}
              uploadedDocs={uploadedDocs[bucket.id] || []}
              isUploading={uploading[bucket.id]}
              onUpload={(file) => uploadDocument(file, bucket.id)}
            />
          ))}
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded p-4 mt-6 text-red-700">
          {error}
        </div>
      )}

      {/* Start Assessment Button */}
      <button
        onClick={startAssessment}
        disabled={!canStartAssessment()}
        className="mt-8 bg-blue-600 text-white px-6 py-3 rounded font-semibold hover:bg-blue-700 disabled:opacity-50"
      >
        Start Assessment
      </button>
    </div>
  )
}

function BucketUploadZone({ bucket, uploadedDocs, isUploading, onUpload }) {
  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    if (rejectedFiles.length > 0) {
      const rejection = rejectedFiles[0]
      if (rejection.errors[0].code === "file-too-large") {
        alert("File too large. Maximum 50MB.")
      } else if (rejection.errors[0].code === "file-invalid-type") {
        alert("Invalid file type. Only PDF and DOCX allowed.")
      }
      return
    }

    if (acceptedFiles.length > 0) {
      onUpload(acceptedFiles[0])
    }
  }, [onUpload])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"]
    },
    maxSize: MAX_FILE_SIZE,
    multiple: false
  })

  return (
    <div className="border rounded-lg p-6">
      <h3 className="text-xl font-semibold mb-2">
        {bucket.name}
        {bucket.required && <span className="text-red-500 ml-2">*</span>}
      </h3>

      {/* Drag-Drop Zone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition ${
          isDragActive ? "border-blue-500 bg-blue-50" : "border-gray-300"
        }`}
      >
        <input {...getInputProps()} />
        {isUploading ? (
          <div>
            <div className="spinner mb-2"></div>
            <p>Uploading...</p>
          </div>
        ) : (
          <>
            <p className="text-lg">Drag & drop PDF here, or click to browse</p>
            <p className="text-sm text-gray-500 mt-2">Max 50MB</p>
          </>
        )}
      </div>

      {/* Uploaded Documents */}
      {uploadedDocs.length > 0 && (
        <div className="mt-4 space-y-2">
          {uploadedDocs.map(doc => (
            <div key={doc.id} className="flex items-center gap-2 p-2 bg-green-50 rounded">
              <span className="text-green-600">✓</span>
              <span>{doc.file_name}</span>
              <span className="text-sm text-gray-500">
                ({(doc.file_size / 1024 / 1024).toFixed(2)} MB)
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
```

---

## Dependencies

- **Blocked By**:
  - STORY-015 (Upload API) - need POST /v1/documents endpoint
  - STORY-016 (Start Assessment) - need POST /v1/assessments endpoint
  - STORY-010 (List Workflows) - need to populate workflow selector
- **Blocks**: Nothing (completes Journey Step 2 UI)

---

## Estimation

**Effort**: 2 person-days

**Breakdown**:
- UI layout: 0.5 days (workflow selector, bucket sections)
- Drag-drop integration: 0.5 days (react-dropzone setup)
- Upload logic: 0.5 days (API calls, progress tracking)
- Error handling: 0.5 days (validation, error messages)

---

## Definition of Done

- [ ] Upload page accessible at `/assessments/new`
- [ ] Workflow selector populated with org's workflows
- [ ] Drag-drop zones for each bucket
- [ ] Click to browse files works
- [ ] File type validation (PDF/DOCX)
- [ ] File size validation (<50MB)
- [ ] Upload progress indicator shown
- [ ] Success message after upload
- [ ] Error messages for validation failures
- [ ] "Start Assessment" button enabled when ready
- [ ] Starts assessment successfully
- [ ] Responsive design tested
- [ ] Code reviewed and merged to main

---

## Testing Requirements

**E2E Tests**:
- [ ] Select workflow → buckets displayed
- [ ] Drag PDF into bucket → upload starts
- [ ] Upload completes → success message shown
- [ ] Upload all required buckets → "Start Assessment" enabled
- [ ] Click "Start Assessment" → redirect to assessment page
- [ ] Upload invalid file type → error message
- [ ] Upload file >50MB → error message

---

## Risks & Mitigations

**Risk**: Drag-drop confusing for non-technical users
- **Mitigation**: Clear instructions, support click-to-browse alternative

**Risk**: Upload progress not visible (users think it's frozen)
- **Mitigation**: Show percentage + spinner, estimate time remaining

---

## Notes

- This completes **Journey Step 2 UI** - Project Handler uploads documents
- After completing this story, proceed to STORY-018 (Document Download)
