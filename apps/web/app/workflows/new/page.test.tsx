import { describe, it, expect, vi, beforeEach } from "vitest"
import { render, screen, waitFor } from "@testing-library/react"
import { userEvent } from "@testing-library/user-event"
import { useRouter } from "next/navigation"
import { useSession } from "next-auth/react"
import NewWorkflowPage from "./page"

// Mock Next.js navigation
vi.mock("next/navigation", () => ({
  useRouter: vi.fn(),
}))

// Mock Next Auth
vi.mock("next-auth/react", () => ({
  useSession: vi.fn(),
}))

// Mock fetch for API calls
global.fetch = vi.fn()

describe("NewWorkflowPage", () => {
  const mockRouter = {
    push: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
    ;(useRouter as any).mockReturnValue(mockRouter)
    ;(global.fetch as any).mockClear()
  })

  describe("Authentication", () => {
    it("redirects to login when user is unauthenticated", () => {
      ;(useSession as any).mockReturnValue({
        data: null,
        status: "unauthenticated",
      })

      render(<NewWorkflowPage />)

      expect(mockRouter.push).toHaveBeenCalledWith("/login")
    })

    it("shows loading state while checking authentication", () => {
      ;(useSession as any).mockReturnValue({
        data: null,
        status: "loading",
      })

      render(<NewWorkflowPage />)

      expect(screen.getByText("Loading...")).toBeInTheDocument()
    })
  })

  describe("Role-Based Access Control", () => {
    it("allows process_manager to access the form", () => {
      ;(useSession as any).mockReturnValue({
        data: {
          user: {
            id: "user-123",
            email: "pm@example.com",
            role: "process_manager",
            organizationId: "org-123",
            name: "Process Manager",
          },
        },
        status: "authenticated",
      })

      render(<NewWorkflowPage />)

      expect(screen.getByText("Create Workflow")).toBeInTheDocument()
      expect(screen.getByLabelText(/Workflow Name/i)).toBeInTheDocument()
    })

    it("allows admin to access the form", () => {
      ;(useSession as any).mockReturnValue({
        data: {
          user: {
            id: "admin-123",
            email: "admin@example.com",
            role: "admin",
            organizationId: "org-123",
            name: "Admin",
          },
        },
        status: "authenticated",
      })

      render(<NewWorkflowPage />)

      expect(screen.getByText("Create Workflow")).toBeInTheDocument()
    })

    it("denies access to project_handler", () => {
      ;(useSession as any).mockReturnValue({
        data: {
          user: {
            id: "ph-123",
            email: "ph@example.com",
            role: "project_handler",
            organizationId: "org-123",
            name: "Project Handler",
          },
        },
        status: "authenticated",
      })

      render(<NewWorkflowPage />)

      expect(screen.getByText("Access Denied")).toBeInTheDocument()
      expect(screen.getByText(/project_handler/i)).toBeInTheDocument()
    })
  })

  describe("Form Rendering", () => {
    beforeEach(() => {
      ;(useSession as any).mockReturnValue({
        data: {
          user: {
            id: "user-123",
            email: "pm@example.com",
            role: "process_manager",
            organizationId: "org-123",
            name: "PM",
          },
        },
        status: "authenticated",
      })
    })

    it("renders workflow name and description fields", () => {
      render(<NewWorkflowPage />)

      expect(screen.getByLabelText(/Workflow Name/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/Description/i)).toBeInTheDocument()
    })

    it("renders default bucket and criteria", () => {
      render(<NewWorkflowPage />)

      expect(screen.getByText("Document Buckets")).toBeInTheDocument()
      expect(screen.getByText("Validation Criteria")).toBeInTheDocument()
      expect(screen.getByText("1 bucket")).toBeInTheDocument()
      expect(screen.getByText("1 criteria")).toBeInTheDocument()
    })

    it("has Add Bucket button", () => {
      render(<NewWorkflowPage />)

      expect(screen.getByText("+ Add Bucket")).toBeInTheDocument()
    })

    it("has Add Criteria button", () => {
      render(<NewWorkflowPage />)

      expect(screen.getByText("+ Add Criteria")).toBeInTheDocument()
    })
  })

  describe("Dynamic Bucket Management", () => {
    beforeEach(() => {
      ;(useSession as any).mockReturnValue({
        data: {
          user: {
            id: "user-123",
            email: "pm@example.com",
            role: "process_manager",
            organizationId: "org-123",
          },
        },
        status: "authenticated",
      })
    })

    it("adds a new bucket when Add Bucket is clicked", async () => {
      const user = userEvent.setup()
      render(<NewWorkflowPage />)

      const addButton = screen.getByText("+ Add Bucket")
      await user.click(addButton)

      await waitFor(() => {
        expect(screen.getByText("2 buckets")).toBeInTheDocument()
      })
    })

    it("removes a bucket when Remove is clicked", async () => {
      const user = userEvent.setup()
      render(<NewWorkflowPage />)

      // Add a second bucket
      await user.click(screen.getByText("+ Add Bucket"))

      await waitFor(() => {
        expect(screen.getByText("2 buckets")).toBeInTheDocument()
      })

      // Remove one bucket
      const removeButtons = screen.getAllByText("Remove")
      await user.click(removeButtons[0])

      await waitFor(() => {
        expect(screen.getByText("1 bucket")).toBeInTheDocument()
      })
    })

    it("prevents removing the last bucket", () => {
      render(<NewWorkflowPage />)

      // With only 1 bucket, remove button should not be present
      expect(screen.queryByText("Remove")).not.toBeInTheDocument()
    })
  })

  describe("Form Validation", () => {
    beforeEach(() => {
      ;(useSession as any).mockReturnValue({
        data: {
          user: {
            id: "user-123",
            email: "pm@example.com",
            role: "process_manager",
            organizationId: "org-123",
          },
        },
        status: "authenticated",
      })
    })

    it("shows error when workflow name is empty", async () => {
      const user = userEvent.setup()
      render(<NewWorkflowPage />)

      const submitButton = screen.getByText("Create Workflow")
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText("Workflow name is required")).toBeInTheDocument()
      })
    })

    it("shows error when bucket name is empty", async () => {
      const user = userEvent.setup()
      render(<NewWorkflowPage />)

      // Fill workflow name but leave bucket name empty
      const workflowNameInput = screen.getByLabelText(/Workflow Name/i)
      await user.type(workflowNameInput, "Test Workflow")

      const submitButton = screen.getByText("Create Workflow")
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText("Bucket name is required")).toBeInTheDocument()
      })
    })

    it("shows error when criteria name is empty", async () => {
      const user = userEvent.setup()
      render(<NewWorkflowPage />)

      // Fill workflow name and bucket name but leave criteria name empty
      const workflowNameInput = screen.getByLabelText(/Workflow Name/i)
      await user.type(workflowNameInput, "Test Workflow")

      const bucketInputs = screen.getAllByPlaceholderText(/Technical Documentation/i)
      await user.type(bucketInputs[0], "Bucket 1")

      const submitButton = screen.getByText("Create Workflow")
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText("Criteria name is required")).toBeInTheDocument()
      })
    })
  })

  describe("API Integration", () => {
    beforeEach(() => {
      ;(useSession as any).mockReturnValue({
        data: {
          user: {
            id: "user-123",
            email: "pm@example.com",
            role: "process_manager",
            organizationId: "org-123",
          },
        },
        status: "authenticated",
      })
    })

    it("submits form data to API proxy route", async () => {
      const user = userEvent.setup()
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: "workflow-123" }),
      })

      render(<NewWorkflowPage />)

      // Fill form
      const workflowNameInput = screen.getByLabelText(/Workflow Name/i)
      await user.type(workflowNameInput, "Test Workflow")

      const bucketInputs = screen.getAllByPlaceholderText(/Technical Documentation/i)
      await user.type(bucketInputs[0], "Documents")

      const criteriaInputs = screen.getAllByPlaceholderText(/All documents must be signed/i)
      await user.type(criteriaInputs[0], "Check signatures")

      // Submit
      const submitButton = screen.getByText("Create Workflow")
      await user.click(submitButton)

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith("/api/v1/workflows", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: expect.stringContaining("Test Workflow"),
        })
      })
    })

    it("redirects to workflow details on successful creation", async () => {
      const user = userEvent.setup()
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: "workflow-123" }),
      })

      render(<NewWorkflowPage />)

      // Fill and submit form (simplified)
      await user.type(screen.getByLabelText(/Workflow Name/i), "Test Workflow")
      const bucketInputs = screen.getAllByPlaceholderText(/Technical Documentation/i)
      await user.type(bucketInputs[0], "Docs")
      const criteriaInputs = screen.getAllByPlaceholderText(/All documents must be signed/i)
      await user.type(criteriaInputs[0], "Criteria 1")
      
      await user.click(screen.getByText("Create Workflow"))

      await waitFor(() => {
        expect(mockRouter.push).toHaveBeenCalledWith("/workflows/workflow-123")
      })
    })

    it("displays error message when API returns error", async () => {
      const user = userEvent.setup()
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({
          detail: { message: "Validation failed" },
        }),
      })

      render(<NewWorkflowPage />)

      // Fill and submit form
      await user.type(screen.getByLabelText(/Workflow Name/i), "Test")
      const bucketInputs = screen.getAllByPlaceholderText(/Technical Documentation/i)
      await user.type(bucketInputs[0], "Bucket")
      const criteriaInputs = screen.getAllByPlaceholderText(/All documents must be signed/i)
      await user.type(criteriaInputs[0], "Criteria")
      
      await user.click(screen.getByText("Create Workflow"))

      await waitFor(() => {
        expect(screen.getByText("Validation failed")).toBeInTheDocument()
      })
    })

    it("shows loading state during submission", async () => {
      const user = userEvent.setup()
      ;(global.fetch as any).mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 1000))
      )

      render(<NewWorkflowPage />)

      // Fill and submit form
      await user.type(screen.getByLabelText(/Workflow Name/i), "Test")
      const bucketInputs = screen.getAllByPlaceholderText(/Technical Documentation/i)
      await user.type(bucketInputs[0], "Bucket")
      const criteriaInputs = screen.getAllByPlaceholderText(/All documents must be signed/i)
      await user.type(criteriaInputs[0], "Criteria")
      
      await user.click(screen.getByText("Create Workflow"))

      // Check loading state
      expect(screen.getByText("Creating...")).toBeInTheDocument()
    })
  })
})
