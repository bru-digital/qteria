'use client'

import { useForm, useFieldArray } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { useSession } from 'next-auth/react'

/**
 * Workflow Builder Page
 *
 * Journey Step 1: Process Manager creates validation workflows
 *
 * This page provides an intuitive form for creating workflows with:
 * - Dynamic bucket management (add/remove/reorder)
 * - Dynamic criteria management with bucket targeting
 * - Real-time validation with Zod
 * - API integration with error handling
 *
 * Target: <30 minutes to create first workflow
 */

// Zod validation schema matching API contract
const workflowSchema = z.object({
  name: z
    .string()
    .trim()
    .min(1, 'Workflow name is required')
    .max(255)
    .refine(val => val.length > 0, 'Workflow name cannot be only whitespace'),
  description: z
    .string()
    .trim()
    .max(2000)
    .transform(val => val.trim()),
  buckets: z
    .array(
      z.object({
        name: z
          .string()
          .trim()
          .min(1, 'Bucket name is required')
          .max(100)
          .refine(val => val.length > 0, 'Bucket name cannot be only whitespace'),
        required: z.boolean(),
        order_index: z.number(),
      })
    )
    .min(1, 'At least one bucket is required'),
  criteria: z
    .array(
      z.object({
        name: z
          .string()
          .trim()
          .min(1, 'Criteria name is required')
          .max(255)
          .refine(val => val.length > 0, 'Criteria name cannot be only whitespace'),
        description: z
          .string()
          .trim()
          .max(2000)
          .transform(val => val.trim()),
        // Array indices (0-based) that map to bucket order_index
        // These will be transformed to actual bucket positions before sending to API
        applies_to_bucket_ids: z.array(z.number()),
      })
    )
    .min(1, 'At least one criteria is required'),
})

type WorkflowForm = z.infer<typeof workflowSchema>

