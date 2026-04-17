# Work Done vs Jira Tickets

## Purpose

This ledger maps the work already completed in the repo to Jira tickets and suggests branch and commit naming aligned with the company convention:

`SCRUM-123: short task description`

## Completed Work

### `SCRUM-6`

Scope:

- Alembic scaffolding
- migration foundation
- repo-ready migration flow

Relevant files:

- [backend/alembic.ini](/Users/ashishsalunkhe/My Projects/geosyn/backend/alembic.ini)
- [backend/alembic/env.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/alembic/env.py)
- [backend/alembic/versions/0001_v2_foundation.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/alembic/versions/0001_v2_foundation.py)

Suggested commit:

- `SCRUM-6: establish alembic migration workflow`

### `SCRUM-7`

Scope:

- canonical v2 models
- events, entities, customer, watchlists, exposure foundation

Relevant files:

- [backend/app/models/v2.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/models/v2.py)
- [backend/app/db/base.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/db/base.py)

Suggested commit:

- `SCRUM-7: add canonical v2 event models`

### `SCRUM-8`

Scope:

- legacy cluster backfill into canonical events

Relevant files:

- [backend/scripts/backfill_events_v2.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/scripts/backfill_events_v2.py)

Suggested commit:

- `SCRUM-8: backfill legacy event clusters into canonical events`

### `SCRUM-9`

Scope:

- customer foundation
- demo customer seed
- customer context dependency

Relevant files:

- [backend/app/services/customer_service_v2.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/services/customer_service_v2.py)
- [backend/app/api/deps.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/api/deps.py)
- [backend/scripts/seed_v2_foundation.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/scripts/seed_v2_foundation.py)

Suggested commit:

- `SCRUM-9: add customer and watchlist foundation`

### `SCRUM-10`

Scope:

- exposure link foundation table and model

Relevant files:

- [backend/app/models/v2.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/models/v2.py)

Suggested commit:

- `SCRUM-10: add exposure link foundation`

### `SCRUM-11`

Scope:

- v2 event service
- canonical event read APIs

Relevant files:

- [backend/app/services/event_service_v2.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/services/event_service_v2.py)
- [backend/app/api/endpoints/events.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/api/endpoints/events.py)
- [backend/app/schemas/domain.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/schemas/domain.py)

Suggested commit:

- `SCRUM-11: create v2 event read APIs`

### `SCRUM-12`

Scope:

- clustering dual-write into canonical events

Relevant files:

- [backend/app/services/clustering_service.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/services/clustering_service.py)

Suggested commit:

- `SCRUM-12: dual-write clustering output into canonical events`

### `SCRUM-14`

Scope:

- jira-aware git hooks
- commit template
- setup script

Relevant files:

- [.githooks/prepare-commit-msg](/Users/ashishsalunkhe/My Projects/geosyn/.githooks/prepare-commit-msg)
- [.githooks/commit-msg](/Users/ashishsalunkhe/My Projects/geosyn/.githooks/commit-msg)
- [.gitmessage-jira.txt](/Users/ashishsalunkhe/My Projects/geosyn/.gitmessage-jira.txt)
- [scripts/setup_jira_git_workflow.sh](/Users/ashishsalunkhe/My Projects/geosyn/scripts/setup_jira_git_workflow.sh)

Suggested commit:

- `SCRUM-14: add jira-aware git hooks and commit template`

### `SCRUM-15`

Scope:

- PR template for Jira-linked work

Relevant files:

- [.github/pull_request_template.md](/Users/ashishsalunkhe/My Projects/geosyn/.github/pull_request_template.md)

Suggested commit:

- `SCRUM-15: add pull request template for jira-linked prs`

### `SCRUM-16`

Scope:

- Jira setup guide
- Jira backlog automation

Relevant files:

- [docs/jira_setup.md](/Users/ashishsalunkhe/My Projects/geosyn/docs/jira_setup.md)
- [docs/jira_backlog.md](/Users/ashishsalunkhe/My Projects/geosyn/docs/jira_backlog.md)
- [scripts/create_jira_backlog.py](/Users/ashishsalunkhe/My Projects/geosyn/scripts/create_jira_backlog.py)

Suggested commit:

- `SCRUM-16: document jira and github integration workflow`

## In Progress Work

### `SCRUM-18`

Scope:

- v2 alert models
- customer-scoped alert generation
- alert evidence and action endpoints

### `SCRUM-19`

Scope:

- supplier/facility CSV import
- exposure import endpoint

### `SCRUM-20`

Scope:

- event-to-exposure explanation query
- event exposure endpoint

### `SCRUM-21`

Scope:

- v2 alert center endpoints for frontend transition

## Completed Planning And Strategy Artifacts

These should be ticketed separately from the implementation foundation:

- board memo
- pitch narrative
- 90-day plan
- architecture blueprint, schema proposal, migration plan, implementation tickets
