# [STORY-029] Assessment Status Polling

**Epic**: EPIC-06 - Results & Evidence Display
**Priority**: P0 (MVP Critical)
**Estimated Effort**: 2 days
**Journey Step**: Step 3 - Wait for Results

---

## User Story

**As a** Project Handler
**I want to** see real-time progress while my assessment runs
**So that** I know the system is working and can estimate when results will be ready

---

## Acceptance Criteria

- [ ] Status polling starts automatically after submitting assessment
- [ ] Frontend polls `GET /v1/assessments/:id` every 30 seconds
- [ ] Progress indicator shows current status (pending/processing/completed)
- [ ] Estimated time remaining displayed (if available)
- [ ] Auto-redirect to results page when completed
- [ ] Stop polling when status = "completed" or "failed"
- [ ] Handle errors gracefully (timeout, network failure)
- [ ] Polling efficient (no unnecessary requests)

---

## Technical Details

**Tech Stack**:
- Frontend: React useEffect hook + setInterval
- API: `GET /v1/assessments/:id`
- State Management: React Query (automatic polling)

**Polling Flow**:
1. User submits assessment → status: "pending"
2. Frontend starts polling every 30 seconds
3. Status transitions: pending → processing → completed
4. When status = "completed", stop polling and redirect to results
5. If status = "failed", show error message

**API Response**:
```json
{
  "assessment_id": "assess_123",
  "status": "processing",  // pending | processing | completed | failed
  "progress_percent": 40,  // optional: 0-100
  "estimated_completion_seconds": 300,  // optional: time remaining
  "started_at": "2026-01-15T14:30:00Z",
  "updated_at": "2026-01-15T14:32:00Z"
}
```

**Frontend Implementation** (React Query):
```tsx
// hooks/useAssessmentStatus.ts

import { useQuery } from '@tanstack/react-query';

export function useAssessmentStatus(assessmentId: string) {
  return useQuery({
    queryKey: ['assessment', assessmentId],
    queryFn: () => fetchAssessmentStatus(assessmentId),
    refetchInterval: (data) => {
      // Poll every 30s if still processing
      if (data?.status === 'pending' || data?.status === 'processing') {
        return 30000; // 30 seconds
      }
      return false; // Stop polling when completed/failed
    },
    refetchIntervalInBackground: false,
  });
}

// components/AssessmentStatusPage.tsx

export function AssessmentStatusPage({ assessmentId }: { assessmentId: string }) {
  const { data: assessment, isLoading } = useAssessmentStatus(assessmentId);
  const router = useRouter();

  useEffect(() => {
    if (assessment?.status === 'completed') {
      // Redirect to results page
      router.push(`/assessments/${assessmentId}/results`);
    }
  }, [assessment?.status]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <Spinner />
      <h2 className="text-xl font-semibold mt-4">
        {assessment?.status === 'pending' && 'Assessment queued...'}
        {assessment?.status === 'processing' && 'Validating documents...'}
      </h2>

      {assessment?.progress_percent && (
        <ProgressBar value={assessment.progress_percent} className="w-64 mt-4" />
      )}

      {assessment?.estimated_completion_seconds && (
        <p className="text-gray-600 mt-2">
          Estimated time remaining: {Math.ceil(assessment.estimated_completion_seconds / 60)} minutes
        </p>
      )}

      {assessment?.status === 'failed' && (
        <ErrorMessage>
          Assessment failed. Please try again or contact support.
        </ErrorMessage>
      )}
    </div>
  );
}
```

**Alternative Implementation** (Manual useEffect):
```tsx
useEffect(() => {
  let interval: NodeJS.Timeout;

  const poll = async () => {
    const status = await fetchAssessmentStatus(assessmentId);
    setAssessment(status);

    if (status.status === 'completed') {
      clearInterval(interval);
      router.push(`/assessments/${assessmentId}/results`);
    } else if (status.status === 'failed') {
      clearInterval(interval);
      setError('Assessment failed');
    }
  };

  // Initial poll
  poll();

  // Start polling
  interval = setInterval(poll, 30000); // 30 seconds

  return () => clearInterval(interval);
}, [assessmentId]);
```

**Backend API**:
```python
# backend/app/api/v1/assessments.py

@router.get("/assessments/{assessment_id}")
async def get_assessment_status(
    assessment_id: str,
    user: User = Depends(get_current_user)
):
    assessment = await db.get_assessment(assessment_id)

    # Verify user has access
    if assessment.organization_id != user.organization_id:
        raise HTTPException(403, "Forbidden")

    return {
        "assessment_id": assessment.id,
        "status": assessment.status,
        "progress_percent": calculate_progress(assessment),
        "estimated_completion_seconds": estimate_time_remaining(assessment),
        "started_at": assessment.started_at,
        "updated_at": assessment.updated_at
    }
```

---

## Dependencies

**Blocks**:
- None (improves UX but not strictly required)

**Blocked By**:
- STORY-023: Background job queue (needs assessment status updates)
- STORY-016: Start assessment API (needs assessment creation)

---

## Testing Requirements

**Unit Tests** (50% coverage):
- [ ] useAssessmentStatus hook polls correctly
- [ ] Polling stops when status = completed
- [ ] Redirect triggered on completion
- [ ] Error handling for failed assessments

**Integration Tests**:
- [ ] GET /v1/assessments/:id returns status
- [ ] Status transitions correctly (pending → processing → completed)

**E2E Tests** (critical):
- [ ] Submit assessment → See "queued" message
- [ ] Status updates to "processing" after 30s poll
- [ ] Auto-redirect to results when completed
- [ ] Error shown if assessment fails

---

## Design Reference

**Status Page Layout**:
```
┌────────────────────────────────────┐
│                                    │
│          ⏳ (spinner)              │
│                                    │
│    Validating documents...         │
│                                    │
│    ████████░░░░░░░░░░░ 40%        │
│                                    │
│    Estimated time: 5 minutes       │
│                                    │
└────────────────────────────────────┘
```

**Status Messages**:
- pending: "Assessment queued..."
- processing: "Validating documents..."
- completed: (redirect to results)
- failed: "Assessment failed. Please try again."

---

## RICE Score

**Reach**: 100 (every user waits for results)
**Impact**: 2 (medium - improves UX but not core)
**Confidence**: 100%
**Effort**: 2 days

**RICE Score**: (100 × 2 × 1.00) ÷ 2 = **100**

---

## Definition of Done

- [ ] Status polling implemented with React Query or useEffect
- [ ] Polls every 30 seconds while pending/processing
- [ ] Stops polling when completed/failed
- [ ] Progress indicator shown (if available)
- [ ] Estimated time displayed (if available)
- [ ] Auto-redirect to results on completion
- [ ] Error handling for failed assessments
- [ ] No polling in background tabs (save resources)
- [ ] Unit tests pass (50% coverage)
- [ ] E2E test: Submit → Poll → Redirect
- [ ] Code reviewed and merged to main
- [ ] Deployed to staging

---

## Risks & Mitigations

**Risk**: Polling too frequent (overloads backend)
- **Mitigation**: 30 second interval, exponential backoff if needed

**Risk**: Polling never stops (memory leak)
- **Mitigation**: Always clear interval on unmount or completion

**Risk**: User closes tab and misses completion
- **Mitigation**: Email notification (STORY-030)

---

## Notes

This story improves UX by showing progress instead of leaving users wondering "is it working?" Critical for assessments that take 5-10 minutes.

**Reference**: `product-guidelines/00-user-journey.md` (Step 3)
