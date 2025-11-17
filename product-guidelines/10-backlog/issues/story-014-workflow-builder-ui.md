# [STORY-014] Workflow Builder UI

**Type**: Story
**Epic**: EPIC-03 (Workflow Management)
**Journey Step**: Step 1 - Process Manager Creates Workflow
**Priority**: P0 (MVP Critical - User-Facing)
**RICE Score**: 90 (R:100 × I:3 × C:90% ÷ E:3)

---

## User Value

**Job-to-Be-Done**: When Process Managers need to create validation workflows, they need an intuitive form with drag-drop bucket management and dynamic criteria fields, so they can set up workflows in <30 minutes without technical knowledge.

**Value Delivered**: Beautiful, intuitive workflow builder that enables non-technical users to create complex validation workflows quickly, achieving the <30 min target from product strategy.

**Success Metric**: Time to create first workflow <30 minutes, workflow creation completion rate >90%.

---

## Acceptance Criteria

- [ ] Workflow creation page at `/workflows/new`
- [ ] Form fields: workflow name (required), description (optional)
- [ ] Dynamic bucket list with "Add Bucket" button
- [ ] Each bucket has: name, required checkbox, drag handle for reordering
- [ ] Dynamic criteria list with "Add Criteria" button
- [ ] Each criteria has: name, description, applies_to_bucket selector (multi-select or "all")
- [ ] "Remove" button for each bucket and criteria
- [ ] Form validation (required fields highlighted)
- [ ] "Save Workflow" button creates workflow via POST /v1/workflows
- [ ] Success: redirect to workflow details page
- [ ] Error: display API error message
- [ ] Loading state during API call
- [ ] Responsive design (works on desktop, tablet)

---

## Technical Approach

**Tech Stack Components Used**:
- Frontend: Next.js 14+ (App Router), React Hook Form, Zod validation
- UI Library: Tailwind CSS, Shadcn UI (form components)
- State Management: React Hook Form (form state)

**Workflow Builder Page** (`app/workflows/new/page.tsx`):
```typescript
"use client"
import { useForm, useFieldArray } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useRouter } from "next/navigation"
import { useState } from "react"

const workflowSchema = z.object({
  name: z.string().min(1, "Workflow name is required").max(255),
  description: z.string().max(2000).optional(),
  buckets: z.array(z.object({
    name: z.string().min(1, "Bucket name is required"),
    required: z.boolean(),
    order_index: z.number()
  })).min(1, "At least one bucket is required"),
  criteria: z.array(z.object({
    name: z.string().min(1, "Criteria name is required"),
    description: z.string().optional(),
    applies_to_bucket_ids: z.array(z.string())
  })).min(1, "At least one criteria is required")
})

type WorkflowForm = z.infer<typeof workflowSchema>

export default function NewWorkflowPage() {
  const router = useRouter()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState("")

  const { register, control, handleSubmit, formState: { errors } } = useForm<WorkflowForm>({
    resolver: zodResolver(workflowSchema),
    defaultValues: {
      name: "",
      description: "",
      buckets: [{ name: "", required: true, order_index: 0 }],
      criteria: [{ name: "", description: "", applies_to_bucket_ids: [] }]
    }
  })

  const { fields: buckets, append: addBucket, remove: removeBucket } = useFieldArray({
    control,
    name: "buckets"
  })

  const { fields: criteria, append: addCriteria, remove: removeCriteria } = useFieldArray({
    control,
    name: "criteria"
  })

  const onSubmit = async (data: WorkflowForm) => {
    setIsSubmitting(true)
    setError("")

    try {
      const response = await fetch("/api/v1/workflows", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || "Failed to create workflow")
      }

      const workflow = await response.json()
      router.push(`/workflows/${workflow.id}`)
    } catch (err) {
      setError(err.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Create Workflow</h1>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        {/* Workflow Name */}
        <div>
          <label className="block font-medium mb-2">Workflow Name *</label>
          <input
            {...register("name")}
            className="w-full border rounded px-3 py-2"
            placeholder="e.g., Machinery Directive 2006/42/EC"
          />
          {errors.name && <p className="text-red-500 text-sm mt-1">{errors.name.message}</p>}
        </div>

        {/* Description */}
        <div>
          <label className="block font-medium mb-2">Description</label>
          <textarea
            {...register("description")}
            className="w-full border rounded px-3 py-2"
            rows={3}
            placeholder="Validation workflow for..."
          />
        </div>

        {/* Buckets */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Document Buckets</h2>
          {buckets.map((bucket, index) => (
            <div key={bucket.id} className="border rounded p-4 mb-4">
              <div className="flex gap-4 items-start">
                <div className="flex-1">
                  <input
                    {...register(`buckets.${index}.name`)}
                    className="w-full border rounded px-3 py-2"
                    placeholder="e.g., Technical Documentation"
                  />
                  {errors.buckets?.[index]?.name && (
                    <p className="text-red-500 text-sm mt-1">
                      {errors.buckets[index].name.message}
                    </p>
                  )}
                </div>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    {...register(`buckets.${index}.required`)}
                  />
                  Required
                </label>
                <button
                  type="button"
                  onClick={() => removeBucket(index)}
                  className="text-red-500"
                  disabled={buckets.length === 1}
                >
                  Remove
                </button>
              </div>
            </div>
          ))}
          <button
            type="button"
            onClick={() => addBucket({ name: "", required: true, order_index: buckets.length })}
            className="border border-dashed rounded px-4 py-2"
          >
            + Add Bucket
          </button>
        </div>

        {/* Criteria */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Validation Criteria</h2>
          {criteria.map((criteriaItem, index) => (
            <div key={criteriaItem.id} className="border rounded p-4 mb-4">
              <input
                {...register(`criteria.${index}.name`)}
                className="w-full border rounded px-3 py-2 mb-2"
                placeholder="e.g., All documents must be signed"
              />
              <textarea
                {...register(`criteria.${index}.description`)}
                className="w-full border rounded px-3 py-2 mb-2"
                rows={2}
                placeholder="Description (optional)"
              />
              <button
                type="button"
                onClick={() => removeCriteria(index)}
                className="text-red-500"
                disabled={criteria.length === 1}
              >
                Remove
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={() => addCriteria({ name: "", description: "", applies_to_bucket_ids: [] })}
            className="border border-dashed rounded px-4 py-2"
          >
            + Add Criteria
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded p-4 text-red-700">
            {error}
          </div>
        )}

        {/* Submit */}
        <button
          type="submit"
          disabled={isSubmitting}
          className="bg-blue-600 text-white px-6 py-3 rounded font-semibold hover:bg-blue-700 disabled:opacity-50"
        >
          {isSubmitting ? "Creating..." : "Create Workflow"}
        </button>
      </form>
    </div>
  )
}
```

