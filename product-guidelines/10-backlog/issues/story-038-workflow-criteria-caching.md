# [STORY-038] Workflow & Criteria Caching

**Epic**: EPIC-09 - Performance Optimization
**Priority**: P1 (Post-MVP Polish)
**Estimated Effort**: 2 days
**Journey Step**: Cross-Cutting - Performance

---

## User Story

**As a** developer
**I want to** cache frequently accessed workflows in Redis
**So that** repeated queries don't hit the database

---

## Acceptance Criteria

- [ ] Workflows cached in Redis (Upstash)
- [ ] TTL: 1 hour
- [ ] Cache key: `workflow:{workflow_id}`
- [ ] Invalidate cache on UPDATE/DELETE
- [ ] Cache hit rate >80%
- [ ] Reduces database queries for workflows from 3 → 0

---

## Technical Details

**Tech Stack**:
- Redis: Upstash (serverless Redis)
- Library: redis-py

**Implementation**:
```python
import redis
import json

redis_client = redis.from_url(settings.REDIS_URL)

async def get_workflow_cached(workflow_id: str):
    # Try cache first
    cache_key = f"workflow:{workflow_id}"
    cached = redis_client.get(cache_key)

    if cached:
        return json.loads(cached)

    # Cache miss - fetch from database
    workflow = await db.get_workflow_with_relations(workflow_id)

    # Store in cache (1 hour TTL)
    redis_client.setex(
        cache_key,
        3600,  # 1 hour
        json.dumps(workflow.dict())
    )

    return workflow

async def invalidate_workflow_cache(workflow_id: str):
    redis_client.delete(f"workflow:{workflow_id}")
```

**Cache Invalidation**:
```python
@router.put("/workflows/{workflow_id}")
async def update_workflow(...):
    # Update database
    workflow = await db.update_workflow(workflow_id, updates)

    # Invalidate cache
    await invalidate_workflow_cache(workflow_id)

    return workflow
```

---

## RICE Score

**RICE**: (70 × 1 × 0.80) ÷ 2 = **28**

---

## Definition of Done

- [ ] Redis (Upstash) integrated
- [ ] Workflows cached with 1 hour TTL
- [ ] Cache invalidation on UPDATE/DELETE
- [ ] Cache hit rate >80%
- [ ] Database queries reduced
- [ ] Tests pass
- [ ] Code reviewed and merged
