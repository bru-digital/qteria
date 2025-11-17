# Database Schema Essentials (For Backlog Generation)

> This is a condensed version for Session 10 (backlog generation).
> See `07-database-schema.md` for complete schema with columns, indexes, constraints,
> migration files, query examples, and scaling considerations.

---

## Database Technology

- **Database**: [PostgreSQL/MongoDB/MySQL from tech stack]
- **ORM**: [Prisma/TypeORM/Alembic/etc.]
- **ID Strategy**: [UUIDs/BigInt/CUID]
- **Multi-tenancy**: [Approach - team-based isolation/row-level security/separate schemas]

---

## Tables (Journey Mapping)

### Core Tables

**Authentication & Multi-tenancy:**
- **users** - User accounts (Step 0: Authentication)
- **teams** - Team/organization accounts (multi-tenancy isolation)

**Journey Tables:**
- **[entity1]** - [Purpose and description] (Journey Step 1: [Step name])
- **[entity2]** - [Purpose and description] (Journey Step 2: [Step name])
- **[entity3]** - [Purpose and description] (Journey Step 3: [Step name])
- **[entity4]** - [Purpose and description] (Journey Step 4: [Step name])

### Supporting Tables

**System & Analytics:**
- **usage_events** - Analytics and metrics tracking (for North Star metric)
- **[join_table]** - M:N relationship between [Entity A] and [Entity B]
- **[system_entity]** - [Purpose - e.g., frameworks, templates, etc.]

---

## Entity Relationship Diagram

```
┌─────────────┐       ┌──────────────┐
│    Teams    │───────│    Users     │
└─────────────┘  1:N  └──────┬───────┘
                              │ 1:N
                      ┌───────▼────────┐
                      │   [Entity1]    │
                      └───────┬────────┘
                              │ 1:N
                      ┌───────▼────────┐       ┌──────────────┐
                      │   [Entity2]    │───────│  [Entity3]   │
                      └────────────────┘  M:N  └──────────────┘
                              │ 1:N
                      ┌───────▼────────┐
                      │ Usage Events   │
                      └────────────────┘
```

**Entity Descriptions:**
- **[Entity1]**: [1-sentence purpose - how it serves the journey]
- **[Entity2]**: [1-sentence purpose - how it serves the journey]
- **[Entity3]**: [1-sentence purpose - how it serves the journey]

---

## Key Relationships

### One-to-Many

**Core ownership hierarchy:**
- `teams` → `users` (1:N) - Team has many members
- `users` → `[entity1]` (1:N) - User owns many [entity1 items]
- `[entity1]` → `[entity2]` (1:N) - [Relationship description]

### Many-to-Many

**Cross-entity relationships:**
- `[entity2]` ↔ `[entity3]` (via `[join_table]`) - [Relationship description]

### Foreign Key Behaviors

**ON DELETE CASCADE:**
- `users` deleted → Delete all owned `[entity1]` (GDPR compliance)
- `[entity1]` deleted → Delete all related `[entity2]` (data consistency)

**ON DELETE RESTRICT:**
- Can't delete `[system_entity]` if referenced by `[entity2]` (data integrity)

**ON DELETE SET NULL:**
- `teams` disbanded → `users.team_id` becomes NULL (user keeps account)

---

## Data Access Patterns (for story scope)

These common queries inform story complexity and acceptance criteria:

### Critical Path Queries (Journey Steps 1-3)

**Query 1: [Description - e.g., "List user's items"]**
- Tables: `[entity1]`, `users`
- Complexity: Simple filter + sort
- Story impact: Basic CRUD stories

**Query 2: [Description - e.g., "Get item with related data"]**
- Tables: `[entity2]`, `[entity3]`, `[join_table]`
- Complexity: Multi-table JOIN
- Story impact: Affects story estimation (join complexity)

**Query 3: [Description - e.g., "Filter by status and date"]**
- Tables: `[entity1]`
- Complexity: Filtered query with pagination
- Story impact: List/grid view stories need pagination

### Analytics Queries

**Query: Calculate usage for billing**
- Tables: `usage_events`, `teams`
- Complexity: Aggregation by team + time period
- Story impact: Billing stories need aggregation logic

---

## Notes for Backlog Generation

### Story Scoping Guidance

**Simple stories** (1-2 days):
- Single table CRUD (create/read/update/delete)
- Example: "User can create [entity1]" → INSERT into one table

**Medium stories** (3-5 days):
- Multi-table queries with relationships
- Example: "User can view [entity2] with related [entity3]" → JOIN query + UI

**Complex stories** (5+ days - should be split):
- Multiple entities with business logic
- Aggregations/analytics
- Example: "Admin can view team usage dashboard" → Multiple aggregations + data transformation

### Multi-tenancy Impact

**Row-level security approach:**
- All queries must filter by `team_id` or `user_id`
- Stories need "ensure data isolation" in acceptance criteria

**Schema-based approach:**
- Each team has separate schema
- Stories need "support multi-schema" in technical notes

### Data Migration Stories

If modifying existing schema:
- [ ] Story for writing migration
- [ ] Story for backfilling data
- [ ] Story for testing migration on staging

---

## Technology-Specific Notes

### If using Prisma (TypeScript)
- Stories can leverage Prisma Client for type-safe queries
- Schema changes require `prisma migrate` step
- Include "Update Prisma schema" in relevant stories

### If using Alembic (Python)
- Stories need migration file generation
- Include "Create Alembic migration" in schema-change stories
- Downgrade path required for rollback

### If using raw SQL
- Stories need manual migration scripts
- Include SQL review in acceptance criteria
- Consider query parameterization for security

---

## References

For complete schema details including:
- Full column definitions with types and constraints
- Index strategies and query optimization
- Migration file syntax
- Data types rationale
- Scaling considerations (partitioning, sharding, read replicas)
- Testing strategy
- Alternatives considered ("What We DIDN'T Choose")

See: `product-guidelines/07-database-schema.md`
