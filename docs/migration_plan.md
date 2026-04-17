# GeoSyn Data Migration Plan

## Objective

Migrate GeoSyn from the current local SQLite-first schema into a PostgreSQL-oriented event and exposure model without breaking current ingestion, UI APIs, or demo workflows.

## Constraints

- The current system boots with `Base.metadata.create_all()` during app startup ([backend/app/main.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/main.py:54)).
- The DB layer falls back to SQLite for zero-config local usage ([backend/app/core/config.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/core/config.py:24)).
- Current migrations are ad hoc and additive, not revisioned ([backend/migrate_db.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/migrate_db.py:1)).
- Existing services assume current table names and model semantics.

Because of that, the migration should be phased, additive, and reversible.

## Migration Strategy

Use a **parallel schema migration** rather than a destructive rewrite.

That means:

- add new v2 tables alongside existing ones,
- dual-write from selected services where needed,
- backfill historical data,
- switch reads over endpoint by endpoint,
- then retire legacy tables only after the new paths stabilize.

## Phases

## Phase 0: Migration Infrastructure

### Goals

- Stop relying on `create_all()` and one-off `ALTER TABLE` scripts for production evolution
- Introduce revisioned migrations

### Actions

- Add Alembic
- Freeze a baseline migration from the current schema
- Add environment-specific DB URLs for PostgreSQL and local SQLite
- Define naming conventions for constraints and indexes

### Deliverables

- `alembic.ini`
- migration environment
- baseline revision
- documented local migration workflow

## Phase 1: Add Canonical Event Tables

### Goals

- Introduce `events`, `event_evidence`, and `event_entities`
- Preserve existing `event_clusters` while new services are built

### Actions

- Create new `events` table
- Create backfill script:
  `event_clusters -> events`
- Create mapping table from legacy cluster IDs to new event IDs
- Update clustering service to optionally populate v2 events

### Read/Write Behavior

- Legacy UI continues reading old cluster-backed views
- New services can start reading `events`

### Rollback

- Disable dual-write and continue serving legacy cluster data

## Phase 2: Add Customer And Watchlist Domain

### Goals

- Introduce customer scope without rewriting the entire app

### Actions

- Create `customers`, `watchlists`, `watchlist_items`
- Seed one internal/demo customer
- Add a customer context abstraction in the API layer
- Keep unauthenticated single-tenant mode working by defaulting to demo customer

### Deliverables

- base customer seed
- customer-scoped watchlist service
- API support for `customer_id`

## Phase 3: Add Exposure Graph Tables

### Goals

- Introduce the missing exposure model

### Actions

- Create `suppliers`, `facilities`, `customer_assets`, `ports`, `routes`, `commodities`, `exposure_links`
- Add CSV import path for customer exposure data
- Build exposure graph sync job from normalized records
- Add first explanation query:
  event -> entities -> exposure links -> customer-relevant objects

### Deliverables

- exposure import service
- graph edge builder
- first exposure query service

## Phase 4: Add Customer-Scoped Alerts

### Goals

- Move from generic system alerts to customer-relevant alerts

### Actions

- Create new `alerts`, `alert_evidence`, `alert_actions`
- Keep legacy alert table alive temporarily
- Add alert generation logic based on `events + exposure_links + risk_scores`
- Update frontend endpoints to support new alert object contract

### Rollout

- Run both alert systems during transition
- Compare alert counts and analyst acceptance before deprecating legacy alerts

## Phase 5: Add Evaluation And Backtesting

### Goals

- Make the system measurable

### Actions

- Create `risk_scores`, `evaluation_labels`, `backtest_runs`
- Add historical labeling workflow
- Add evaluation scripts and dashboards

### Deliverables

- evaluation schema
- baseline metrics harness
- first internal quality report

## Table-Level Mapping

## Legacy -> V2 Mapping

### `sources` -> `ingest_sources`

- mostly direct carryover
- add tiering, licensing, and richer source metadata