export default function NewWorkflowPage() {
  const router = useRouter()
  const { data: session, status } = useSession()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  const form = useForm<WorkflowForm>({
    resolver: zodResolver(workflowSchema),
    defaultValues: {
      name: '',
      description: '',
      buckets: [{ name: '', required: true, order_index: 0 }],
      criteria: [{ name: '', description: '', applies_to_bucket_ids: [] }],
    },
  })

  const {
    register,
    control,
    handleSubmit,
    watch,
    formState: { errors },
  } = form

  const {
    fields: buckets,
    append: addBucket,
    remove: removeBucket,
  } = useFieldArray({
    control,
    name: 'buckets',
  })

  const {
    fields: criteria,
    append: addCriteria,
    remove: removeCriteria,
  } = useFieldArray({
    control,
    name: 'criteria',
  })

  // Watch criteria for bucket selection
  const watchedCriteria = watch('criteria')

  // Handle authentication redirects after hooks
  if (status === 'unauthenticated') {
    router.push('/login')
    return null
  }

  // Show loading while checking auth
  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div
            className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"
            role="status"
            aria-label="Loading authentication status"
          ></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  // Role-based access control: Only process_manager and admin can create workflows
  const allowedRoles = ['process_manager', 'admin']
  if (session?.user?.role && !allowedRoles.includes(session.user.role)) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md mx-auto text-center">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="flex justify-center mb-4">
              <svg
                className="h-12 w-12 text-red-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Access Denied</h2>
            <p className="text-gray-700 mb-4">
              You do not have permission to create workflows. Only Process Managers and
              Administrators can create workflows.
            </p>
            <p className="text-sm text-gray-600 mb-4">
              Your role: <span className="font-medium">{session.user.role}</span>
            </p>
            <button
              onClick={() => router.push('/workflows')}
              className="px-6 py-3 bg-blue-600 text-white rounded-md font-semibold hover:bg-blue-700"
            >
              Go to Workflows
            </button>
          </div>
        </div>
      </div>
    )
  }

  const onSubmit = async (data: WorkflowForm) => {
    setIsSubmitting(true)
    setError('')

    try {
      // Transform criteria applies_to_bucket_ids from array indices to 0-indexed positions
      // This ensures bucket indices are always numbers (not strings from checkbox values)
      const transformedData = {
        ...data,
        criteria: data.criteria.map(c => ({
          ...c,
          applies_to_bucket_ids: c.applies_to_bucket_ids.map(Number),
        })),
      }

      // Call Next.js API proxy route (handles authentication server-side)
      const response = await fetch('/api/v1/workflows', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(transformedData),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({
          detail: { message: 'Failed to create workflow' },
        }))

        // Provide specific error messages based on status codes
        let errorMessage: string
        switch (response.status) {
          case 400:
            errorMessage =
              errorData.detail?.message || 'Invalid workflow data. Please check your inputs.'
            break
          case 401:
            errorMessage = 'Your session has expired. Please log in again.'
            break
          case 403:
            errorMessage = "You don't have permission to create workflows."
            break
          case 422:
            errorMessage =
              errorData.detail?.message || 'Validation failed. Please check your inputs.'
            break
          case 500:
            errorMessage = 'Server error. Please try again or contact support.'
            break
          default:
            errorMessage =
              errorData.detail?.message || errorData.message || 'Failed to create workflow'
        }

        throw new Error(errorMessage)
      }

      const workflow = await response.json()
      router.push(`/workflows/${workflow.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <button
                onClick={() => router.push('/workflows')}
                className="text-gray-600 hover:text-gray-900 mr-4"
              >
                ← Back
              </button>
              <h1 className="text-xl font-bold text-gray-900">Create Workflow</h1>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
          {/* Workflow Details Section */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Workflow Details</h2>

            {/* Workflow Name */}
            <div className="mb-4">
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                Workflow Name <span className="text-red-500">*</span>
              </label>
              <input
                id="name"
                type="text"
                {...register('name')}
                className={`w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 ${
                  errors.name
                    ? 'border-red-500 focus:ring-red-200'
                    : 'border-gray-300 focus:ring-blue-200 focus:border-blue-500'
                }`}
                placeholder="e.g., Medical Device - Class II"
              />
              {errors.name && <p className="text-red-500 text-sm mt-1">{errors.name.message}</p>}
              <p className="text-xs text-gray-600 mt-1">
                Choose a descriptive name for your validation workflow
              </p>
            </div>

            {/* Description */}
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <textarea
                id="description"
                {...register('description')}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-500"
                rows={3}
                placeholder="Validation workflow for..."
              />
              {errors.description && (
                <p className="text-red-500 text-sm mt-1">{errors.description.message}</p>
              )}
            </div>
          </div>

          {/* Document Buckets Section */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Document Buckets</h2>
              <span className="text-sm text-gray-600">
                {buckets.length} bucket{buckets.length !== 1 ? 's' : ''}
              </span>
            </div>

            <p className="text-sm text-gray-600 mb-4">
              Define categories for organizing uploaded documents. Each bucket can be marked as
              required or optional.
            </p>

            <div className="space-y-3">
              {buckets.map((bucket, index) => (
                <div key={bucket.id} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                  <div className="flex gap-4 items-start">
                    <div className="flex-1">
                      <label
                        htmlFor={`buckets.${index}.name`}
                        className="block text-sm font-medium text-gray-700 mb-1"
                      >
                        Bucket {index + 1}
                      </label>
                      <input
                        id={`buckets.${index}.name`}
                        type="text"
                        {...register(`buckets.${index}.name`)}
                        className={`w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 ${
                          errors.buckets?.[index]?.name
                            ? 'border-red-500 focus:ring-red-200'
                            : 'border-gray-300 focus:ring-blue-200 focus:border-blue-500'
                        }`}
                        placeholder="e.g., Technical Documentation"
                      />
                      {errors.buckets?.[index]?.name && (
                        <p className="text-red-500 text-sm mt-1">
                          {errors.buckets[index]?.name?.message}
                        </p>
                      )}
                    </div>

                    <div className="flex flex-col gap-2 pt-6">
                      <label className="flex items-center gap-2 text-sm text-gray-700">
                        <input
                          type="checkbox"
                          {...register(`buckets.${index}.required`)}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        Required
                      </label>

                      {buckets.length > 1 && (
                        <button
                          type="button"
                          onClick={() => removeBucket(index)}
                          aria-label={`Remove bucket ${index + 1}: ${watch(`buckets.${index}.name`) || 'unnamed'}`}
                          className="text-red-600 hover:text-red-700 text-sm font-medium"
                        >
                          Remove
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {errors.buckets && typeof errors.buckets.message === 'string' && (
              <p className="text-red-500 text-sm mt-2">{errors.buckets.message}</p>
            )}

            <button
              type="button"
              onClick={() => addBucket({ name: '', required: true, order_index: buckets.length })}
              className="mt-4 w-full border-2 border-dashed border-gray-300 rounded-lg px-4 py-3 text-gray-600 hover:border-blue-500 hover:text-blue-600 transition-colors font-medium"
            >
              + Add Bucket
            </button>
          </div>

          {/* Validation Criteria Section */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Validation Criteria</h2>
              <span className="text-sm text-gray-600">{criteria.length} criteria</span>
            </div>

            <p className="text-sm text-gray-600 mb-4">
              Define validation rules that will be checked by AI. You can apply criteria to specific
              buckets or all buckets.
            </p>

            <div className="space-y-4">
              {criteria.map((criteriaItem, index) => (
                <div
                  key={criteriaItem.id}
                  className="border border-gray-200 rounded-lg p-4 bg-gray-50"
                >
                  <div className="space-y-3">
                    <div>
                      <label
                        htmlFor={`criteria.${index}.name`}
                        className="block text-sm font-medium text-gray-700 mb-1"
                      >
                        Criteria {index + 1} <span className="text-red-500">*</span>
                      </label>
                      <input
                        id={`criteria.${index}.name`}
                        type="text"
                        {...register(`criteria.${index}.name`)}
                        className={`w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 ${
                          errors.criteria?.[index]?.name
                            ? 'border-red-500 focus:ring-red-200'
                            : 'border-gray-300 focus:ring-blue-200 focus:border-blue-500'
                        }`}
                        placeholder="e.g., All documents must be signed"
                      />
                      {errors.criteria?.[index]?.name && (
                        <p className="text-red-500 text-sm mt-1">
                          {errors.criteria[index]?.name?.message}
                        </p>
                      )}
                    </div>

                    <div>
                      <label
                        htmlFor={`criteria.${index}.description`}
                        className="block text-sm font-medium text-gray-700 mb-1"
                      >
                        Description
                      </label>
                      <textarea
                        id={`criteria.${index}.description`}
                        {...register(`criteria.${index}.description`)}
                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-500"
                        rows={2}
                        placeholder="Description (optional)"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Applies to buckets
                      </label>
                      <div className="space-y-2">
                        {buckets.map((bucket, bucketIndex) => {
                          const bucketName = form.watch(`buckets.${bucketIndex}.name`)
                          const displayName = bucketName || `Bucket ${bucketIndex + 1}`
                          const isUnnamed = !bucketName

                          return (
                            <label
                              key={bucketIndex}
                              className={`flex items-center gap-2 text-sm ${
                                isUnnamed ? 'text-gray-400 italic' : 'text-gray-700'
                              }`}
                            >
                              <input
                                type="checkbox"
                                value={bucketIndex}
                                {...register(`criteria.${index}.applies_to_bucket_ids`)}
                                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                              />
                              {displayName}
                              {isUnnamed && (
                                <span className="text-xs text-gray-400">(unnamed)</span>
                              )}
                            </label>
                          )
                        })}
                      </div>
                      <p className="text-xs text-gray-500 mt-2">
                        Leave unchecked to apply to all buckets
                      </p>
                    </div>

                    {criteria.length > 1 && (
                      <div className="flex justify-end">
                        <button
                          type="button"
                          onClick={() => removeCriteria(index)}
                          aria-label={`Remove criteria ${index + 1}: ${watch(`criteria.${index}.name`) || 'unnamed'}`}
                          className="text-red-600 hover:text-red-700 text-sm font-medium"
                        >
                          Remove Criteria
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {errors.criteria && typeof errors.criteria.message === 'string' && (
              <p className="text-red-500 text-sm mt-2">{errors.criteria.message}</p>
            )}

            <button
              type="button"
              onClick={() => addCriteria({ name: '', description: '', applies_to_bucket_ids: [] })}
              className="mt-4 w-full border-2 border-dashed border-gray-300 rounded-lg px-4 py-3 text-gray-600 hover:border-blue-500 hover:text-blue-600 transition-colors font-medium"
            >
              + Add Criteria
            </button>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">Error creating workflow</h3>
                  <p className="text-sm text-red-700 mt-1">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Submit Buttons */}
          <div className="flex justify-end gap-4">
            <button
              type="button"
              onClick={() => router.push('/workflows')}
              className="px-6 py-3 border border-gray-300 rounded-md text-gray-700 font-semibold hover:bg-gray-50 transition-colors"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-3 bg-blue-600 text-white rounded-md font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              {isSubmitting && (
                <div
                  className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"
                  role="status"
                  aria-label="Creating workflow"
                ></div>
              )}
              {isSubmitting ? 'Creating...' : 'Create Workflow'}
            </button>
          </div>
        </form>
      </main>
    </div>
  )
}
