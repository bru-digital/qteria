"use client"

import { useRole } from "@/lib/hooks/useRole"
import {
  CanCreateWorkflow,
  CanRunAssessment,
  CanUploadDocuments,
  AdminOnly,
} from "@/components/RoleGuard"
import {
  FileText,
  PlayCircle,
  Upload,
  Settings,
  FileCheck,
  Users,
  Shield,
} from "lucide-react"

/**
 * Dashboard actions component (Client Component).
 *
 * Redesigned to match professional, minimalistic brand aesthetic:
 * - Clean icon-based sections (no colored borders)
 * - Primary blue CTAs only
 * - Grays for structure (90% of UI)
 * - Subtle shadows for depth
 * - Professional typography hierarchy
 *
 * IMPORTANT: These buttons are UI hints only. Backend always enforces permissions!
 */
export function DashboardActions() {
  const {
    roleTitle,
    canCreateWorkflow,
    canRunAssessment,
    canUploadDocuments,
    canManageUsers,
    isAdmin,
  } = useRole()

  return (
    <div className="space-y-6">
      {/* Section Header */}
      <div className="flex items-baseline justify-between">
        <h2 className="text-xl font-semibold text-gray-900">Quick Actions</h2>
        <span className="text-sm text-gray-500">Based on your role: {roleTitle}</span>
      </div>

      {/* Action Cards Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Workflow Management - Process Manager & Admin */}
        <CanCreateWorkflow>
          <ActionCard
            icon={<FileText className="h-6 w-6 text-gray-600" />}
            title="Workflow Management"
            description="Create and manage validation workflows"
            primaryAction={{
              label: "Create Workflow",
              href: "/workflows/new",
            }}
            secondaryAction={{
              label: "View Workflows",
              href: "/workflows",
            }}
          />
        </CanCreateWorkflow>

        {/* Assessment Management - Project Handler & Admin */}
        <CanRunAssessment>
          <ActionCard
            icon={<PlayCircle className="h-6 w-6 text-gray-600" />}
            title="Assessment Management"
            description="Run AI-powered document validation"
            primaryAction={{
              label: "Start Assessment",
              href: "/assessments/new",
            }}
            secondaryAction={{
              label: "View Results",
              href: "/assessments",
            }}
          />
        </CanRunAssessment>

        {/* Document Upload - Project Handler & Admin */}
        <CanUploadDocuments>
          <ActionCard
            icon={<Upload className="h-6 w-6 text-gray-600" />}
            title="Document Upload"
            description="Upload documents for validation"
            primaryAction={{
              label: "Upload Documents",
              href: "/assessments/new",
            }}
          />
        </CanUploadDocuments>

        {/* Admin Only Section */}
        <AdminOnly>
          <ActionCard
            icon={<Settings className="h-6 w-6 text-gray-600" />}
            title="Administration"
            description="Manage users and organization settings"
            primaryAction={{
              label: "Manage Users",
              href: "/admin/users",
            }}
            secondaryActions={[
              { label: "Organization Settings", href: "/admin/settings" },
              { label: "View Audit Logs", href: "/admin/audit-logs" },
            ]}
          />
        </AdminOnly>
      </div>

      {/* Permission Summary - Minimal Design */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        <p className="text-xs text-gray-500 mb-3">YOUR PERMISSIONS</p>
        <div className="flex flex-wrap gap-2">
          {canCreateWorkflow && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 text-xs font-medium text-gray-700 bg-gray-100 rounded-full">
              <FileCheck className="h-3 w-3" />
              Create Workflows
            </span>
          )}
          {canRunAssessment && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 text-xs font-medium text-gray-700 bg-gray-100 rounded-full">
              <PlayCircle className="h-3 w-3" />
              Run Assessments
            </span>
          )}
          {canUploadDocuments && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 text-xs font-medium text-gray-700 bg-gray-100 rounded-full">
              <Upload className="h-3 w-3" />
              Upload Documents
            </span>
          )}
          {canManageUsers && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 text-xs font-medium text-gray-700 bg-gray-100 rounded-full">
              <Users className="h-3 w-3" />
              Manage Users
            </span>
          )}
          {isAdmin && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 text-xs font-medium text-gray-700 bg-gray-100 rounded-full">
              <Shield className="h-3 w-3" />
              Full Admin Access
            </span>
          )}
        </div>
      </div>

      {/* Info note - Minimal */}
      <div className="mt-6 flex items-start gap-3 rounded-lg bg-gray-50 p-4">
        <div className="flex-shrink-0">
          <svg
            className="h-5 w-5 text-gray-400"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
              clipRule="evenodd"
            />
          </svg>
        </div>
        <p className="text-sm text-gray-600">
          All permissions are enforced on the server for security. Actions shown
          are based on your role.
        </p>
      </div>
    </div>
  )
}

/**
 * ActionCard Component
 * Clean, professional action card with icon, title, description, and buttons
 */
interface ActionCardProps {
  icon: React.ReactNode
  title: string
  description: string
  primaryAction: { label: string; href: string }
  secondaryAction?: { label: string; href: string }
  secondaryActions?: { label: string; href: string }[]
}

function ActionCard({
  icon,
  title,
  description,
  primaryAction,
  secondaryAction,
  secondaryActions,
}: ActionCardProps) {
  return (
    <div className="group relative bg-white rounded-lg border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow">
      {/* Icon & Title */}
      <div className="flex items-start gap-4 mb-4">
        <div className="flex-shrink-0 p-2 bg-gray-50 rounded-lg group-hover:bg-gray-100 transition-colors">
          {icon}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-base font-semibold text-gray-900">{title}</h3>
          <p className="mt-1 text-sm text-gray-600">{description}</p>
        </div>
      </div>

      {/* Actions */}
      <div className="flex flex-wrap gap-2">
        {/* Primary CTA - Blue */}
        <a
          href={primaryAction.href}
          className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
        >
          {primaryAction.label}
        </a>

        {/* Secondary Action */}
        {secondaryAction && (
          <a
            href={secondaryAction.href}
            className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
          >
            {secondaryAction.label}
          </a>
        )}

        {/* Multiple Secondary Actions */}
        {secondaryActions?.map((action, index) => (
          <a
            key={index}
            href={action.href}
            className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
          >
            {action.label}
          </a>
        ))}
      </div>
    </div>
  )
}