### `documents` -> `evidence_documents`

- direct conceptual migration
- rename and enrich with provenance fields

### `document_entity_association` -> `document_entities`

- preserve the relationship, add mention metadata and confidence

### `event_clusters` -> `events`

- replace cluster-as-event with canonical event representation

### `claims`

- keep only if the claim verification feature remains core
- otherwise freeze and deprecate

### `market_series` and `market_points`

- preserve
- add richer observation structure later if needed

### `alerts`

- do not mutate in place
- create a new customer-scoped alert model and migrate reads gradually

### `causal_nodes` and `causal_edges`

- treat as legacy experimental graph layer
- do not build the new product on top of them
- replace with `entities`, `entity_relationships`, and `exposure_links`

### `strategic_scenarios`

- keep as a tactical layer during transition
- later merge with `events` if the semantics truly overlap

### `intelligence_archive`

- keep as cache/support table
- low migration priority

## Application Refactor Order

### 1. Persistence layer

- introduce SQLAlchemy models for v2 tables
- keep legacy models during transition

### 2. Service layer

- add v2 services rather than mutating all legacy services in place
- example:
  `event_service_v2`, `exposure_service_v2`, `alert_service_v2`

### 3. Endpoint layer

- add parallel v2 endpoints
- keep legacy endpoints until frontend is migrated

### 4. Frontend

- migrate alert center and event detail first
- postpone full dashboard rewrite until v2 APIs stabilize

## Data Backfill Plan

## Backfill 1: Events

Source:

- `event_clusters`
- cluster-linked `documents`

Output:

- `events`
- `event_evidence`

Logic:

- one cluster becomes one event seed
- cluster `created_at` -> `first_seen_at`
- latest linked document timestamp -> `last_seen_at`
- cluster title/description become provisional event fields

## Backfill 2: Entities

Source:

- current `entities`
- document links

Output:

- `entities`
- `entity_aliases`
- `document_entities`

Logic:

- preserve existing IDs only if useful
- otherwise assign new UUIDs and maintain a legacy mapping table

## Backfill 3: Alerts

Source:

- legacy `alerts`

Output:

- optional carry-forward into new `alerts`

Logic:

- only migrate alerts that can be associated with an event or customer context
- otherwise keep as historical legacy data

## Operational Rollout Plan

### Local development

- continue to support SQLite for current dev convenience
- run PostgreSQL locally for v2 development paths

### Staging

- make PostgreSQL the default
- run dual-write where supported
- validate parity between legacy and v2 outputs

### Production / Pilot

- switch event and alert reads to v2 endpoints first
- keep legacy intelligence brief cache available

## Risks And Mitigations

### Risk: Service breakage due to mixed schemas

Mitigation:

- keep v2 behind new services and endpoints
- avoid renaming or dropping legacy tables early

### Risk: Data drift between legacy and v2

Mitigation:

- add migration audit logs
- add record-count parity checks
- add sample-level validation scripts

### Risk: Overbuilding the graph before the workflow is proven

Mitigation:

- implement only the minimum viable exposure edges needed for the first sector

### Risk: PostgreSQL migration slows feature work

Mitigation:

- keep local-first mode for UI work
- isolate DB migration work into focused tickets

## Definition Of Done Per Phase

### Phase 1 done when

- canonical events exist
- clustering can populate them
- historical events are backfilled

### Phase 2 done when

- app can scope data to a customer
- watchlists exist in v2 tables

### Phase 3 done when

- customer exposure records import successfully
- event-to-exposure explanation query returns valid paths

### Phase 4 done when

- customer-scoped alerts are generated and visible in UI
- alert evidence is attached

### Phase 5 done when

- internal quality metrics are produced on every backtest run

## Immediate Recommendation

Start with:

1. Alembic setup
2. `events` and related tables
3. `customers` and `watchlists`
4. `exposure_links`

That path creates the minimum scaffolding needed to begin real product transformation without destabilizing the current app.
