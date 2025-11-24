"use client"

import { useRole } from "@/lib/hooks/useRole"
import {
  CanCreateWorkflow,
  CanRunAssessment,
  CanUploadDocuments,
  AdminOnly,
} from "@/components/RoleGuard"

/**
 * Dashboard actions component (Client Component).
 *
 * Demonstrates role-based UI rendering:
 * - Process Manager: Can create workflows
 * - Project Handler: Can run assessments and upload documents
 * - Admin: Can do everything + admin actions
 *
 * IMPORTANT: These buttons are UI hints only. Backend always enforces permissions!
 */
export function DashboardActions() {
  const {
    roleTitle,
    isProcessManager,
    isProjectHandler,
    isAdmin,
    canCreateWorkflow,
    canRunAssessment,
    canUploadDocuments,
    canManageUsers,
  } = useRole()

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">
        Available Actions
        <span className="ml-2 text-sm font-normal text-gray-500">
          (Based on your role: {roleTitle})
        </span>
      </h3>

      <div className="space-y-6">
        {/* Workflow Management - Process Manager & Admin */}
        <CanCreateWorkflow>
          <div className="border-l-4 border-blue-500 pl-4">
            <h4 className="text-sm font-medium text-gray-900">Workflow Management</h4>
            <p className="text-sm text-gray-500 mb-2">
              Create and manage validation workflows
            </p>
            <div className="flex space-x-2">
              <button className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                Create Workflow
              </button>
              <button className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                View Workflows
              </button>
            </div>
          </div>
        </CanCreateWorkflow>

        {/* Assessment Management - Project Handler & Admin */}
        <CanRunAssessment>
          <div className="border-l-4 border-green-500 pl-4">
            <h4 className="text-sm font-medium text-gray-900">Assessment Management</h4>
            <p className="text-sm text-gray-500 mb-2">
              Run AI-powered document validation
            </p>
            <div className="flex space-x-2">
              <button className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500">
                Start Assessment
              </button>
              <button className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500">
                View Results
              </button>
            </div>
          </div>
        </CanRunAssessment>

        {/* Document Upload - Project Handler & Admin */}
        <CanUploadDocuments>
          <div className="border-l-4 border-yellow-500 pl-4">
            <h4 className="text-sm font-medium text-gray-900">Document Upload</h4>
            <p className="text-sm text-gray-500 mb-2">
              Upload documents for validation
            </p>
            <button className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md shadow-sm text-white bg-yellow-600 hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500">
              Upload Documents
            </button>
          </div>
        </CanUploadDocuments>

        {/* Admin Only Section */}
        <AdminOnly>
          <div className="border-l-4 border-purple-500 pl-4">
            <h4 className="text-sm font-medium text-gray-900">Administration</h4>
            <p className="text-sm text-gray-500 mb-2">
              Manage users and organization settings
            </p>
            <div className="flex space-x-2">
              <button className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md shadow-sm text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500">
                Manage Users
              </button>
              <button className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500">
                Organization Settings
              </button>
              <button className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500">
                View Audit Logs
              </button>
            </div>
          </div>
        </AdminOnly>

        {/* Permission Summary */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Your Permissions</h4>
          <div className="flex flex-wrap gap-2">
            {canCreateWorkflow && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                Create Workflows
              </span>
            )}
            {canRunAssessment && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                Run Assessments
              </span>
            )}
            {canUploadDocuments && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                Upload Documents
              </span>
            )}
            {canManageUsers && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                Manage Users
              </span>
            )}
            {isAdmin && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                Full Admin Access
              </span>
            )}
          </div>
        </div>

        {/* Info note */}
        <div className="mt-4 rounded-md bg-gray-50 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-gray-600">
                <span className="font-medium">Note:</span> Actions shown are based on your role ({roleTitle}).
                All permissions are enforced on the server for security.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
