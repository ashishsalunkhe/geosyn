# GeoSyn Initial Implementation Tickets

## Purpose

This document breaks the first implementation phase into concrete engineering tickets. These tickets are ordered to create momentum while minimizing schema churn and frontend breakage.

## Epic 1: Migration Infrastructure

### Ticket 1.1

**Title:** Introduce Alembic and baseline the current schema

**Goal:**
Move away from `create_all()` and ad hoc migration scripts for long-term schema evolution.

**Tasks:**

- Add Alembic to backend dependencies
- Initialize migration environment
- Generate baseline migration from current SQLAlchemy metadata
- Document local migration commands

**Acceptance Criteria:**

- Engineers can run `alembic upgrade head`
- Baseline schema matches current local DB tables
- No runtime regressions for existing local startup

### Ticket 1.2

**Title:** Add PostgreSQL local development configuration

**Goal:**
Support local PostgreSQL without breaking SQLite fallback.

**Tasks:**

- Add documented `.env` example for PostgreSQL
- Verify SQLAlchemy URL generation for Postgres
- Add README instructions for local Postgres boot

**Acceptance Criteria:**

- App can boot against PostgreSQL locally
- Existing SQLite workflow still works

## Epic 2: Canonical Events

### Ticket 2.1

**Title:** Add v2 event models and migrations

**Goal:**
Create `events`, `event_evidence`, and `event_entities` tables.

**Tasks:**

- Add SQLAlchemy models
- Add migration
- Add enums/constants for event status
- Add indexes for `status`, `first_seen_at`, `last_seen_at`

**Acceptance Criteria:**

- New tables exist in PostgreSQL
- ORM models load cleanly
- No legacy models broken

### Ticket 2.2

**Title:** Backfill `event_clusters` into `events`

**Goal:**
Seed canonical events from existing cluster data.

**Tasks:**

- Write one-off backfill script
- Create legacy cluster ID to event ID mapping
- Populate `event_evidence` from linked documents

**Acceptance Criteria:**

- Every legacy cluster becomes a canonical event
- Backfill script is idempotent
- Mapping audit report is produced

### Ticket 2.3

**Title:** Dual-write clustering output into v2 events

**Goal:**
Have the clustering pipeline populate `events` while preserving legacy behavior.

**Tasks:**

- Add event service abstraction
- Update clustering service to call v2 event writer
- Preserve current `event_cluster_id` links during transition

**Acceptance Criteria:**

- New clustered evidence appears in v2 tables
- Existing endpoints still function

## Epic 3: Customers And Watchlists

### Ticket 3.1

**Title:** Add customer, watchlist, and watchlist item tables

**Goal:**
Introduce customer scope into the model.

**Tasks:**

- Add SQLAlchemy models and migration
- Add default demo customer seed
- Add watchlist CRUD service

**Acceptance Criteria:**

- One seeded customer exists in local environments
- Watchlists can be created and queried

### Ticket 3.2

**Title:** Add customer context to API dependency layer

**Goal:**
Make services customer-aware without requiring full auth implementation yet.

**Tasks:**

- Add request-level customer resolver
- Default to demo customer if not specified
- Thread `customer_id` through new v2 services

**Acceptance Criteria:**

- V2 services operate on customer-scoped data
- Existing endpoints continue working

## Epic 4: Exposure Graph Foundation

### Ticket 4.1

**Title:** Add exposure domain tables

**Goal:**
Create `suppliers`, `facilities`, `customer_assets`, `ports`, `routes`, `commodities`, and `exposure_links`.

**Tasks:**

- Add SQLAlchemy models
- Add migrations
- Define relationship type constants
- Add indexes on customer and object identifiers

**Acceptance Criteria:**

- All exposure tables exist
- Tables support CRUD operations

### Ticket 4.2

**Title:** Build CSV import path for customer exposure data

**Goal:**
Enable pilot customers to upload supplier/facility exposure data quickly.

**Tasks:**

- Define CSV templates
- Add backend import parser
- Validate duplicates and bad rows
- Store import summary logs

**Acceptance Criteria:**

- Users can import suppliers and facilities from CSV
- Validation errors are understandable
- Successful imports populate exposure tables

### Ticket 4.3

