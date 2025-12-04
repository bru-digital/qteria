"use client"

import { use, useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { ChevronLeft, CheckCircle, XCircle, AlertTriangle, ChevronDown, ChevronUp, ExternalLink } from "lucide-react"
import { TopNav } from "@/components/navigation/TopNav"
import { Breadcrumb } from "@/components/navigation/Breadcrumb"
import { CardSkeleton } from "@/components/ui/LoadingSkeleton"

// This will be replaced with actual API calls
const useAssessmentQuery = (id: string) => {
  const [isLoading] = useState(false)
  const [assessment] = useState<any>(null)

  return { data: assessment, isLoading }
}

const useAssessmentResults = (id: string, enabled: boolean) => {
  const [results] = useState<any>(null)

  return { data: results }
}

interface Props {
  params: Promise<{ id: string }>
}

function ProgressIndicator({ percent, message }: { percent: number; message: string }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-8">
      <div className="max-w-md mx-auto">
        <div className="text-center mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-2">Processing Assessment</h2>
          <p className="text-sm text-gray-600">{message}</p>
        </div>

        <div className="mb-4">
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-gray-600">Progress</span>
            <span className="font-semibold text-gray-900">{percent}%</span>
          </div>
          <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-500 transition-all duration-500 ease-out rounded-full"
              style={{ width: `${percent}%` }}
            />
          </div>
        </div>

        <div className="text-xs text-gray-500 text-center">
          Estimated time: ~{Math.max(1, Math.round((100 - percent) / 10))} minutes remaining
        </div>
      </div>
    </div>
  )
}

function ResultCard({ result }: { result: any }) {
  const [isExpanded, setIsExpanded] = useState(false)

  const icons = {
    pass: { Icon: CheckCircle, color: "text-green-500" },
    fail: { Icon: XCircle, color: "text-red-500" },
    uncertain: { Icon: AlertTriangle, color: "text-yellow-500" },
  }

  const status = result.pass ? "pass" : result.confidence === "low" ? "uncertain" : "fail"
  const { Icon, color } = icons[status]

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-5 py-4 flex items-start justify-between text-left"
      >
        <div className="flex items-start space-x-3 flex-1">
          <Icon className={`h-6 w-6 flex-shrink-0 mt-0.5 ${color}`} />
          <div className="flex-1 min-w-0">
            <h3 className="text-base font-semibold text-gray-900">{result.criteria_name}</h3>
            {result.pass && (
              <span className="inline-flex items-center px-2 py-1 mt-2 text-xs font-medium text-green-700 bg-green-50 rounded-full">
                PASS
              </span>
            )}
            {!result.pass && (
              <span className="inline-flex items-center px-2 py-1 mt-2 text-xs font-medium text-red-700 bg-red-50 rounded-full">
                FAIL
              </span>
            )}
          </div>
        </div>
        {isExpanded ? (
          <ChevronUp className="h-5 w-5 text-gray-400 flex-shrink-0 ml-2" />
        ) : (
          <ChevronDown className="h-5 w-5 text-gray-400 flex-shrink-0 ml-2" />
        )}
      </button>

      {isExpanded && (
        <div className="px-5 pb-4 space-y-4 border-t border-gray-100">
          {result.evidence && (
            <div className="mt-4">
              <label className="text-sm font-medium text-gray-700 block mb-2">Evidence</label>
              <a
                href={`/api/documents/${result.evidence.document_id}?page=${result.evidence.page}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center space-x-2 text-sm font-mono text-blue-500 hover:text-blue-600 hover:underline"
              >
                <span>
                  {result.evidence.document_name}, page {result.evidence.page}
                  {result.evidence.section && `, section ${result.evidence.section}`}
                </span>
                <ExternalLink className="h-3 w-3" />
              </a>
              {result.evidence.text_snippet && (
                <div className="mt-2 bg-gray-50 p-3 rounded-md text-sm text-gray-600 leading-relaxed">
                  &ldquo;{result.evidence.text_snippet}&rdquo;
                </div>
              )}
            </div>
          )}

          <div>
            <label className="text-sm font-medium text-gray-700 block mb-2">AI Reasoning</label>
            <div className="bg-gray-50 p-3 rounded-md text-sm text-gray-600 leading-relaxed">
              {result.reasoning}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default function AssessmentDetailPage({ params }: Props) {
  const { id } = use(params)
  const router = useRouter()
  const { data: assessment, isLoading } = useAssessmentQuery(id)
  const { data: results } = useAssessmentResults(id, assessment?.status === "completed")

  // Simulate polling for assessment status updates
  useEffect(() => {
    if (assessment?.status === "processing") {
      const interval = setInterval(() => {
        // In real implementation, this would refetch the assessment status
        console.log("Polling assessment status...")
      }, 30000) // Poll every 30 seconds

      return () => clearInterval(interval)
    }
  }, [assessment?.status])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <TopNav />
        <main className="max-w-7xl mx-auto px-8 py-6">
          <CardSkeleton />
        </main>
      </div>
    )
  }

  if (!assessment) {
    return (
      <div className="min-h-screen bg-gray-50">
        <TopNav />
        <main className="max-w-7xl mx-auto px-8 py-6">
          <div className="text-center py-12">
            <h2 className="text-xl font-semibold text-gray-900">Assessment not found</h2>
            <p className="text-sm text-gray-600 mt-2">
              The assessment you&apos;re looking for doesn&apos;t exist or you don&apos;t have access to it.
            </p>
            <button
              onClick={() => router.push("/assessments")}
              className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
            >
              Back to Assessments
            </button>
          </div>
        </main>
      </div>
    )
  }

  const isProcessing = assessment.status === "processing" || assessment.status === "pending"

  return (
    <div className="min-h-screen bg-gray-50">
      <TopNav />

      <main className="max-w-7xl mx-auto px-8 py-6">
        <Breadcrumb
          items={[
            { label: "Dashboard", href: "/dashboard" },
            { label: "Assessments", href: "/assessments" },
            { label: `Assessment ${id.slice(0, 8)}...` },
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
        </div>

        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6 mb-6">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-semibold text-gray-900">{assessment.workflow_name}</h1>
              <p className="text-sm text-gray-500 mt-1">
                Started {new Date(assessment.created_at).toLocaleString()}
              </p>
            </div>
            <span className={`px-3 py-1 text-sm font-medium rounded-full ${
              assessment.status === "completed"
                ? "bg-green-100 text-green-700"
                : assessment.status === "processing"
                ? "bg-blue-100 text-blue-700"
                : "bg-gray-100 text-gray-700"
            }`}>
              {assessment.status}
            </span>
          </div>

          {assessment.status === "completed" && (
            <div className="mt-6 grid grid-cols-2 gap-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-500">Overall Result</div>
                <div className={`text-2xl font-semibold mt-1 ${
                  assessment.overall_pass ? "text-green-600" : "text-red-600"
                }`}>
                  {assessment.overall_pass ? "PASS" : "FAIL"}
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-500">Criteria Passed</div>
                <div className="text-2xl font-semibold text-gray-900 mt-1">
                  {assessment.criteria_passed}/{assessment.criteria_passed + assessment.criteria_failed}
                </div>
              </div>
            </div>
          )}
        </div>

        {isProcessing && (
          <ProgressIndicator
            percent={assessment.progress_percent || 0}
            message={assessment.progress_message || "Initializing assessment..."}
          />
        )}

        {assessment.status === "completed" && results && (
          <div className="space-y-3">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Validation Results</h2>
            {results.results?.map((result: any) => (
              <ResultCard key={result.criteria_id} result={result} />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
