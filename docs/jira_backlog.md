# Proposed Jira Backlog

## Purpose

This is a Jira-ready backlog for the current GeoSyn transformation work. I cannot create Jira tickets directly from this environment, so this document is structured to be pasted into Jira manually or imported by your team.

The ticket key column is intentionally left as `TBD` until Jira creates the real IDs.

## Epic: GeoSyn V2 Architecture Foundation

### Ticket 1

- Key: `GEOSYN-TBD`
- Title: `Establish Alembic migration workflow for GeoSyn backend`
- Type: Story
- Priority: High
- Description:
  Replace the current ad hoc schema evolution approach with Alembic-based migrations so the backend can support v2 schema changes safely.
- Acceptance Criteria:
  - Alembic is configured in `backend/`
  - baseline migration exists
  - developers can run `alembic upgrade head`
  - legacy local startup still works

### Ticket 2

- Key: `GEOSYN-TBD`
- Title: `Add canonical v2 event models to backend`
- Type: Story
- Priority: High
- Description:
  Introduce `events`, `event_evidence`, `event_entities`, and legacy mapping tables in the backend model layer.
- Acceptance Criteria:
  - v2 models are registered with SQLAlchemy metadata
  - migration creates the tables
  - models compile and app startup is not broken

### Ticket 3

- Key: `GEOSYN-TBD`
- Title: `Backfill legacy event clusters into canonical v2 events`
- Type: Task
- Priority: High
- Description:
  Create a one-time backfill path from `event_clusters` to canonical `events` so v2 APIs have usable data immediately.
- Acceptance Criteria:
  - backfill script exists
  - script is idempotent
  - legacy cluster to event mapping table is populated
  - evidence and event entities are backfilled

### Ticket 4

- Key: `GEOSYN-TBD`
- Title: `Introduce customer and watchlist foundation for v2 workflows`
- Type: Story
- Priority: High
- Description:
  Add customer scope to the backend with demo-customer seeding and watchlist support.
- Acceptance Criteria:
  - customer and watchlist tables exist
  - demo customer can be seeded
  - default watchlists are created
  - customer context dependency is available for APIs

### Ticket 5

- Key: `GEOSYN-TBD`
- Title: `Add exposure link foundation to backend`
- Type: Story
- Priority: High
- Description:
  Introduce the first exposure graph table so events can eventually be connected to customer-specific relevance.
- Acceptance Criteria:
  - `exposure_links` table exists
  - ORM model exists
  - API/service layer can query by customer and target entity

### Ticket 6

- Key: `GEOSYN-TBD`
- Title: `Create EventServiceV2 and canonical event read APIs`
- Type: Story
- Priority: High
- Description:
  Add a service layer for canonical events and expose parallel v2 event endpoints without breaking legacy endpoints.
- Acceptance Criteria:
  - v2 event service exists
  - `GET /api/v1/events/v2`
  - `GET /api/v1/events/v2/{event_id}`
  - customer-scoped serialization works

### Ticket 7

- Key: `GEOSYN-TBD`
- Title: `Dual-write clustering output into canonical events`
- Type: Story
- Priority: High
- Description:
  Whenever clustering assigns documents to a legacy cluster, keep the canonical event tables in sync.
- Acceptance Criteria:
  - clustering writes to legacy cluster tables
  - clustering also syncs evidence and event entities to v2 event tables
  - no regression in existing clustering behavior

## Epic: Jira And Developer Workflow Automation

### Ticket 8

- Key: `GEOSYN-TBD`
- Title: `Add Jira-aware git hooks and commit template`
- Type: Task
- Priority: Medium
- Description:
  Add repository-side developer tooling so branches and commits consistently include Jira issue keys.
- Acceptance Criteria:
  - `.githooks/prepare-commit-msg` exists
  - `.githooks/commit-msg` exists
  - `.gitmessage-jira.txt` exists
  - setup script configures local repo hooks and commit template

### Ticket 9

- Key: `GEOSYN-TBD`
- Title: `Add pull request template for Jira-linked PRs`
- Type: Task
- Priority: Medium
- Description:
  Ensure PRs consistently reference Jira work items and capture rollout/testing context.
- Acceptance Criteria:
  - PR template exists in `.github/`
  - PR template requires Jira key and testing notes

### Ticket 10

- Key: `GEOSYN-TBD`
- Title: `Document Jira + GitHub integration workflow for GeoSyn`
- Type: Task
- Priority: Medium
- Description:
  Provide a repo-local setup guide for Jira-GitHub integration, Smart Commits, and commit conventions.
- Acceptance Criteria:
  - setup guide exists in `docs/`
  - includes official Atlassian references
  - includes branch/commit/PR naming convention

## Epic: Next V2 Product Slice

### Ticket 11

- Key: `GEOSYN-TBD`
- Title: `Add v2 alert models and customer-scoped alert generation`
- Type: Story
- Priority: High
- Description:
  Build the next layer after canonical events: alerts derived from events and exposure context.
- Acceptance Criteria:
  - alert v2 tables exist
  - alerts can be generated for a customer
  - alerts include supporting evidence

### Ticket 12

- Key: `GEOSYN-TBD`
- Title: `Add exposure import path for suppliers and facilities`
- Type: Story
- Priority: High
- Description:
  Create a CSV import flow so pilot customers can load exposure data quickly.
- Acceptance Criteria:
  - CSV schema documented
  - import script or API exists
  - validation errors are surfaced clearly

### Ticket 13

- Key: `GEOSYN-TBD`
- Title: `Implement event-to-exposure explanation query`
- Type: Story
- Priority: High
- Description:
  Answer the core question: why does this event matter to this customer?
- Acceptance Criteria:
  - service returns matched watchlists and exposure paths
  - output includes criticality and confidence fields
  - endpoint exists for frontend consumption

### Ticket 14

- Key: `GEOSYN-TBD`
- Title: `Add v2 alert center endpoints for frontend transition`
- Type: Story
- Priority: Medium
- Description:
  Expose customer-scoped alerts in a frontend-friendly contract so the UI can transition from legacy dashboard surfaces.
- Acceptance Criteria:
  - list alert endpoint exists
  - alert detail endpoint exists
  - alert evidence endpoint exists

## Suggested Dependencies

- Ticket 1 before Tickets 2-7
- Ticket 2 before Tickets 3, 6, 7
- Ticket 4 before Ticket 6
- Ticket 5 before Tickets 11-13
- Ticket 8 before team-wide adoption of Jira-linked commits

## Commit Mapping Convention

Once Jira tickets exist, map commits like this:

- `GEOSYN-101: establish alembic migration workflow`
- `GEOSYN-102: add canonical v2 event models`
- `GEOSYN-103: backfill legacy clusters into canonical events`
- `GEOSYN-104: add customer and watchlist foundation`
- `GEOSYN-105: dual-write clustering into canonical events`
- `GEOSYN-106: add jira-aware git hooks and commit template`

## Recommendation

Create the Jira tickets in this order:

1. Ticket 1
2. Ticket 2
3. Ticket 3
4. Ticket 4
5. Ticket 6
6. Ticket 7
7. Ticket 8
8. Ticket 9
9. Ticket 10
10. Ticket 5
11. Ticket 11
12. Ticket 12
13. Ticket 13
14. Ticket 14

That ordering matches the engineering path already underway in the repo.