**Title:** Implement event-to-exposure path query

**Goal:**
Answer the core question: why does this event matter to this customer?

**Tasks:**

- Resolve event entities
- Join to `exposure_links`
- Rank reachable customer exposures by criticality and confidence
- Return structured explanation paths

**Acceptance Criteria:**

- Service returns top exposure paths for a given `event_id` and `customer_id`
- Response includes path explanation and scores

## Epic 5: Customer-Scoped Alerts

### Ticket 5.1

**Title:** Add v2 alert models and workflow tables

**Goal:**
Create `alerts`, `alert_evidence`, and `alert_actions`.

**Tasks:**

- Add models and migrations
- Define severity and status enums
- Add audit timestamps

**Acceptance Criteria:**

- V2 alert tables are available
- Alerts can be created independently of legacy alert system

### Ticket 5.2

**Title:** Build v2 alert generation service

**Goal:**
Generate alerts from `events + exposure_links + risk scores`.

**Tasks:**

- Add alert candidate generator
- Deduplicate repeated event/customer combinations
- Attach top evidence documents

**Acceptance Criteria:**

- Alerts are generated only when customer exposure exists
- Alert records include evidence links

### Ticket 5.3

**Title:** Add v2 alert API endpoints

**Goal:**
Expose customer-scoped alerts to the frontend.

**Tasks:**

- Add `GET /customers/{id}/alerts`
- Add `GET /alerts/{id}`
- Add `GET /alerts/{id}/evidence`
- Add `POST /alerts/{id}/actions`

**Acceptance Criteria:**

- Endpoints return structured alert objects
- Evidence and workflow actions are queryable

## Epic 6: Evaluation

### Ticket 6.1

**Title:** Add evaluation schema and backtest run tables

**Goal:**
Create `risk_scores`, `evaluation_labels`, and `backtest_runs`.

**Tasks:**

- Add models and migrations
- Add JSON storage for component scores and run config
- Add indexes on `event_id`, `customer_id`

**Acceptance Criteria:**

- Evaluation tables exist and are writable

### Ticket 6.2

**Title:** Build historical scenario labeling harness

**Goal:**
Create a simple internal workflow for labeling historical event materiality and alert quality.

**Tasks:**

- Seed first 10-20 historical scenarios
- Add CLI or admin script for labels
- Define label types and scoring conventions

**Acceptance Criteria:**

- Team can label historical events reproducibly
- Labels are persisted in v2 evaluation tables

### Ticket 6.3

**Title:** Build first alert-quality report

**Goal:**
Produce a repeatable internal scorecard.

**Tasks:**

- Aggregate precision-like metrics
- Measure median lead time where labels exist
- Emit markdown or JSON report

**Acceptance Criteria:**

- One command generates an internal quality report

## Epic 7: Frontend Transition

### Ticket 7.1

**Title:** Add event detail page contract for exposure-aware events

**Goal:**
Shift the UI from cluster-oriented detail to event-oriented detail.

**Tasks:**

- Define frontend TypeScript interfaces for v2 events
- Add exposure path section
- Add evidence list section

**Acceptance Criteria:**

- Event detail page can render v2 event payload

### Ticket 7.2

**Title:** Add exposure-aware alert center

**Goal:**
Make alerts the core workflow object.

**Tasks:**

- Add alert list view
- Add severity and status filters
- Add "why this matters" preview

**Acceptance Criteria:**

- Analysts can review alerts and understand exposure relevance quickly

## Recommended Execution Order

1. Ticket 1.1
2. Ticket 1.2
3. Ticket 2.1
4. Ticket 2.2
5. Ticket 3.1
6. Ticket 3.2
7. Ticket 4.1
8. Ticket 4.2
9. Ticket 4.3
10. Ticket 5.1
11. Ticket 5.2
12. Ticket 5.3
13. Ticket 6.1
14. Ticket 6.2
15. Ticket 6.3
16. Ticket 7.1
17. Ticket 7.2

## First Build Slice

If we want the highest leverage first slice, it is:

- Alembic baseline
- canonical `events`
- `customers` and `watchlists`
- `exposure_links`
- event-to-exposure path query

That slice creates the backbone of the new product without forcing a full rewrite.