---

## Dependencies

- **Blocked By**:
  - STORY-009 (Create Workflow API) - need POST endpoint
  - STORY-011 (Get Workflow Details) - need to view created workflow
- **Blocks**: Nothing (completes Journey Step 1)

---

## Estimation

**Effort**: 3 person-days

**Breakdown**:
- UI layout: 1 day (form structure, styling)
- Dynamic fields logic: 1 day (add/remove buckets/criteria)
- Form validation: 0.5 days (Zod schema, error messages)
- API integration: 0.5 days (POST request, redirect)

---

## Definition of Done

- [ ] Workflow builder page accessible at `/workflows/new`
- [ ] Form has all required fields
- [ ] Can add/remove buckets dynamically
- [ ] Can add/remove criteria dynamically
- [ ] Form validation works (errors shown)
- [ ] Submits to POST /v1/workflows
- [ ] Redirects to workflow details on success
- [ ] Shows error message on failure
- [ ] Loading state during submission
- [ ] Responsive design tested (desktop, tablet)
- [ ] Code reviewed and merged to main

---

## Testing Requirements

**E2E Tests** (critical flow):
- [ ] Fill out form → click "Create Workflow" → workflow created
- [ ] Add 3 buckets, 5 criteria → all saved
- [ ] Remove bucket → bucket not included in API request
- [ ] Submit without name → error shown
- [ ] API returns error → error message displayed
- [ ] Create workflow → redirect to details page

**Usability Tests**:
- [ ] Time to create workflow <30 minutes (target metric)
- [ ] Process Manager can complete without help
- [ ] Error messages clear and actionable

---

## Risks & Mitigations

**Risk**: UI too complex, takes >30 minutes to create workflow
- **Mitigation**: Usability test with TÜV SÜD, simplify UI, provide examples

**Risk**: Form validation errors not clear
- **Mitigation**: Show inline error messages, highlight required fields

---

## Notes

- This completes **Journey Step 1** - Process Manager creates workflow in <30 min
- After completing this story, EPIC-03 is DONE → proceed to EPIC-04 (Document Processing)
