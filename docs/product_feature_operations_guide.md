# GeoSyn Product Feature And Operations Guide

## Purpose

This document explains what the GeoSyn product does today, how its features map to the frontend and backend, and which API endpoints power each workflow.

It is written from the current codebase, not from aspirational pitch language.

Core product definition:

> GeoSyn is an exposure-aware geopolitical intelligence system that ingests external signals, groups them into events, maps those events to customer-specific exposure, scores urgency, and surfaces explainable alerts.

In simpler terms:

- detect relevant geopolitical or macro events,
- organize them into canonical incidents,
- connect them to suppliers, facilities, ports, routes, commodities, or watchlists,
- surface risk and alerting,
- support analyst review, evaluation, and backtesting.

## Primary Use Cases

### 1. Operational risk monitoring

Track geopolitical events that could disrupt:

- suppliers,
- facilities,
- logistics routes,
- commodities,
- compliance posture,
- regional business operations.

### 2. Exposure-aware alerting

Tell a customer not just that an event happened, but:

- what business object is exposed,
- how severe the risk is,
- what evidence supports it,
- what action should be taken.

### 3. Analyst investigation

Support human review with:

- event summaries,
- timelines,
- linked entities,
- causal graph views,
- evidence trails,
- evaluation labels.

### 4. Market-context interpretation

Provide market-adjacent context such as:

- correlation with selected tickers,
- market narrative shocks,
- macro and geopolitical intelligence briefs.

Important note:

GeoSyn currently supports market explanation workflows, but its strongest current product direction is operational exposure intelligence rather than rigorous stock-move attribution.

## Product Surfaces

The main application shell is implemented in [frontend/app/page.tsx](/Users/ashishsalunkhe/My Projects/geosyn/frontend/app/page.tsx).

### Main navigation

- `Landscape`
- `Intel`
- `Nexus`
- `Groups`
- `Vault`
- `Glossary`

### Supporting surfaces

- left watchlist and filters sidebar
- KPI strip
- search bar for scenario/topic analysis
- right-side market and alert panel

## Screenshot Map

There are currently no committed screenshot image assets in the repository. This doc therefore includes screenshot targets and UI references instead of embedded local image files.

Recommended screenshots to capture for a polished external version of this document:

1. Dashboard overview
   Source UI: [frontend/app/page.tsx](/Users/ashishsalunkhe/My Projects/geosyn/frontend/app/page.tsx)
2. Sidebar watchlist and region/sector filters
   Source UI: [frontend/components/TopicSidebar.tsx](/Users/ashishsalunkhe/My Projects/geosyn/frontend/components/TopicSidebar.tsx)
3. Landscape view
   Source UI: [frontend/components/MarketLandscape.tsx](/Users/ashishsalunkhe/My Projects/geosyn/frontend/components/MarketLandscape.tsx)
4. Event groups view
   Source UI: [frontend/components/ClusterMap.tsx](/Users/ashishsalunkhe/My Projects/geosyn/frontend/components/ClusterMap.tsx)
5. Alert center panel
   Source UI: [frontend/components/AlertPulse.tsx](/Users/ashishsalunkhe/My Projects/geosyn/frontend/components/AlertPulse.tsx)
6. Intelligence brief screen
   Source UI: [frontend/components/IntelligenceBrief.tsx](/Users/ashishsalunkhe/My Projects/geosyn/frontend/components/IntelligenceBrief.tsx)
7. Nexus graph
   Source UI: [frontend/components/CausalNexus.tsx](/Users/ashishsalunkhe/My Projects/geosyn/frontend/components/CausalNexus.tsx)

## Frontend Feature Inventory

### 1. Dashboard shell

Frontend:

- [frontend/app/page.tsx](/Users/ashishsalunkhe/My Projects/geosyn/frontend/app/page.tsx)

What it does:

- loads initial product data,
- controls active navigation tab,
- triggers full sync,
- manages active topic, filters, ticker, and theme.

Key frontend operations:

- load canonical events
- load v2 alerts
- load market correlation
- load tracked scenarios
- load trending scenarios
- load summary KPIs
- load nexus graph
- load intelligence composite

API calls used:

- `GET /api/v1/events/v2`
- `GET /api/v1/alerts/v2`
- `GET /api/v1/markets/correlation/{ticker}`
- `GET /api/v1/scenarios/`
- `GET /api/v1/scenarios/trending`
- `GET /api/v1/scenarios/summary`
- `GET /api/v1/nexus/graph`
- intelligence composite helper currently referenced from frontend API layer

### 2. Topic sidebar

Frontend:

- [frontend/components/TopicSidebar.tsx](/Users/ashishsalunkhe/My Projects/geosyn/frontend/components/TopicSidebar.tsx)

What it does:

- shows tracked scenarios,
- filters by sector and region,
- lets users click a watched scenario to re-analyze it.

Business value:

- acts as the user’s persistent monitoring scope,
- narrows the intelligence surface to relevant sectors and regions.

Primary API dependencies:

- `GET /api/v1/scenarios/`
- `POST /api/v1/scenarios/`
- watchlist management is now also available through the operator workspace

### 3. KPI strip and scenario HUD

Frontend:

- [frontend/components/AnalyticsKPIStrip.tsx](/Users/ashishsalunkhe/My Projects/geosyn/frontend/components/AnalyticsKPIStrip.tsx)
- [frontend/components/ScenarioHUD.tsx](/Users/ashishsalunkhe/My Projects/geosyn/frontend/components/ScenarioHUD.tsx)

What it does:

- summarizes global risk pulse,
- counts tracked scenarios and active alerts,
- gives a compact view of scenario distribution and system activity.

Primary API dependencies:

- `GET /api/v1/scenarios/summary`

### 4. Landscape view

Frontend:

- [frontend/components/MarketLandscape.tsx](/Users/ashishsalunkhe/My Projects/geosyn/frontend/components/MarketLandscape.tsx)

What it does:

- shows active tracked scenarios,
- shows community or simulated discovery scenarios,
- shows exposure-linked alerts and monitored assets or commodities.

Business value:

- provides a portfolio-style overview of active risk scenarios,
- gives an “at a glance” picture of what needs review.

Primary API dependencies:

- `GET /api/v1/scenarios/`
- `GET /api/v1/scenarios/trending`
- `GET /api/v1/alerts/v2`

### 5. Intelligence brief

Frontend:

- [frontend/components/IntelligenceBrief.tsx](/Users/ashishsalunkhe/My Projects/geosyn/frontend/components/IntelligenceBrief.tsx)

What it does:

- generates a topic-level intelligence brief,
- combines timeline, market context, and explanation-oriented content.

Primary API dependencies:

- `GET /api/v1/intelligence/brief?topic=...&ticker=...`

Business value:

- supports analyst research on one topic or scenario,
- gives a condensed narrative view rather than raw event rows.

### 6. Nexus graph

Frontend:

- [frontend/components/CausalNexus.tsx](/Users/ashishsalunkhe/My Projects/geosyn/frontend/components/CausalNexus.tsx)

What it does:

- renders the relationship graph,
- supports node-click exploration,
- can trigger graph synchronization.

Primary API dependencies:

- `GET /api/v1/nexus/graph`
- `POST /api/v1/nexus/sync`

Business value:

- helps analysts understand linked entities and causal neighborhoods,
- provides an explanatory layer beyond flat event lists.

### 7. Event groups view

Frontend:

- [frontend/components/ClusterMap.tsx](/Users/ashishsalunkhe/My Projects/geosyn/frontend/components/ClusterMap.tsx)

What it does:

- lists canonical v2 events,
- shows risk, evidence count, and exposure matches,
- supports a dedicated event review panel,
- expands into event timelines and evaluation labels,
- shows matched watchlists and supporting evidence,
- lets users apply quick evaluation actions.

Primary API dependencies:

- `GET /api/v1/events/v2`
- `GET /api/v1/events/v2/{event_id}`
- `GET /api/v1/events/v2/{event_id}/timeline`
- `GET /api/v1/events/v2/{event_id}/evaluation`
- `POST /api/v1/events/v2/{event_id}/evaluation`

Business value:

- turns raw signals into a manageable event register,
- gives the analyst an explainable canonical event object,
- provides a clearer `event -> exposure -> risk -> action` review workflow.

### 8. Alert center

Frontend:

- [frontend/components/AlertPulse.tsx](/Users/ashishsalunkhe/My Projects/geosyn/frontend/components/AlertPulse.tsx)

What it does:

- shows exposure-aware customer alerts,
- displays risk rationale and top exposure path,
- supports alert workflow actions such as review, monitor, escalation, and dismissal,
- shows alert action history,
- supports status filtering,
- respects configured workflow transitions.

Primary API dependencies:

- `GET /api/v1/alerts/v2`
- `POST /api/v1/alerts/v2/generate`
- `GET /api/v1/alerts/v2/{alert_id}`
- `GET /api/v1/alerts/v2/{alert_id}/evidence`
- `GET /api/v1/alerts/v2/{alert_id}/actions`
- `GET /api/v1/alerts/v2/workflow/config`
- `POST /api/v1/alerts/v2/{alert_id}/actions`

Business value:

- this is the most operationally meaningful product surface,
- it translates event intelligence into customer action.

### 9. Market correlation panel

Frontend:

- [frontend/components/MarketChart.tsx](/Users/ashishsalunkhe/My Projects/geosyn/frontend/components/MarketChart.tsx)

What it does:

- shows ticker-linked market narratives and correlations,
- gives context around selected exchanges or commodities.

Primary API dependencies:

- `GET /api/v1/markets/correlation/{ticker}`
- `POST /api/v1/markets/sync`

### 10. Live feed

Frontend:

- [frontend/components/LiveFeed.tsx](/Users/ashishsalunkhe/My Projects/geosyn/frontend/components/LiveFeed.tsx)

What it does:

- shows a live stream of recent intelligence items and documents.

Primary API dependencies:

- `GET /api/v1/intelligence/live`

### 11. Vault

Frontend:

- [frontend/components/InsightVault.tsx](/Users/ashishsalunkhe/My Projects/geosyn/frontend/components/InsightVault.tsx)

What it now represents:

- operator workspace for customer onboarding and evaluation,
- customer overview and onboarding readiness,
- exposure CSV validation and import,
- watchlist creation and watch item management,
- evaluation metrics and run creation.

Primary API dependencies:

- `GET /api/v1/customers/me`
- `GET /api/v1/watchlists/`
- `POST /api/v1/watchlists/`
- `POST /api/v1/watchlists/{watchlist_id}/items`
- `DELETE /api/v1/watchlists/items/{item_id}`
- `POST /api/v1/ingestion/exposure/csv/validate`
- `POST /api/v1/ingestion/exposure/csv`
- `GET /api/v1/evaluation/metrics`
- `POST /api/v1/evaluation/runs`

### 12. Glossary

Frontend:

- [frontend/components/Glossary.tsx](/Users/ashishsalunkhe/My Projects/geosyn/frontend/components/Glossary.tsx)

What it does:

- provides terminology support and onboarding value.

## Backend API Overview

Primary router:

- [backend/app/api/api.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/api/api.py)

Mounted endpoint groups:

- `customers`
- `documents`
- `events`
- `markets`
- `claims`
- `ingestion`
- `clustering`
- `scenarios`
- `alerts`
- `watchlists`
- `nexus`
- `intelligence`
- `analytics`
- `evaluation`

## Endpoint Catalog

### Documents

Source:

- [backend/app/api/endpoints/documents.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/api/endpoints/documents.py)

#### `GET /api/v1/documents/`

Purpose:

- return raw ingested documents.

Used for:

- document inspection,
- debugging,
- downstream evidence browsing.

#### `GET /api/v1/documents/{id}`

Purpose:

- return one document by database ID.

### Legacy events

Source:

- [backend/app/api/endpoints/events.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/api/endpoints/events.py)

#### `GET /api/v1/events/`

Purpose:

- list legacy clustered events.

#### `GET /api/v1/events/{id}`

Purpose:

- return one legacy event cluster.

Status:

- legacy compatibility surface,
- superseded by v2 event model for current product direction.

### Canonical v2 events

Source:

- [backend/app/api/endpoints/events.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/api/endpoints/events.py)

#### `GET /api/v1/events/v2`

Purpose:

- list canonical events for the current customer scope.

Supported filters:

- `skip`
- `limit`
- `event_type`
- `status`

Returns:

- canonical title,
- status,
- summary,
- document count,
- entity count,
- timeline count,
- risk score,
- exposure matches,
- matched watchlists.

#### `GET /api/v1/events/v2/{event_id}`

Purpose:

- return one detailed canonical event.

Used by:

- event detail expansion,
- deep analyst review,
- customer-specific event inspection.

#### `GET /api/v1/events/v2/{event_id}/exposure`

Purpose:

- explain why this event matters for a particular customer.

Expected output:

- exposure matches,
- event summary,
- customer-scoped explanation,
- risk score.

This is one of the most important endpoints in the product.

#### `GET /api/v1/events/v2/{event_id}/timeline`

Purpose:

- return timeline items for the event.

Used for:

- sequence reconstruction,
- analyst briefing,
- event development review.

#### `GET /api/v1/events/v2/{event_id}/risk`

Purpose:

- return the current customer-scoped risk score for the event.

#### `GET /api/v1/events/v2/{event_id}/evaluation`

Purpose:

- list evaluation labels for the event.

Used for:

- analyst feedback,
- quality review,
- learning loop for backtesting and model validation.

#### `POST /api/v1/events/v2/{event_id}/evaluation`

Purpose:

- add an evaluation label to an event.

Input shape:

```json
{
  "label_type": "event_was_material",
  "label_value": "true",
  "notes": "optional",
  "labeled_by": "optional"
}
```

Used for:

- marking events as material,
- recording usefulness,
- tagging false positives.

### Alerts

Source:

- [backend/app/api/endpoints/alerts.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/api/endpoints/alerts.py)

#### `GET /api/v1/alerts/`

Purpose:

- return legacy proactive alerts.

#### `POST /api/v1/alerts/clear`

Purpose:

- deactivate all legacy alerts.

#### `GET /api/v1/alerts/v2`

Purpose:

- list customer-scoped exposure-aware alerts.

Returns:

- event ID
- alert type
- severity
- status
- headline
- summary
- recommended action
- metadata including risk score and top exposure path

#### `POST /api/v1/alerts/v2/generate`

Purpose:

- generate alerts for the current customer from current event and exposure state.

This is one of the core operational endpoints.

#### `GET /api/v1/alerts/v2/{alert_id}`

Purpose:

- return one alert in detail.

#### `GET /api/v1/alerts/v2/{alert_id}/evidence`

Purpose:

- list supporting evidence for a customer alert.

#### `POST /api/v1/alerts/v2/{alert_id}/actions`

Purpose:

- record workflow actions on an alert.

Input shape:

```json
{
  "action_type": "review",
  "actor_id": "frontend-user",
  "notes": "optional"
}
```

Examples:

- `review`
- `monitor`
- `escalated`
- `dismissed`

#### `GET /api/v1/alerts/v2/{alert_id}/actions`

Purpose:

- return workflow action history for a single alert.

#### `GET /api/v1/alerts/v2/workflow/config`

Purpose:

- return alert status model and allowed transitions.

### Scenarios

Source:

- [backend/app/api/endpoints/scenarios.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/api/endpoints/scenarios.py)

#### `GET /api/v1/scenarios/`

Purpose:

- list tracked scenarios, optionally filtered by region and sector.

Used by:

- watchlist sidebar,
- landscape portfolio view.

#### `POST /api/v1/scenarios/`

Purpose:

- create or follow a new tracked scenario.

Input shape:

```json
{
  "topic": "Red Sea conflict escalation",
  "region": "MENA",
  "sector": "LOGISTICS",
  "description": "optional"
}
```

#### `PATCH /api/v1/scenarios/{scenario_id}`

Purpose:

- update scenario status or risk profile.

#### `POST /api/v1/scenarios/run`

Purpose:

- trigger immediate scenario-specific ingestion.

#### `GET /api/v1/scenarios/trending`

Purpose:

- return a discovery list of trending scenarios.

Status note:

- currently mocked or simulated community priorities.

#### `GET /api/v1/scenarios/summary`

Purpose:

- compute dashboard summary KPIs from tracked scenarios.

### Ingestion

Source:

- [backend/app/api/endpoints/ingestion.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/api/endpoints/ingestion.py)

#### `POST /api/v1/ingestion/trigger`

Purpose:

- manually ingest from live GDELT and RSS providers.

Effect:

- fetches documents,
- normalizes them,
- persists them for clustering and downstream analysis.

#### `POST /api/v1/ingestion/youtube`

Purpose:

- ingest a YouTube video through the YouTube provider.

Input shape:

```json
{
  "url": "https://youtube.com/..."
}
```

#### `POST /api/v1/ingestion/compliance`

Purpose:

- ingest sanctions or compliance-style official feed signals.

Input:

- optional `query` parameter

#### `POST /api/v1/ingestion/exposure/csv`

Purpose:

- import customer-specific exposure mappings from a CSV.

Required CSV columns:

- `source_object_type`
- `source_object_id`
- `relationship_type`
- `target_entity_name`

Supported `source_object_type` values:

- `supplier`
- `facility`
- `port`
- `route`
- `commodity`
- `customer_asset`

This endpoint is critical to the customer-exposure story.

#### `POST /api/v1/ingestion/exposure/csv/validate`

Purpose:

- validate an exposure CSV before import.

Returns:

- row counts,
- preview rows,
- duplicate warnings,
- validation errors.

### Customers

Source:

- [backend/app/api/endpoints/customers.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/api/endpoints/customers.py)

#### `GET /api/v1/customers/me`

Purpose:

- return current customer overview and onboarding readiness.

### Watchlists

Source:

- [backend/app/api/endpoints/watchlists.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/api/endpoints/watchlists.py)

#### `GET /api/v1/watchlists/`

Purpose:

- list watchlists for the current customer including item summaries.

#### `POST /api/v1/watchlists/`

Purpose:

- create a new customer watchlist.

#### `POST /api/v1/watchlists/{watchlist_id}/items`

Purpose:

- add an entity-backed item to a watchlist.

#### `DELETE /api/v1/watchlists/items/{item_id}`

Purpose:

- remove a watchlist item.

### Clustering

Source:

- [backend/app/api/endpoints/clustering.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/api/endpoints/clustering.py)

#### `POST /api/v1/clustering/trigger`

Purpose:

- manually trigger document clustering into events.

Effect:

- updates clustered events,
- supports downstream event and alert generation.

### Markets

Source:

- [backend/app/api/endpoints/markets.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/api/endpoints/markets.py)

#### `POST /api/v1/markets/sync`

Purpose:

- sync market data into the database.

#### `GET /api/v1/markets/correlation/{ticker}`

Purpose:

- return market time series correlated with geopolitical event shocks.

Used by:

- market chart panel,
- market-adjacent narrative exploration.

### Nexus

Source:

- [backend/app/api/endpoints/nexus.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/api/endpoints/nexus.py)

#### `GET /api/v1/nexus/graph`

Purpose:

- return the graph payload for the relationship or causal visualization.

#### `POST /api/v1/nexus/sync`

Purpose:

- synchronize the knowledge graph.

### Intelligence

Source:

- [backend/app/api/endpoints/intelligence.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/api/endpoints/intelligence.py)

#### `GET /api/v1/intelligence/brief`

Purpose:

- return a topic-specific intelligence brief.

Query parameters:

- `topic`
- optional `ticker`

Output intent:

- timeline
- causal chain
- market correlation
- narrative summary

#### `GET /api/v1/intelligence/live`

Purpose:

- return a near-real-time feed of recent matching documents.

Query parameters:

- `query`
- `limit`

#### `GET /api/v1/intelligence/explain/{alert_id}`

Purpose:

- explain a specific legacy alert using causal evidence.

### Claims

Source:

- [backend/app/api/endpoints/claims.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/api/endpoints/claims.py)

#### `GET /api/v1/claims/`

Purpose:

- return extracted claims.

#### `POST /api/v1/claims/extract/{doc_id}`

Purpose:

- extract claims from one document.

#### `POST /api/v1/claims/verify/event/{event_id}`

Purpose:

- verify claims associated with an event cluster.

### Analytics

Source:

- [backend/app/api/endpoints/analytics.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/api/endpoints/analytics.py)

#### `GET /api/v1/analytics/trends`

Purpose:

- return archived intelligence trends such as:
  top topics,
  confidence trend,
  thematic dimensions,
  geo points.

#### `GET /api/v1/analytics/topic/{topic}`

Purpose:

- return historical intelligence journey for one topic.

### Evaluation

Source:

- [backend/app/api/endpoints/evaluation.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/api/endpoints/evaluation.py)

#### `GET /api/v1/evaluation/metrics`

Purpose:

- compute aggregate evaluation metrics, optionally customer scoped.

Used for:

- system quality measurement,
- model feedback loops,
- alert precision and usefulness tracking.

#### `GET /api/v1/evaluation/runs`

Purpose:

- list backtest or evaluation runs.

#### `POST /api/v1/evaluation/runs`

Purpose:

- create a new backtest run.

Input shape:

```json
{
  "run_name": "April baseline",
  "include_customer_scope": true
}
```

## End-To-End Product Operations

### Operation 1. Ingest external signals

What happens:

1. GeoSyn ingests news, RSS, compliance, or video-derived content.
2. Documents are normalized and stored.
3. Raw content becomes available for clustering and analysis.

Primary endpoints:

- `POST /api/v1/ingestion/trigger`
- `POST /api/v1/ingestion/youtube`
- `POST /api/v1/ingestion/compliance`

Backend services involved:

- [backend/app/services/ingestion_service.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/services/ingestion_service.py)

### Operation 2. Cluster documents into events

What happens:

1. Ingested documents are grouped into event clusters.
2. Canonical events are created or updated.
3. Event summaries and linked entities become available.

Primary endpoint:

- `POST /api/v1/clustering/trigger`

Backend services involved:

- [backend/app/services/clustering_service.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/services/clustering_service.py)
- [backend/app/services/event_service_v2.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/services/event_service_v2.py)

### Operation 3. Import customer exposure

What happens:

1. Customer uploads exposure CSV.
2. GeoSyn creates exposure links across suppliers, facilities, ports, routes, commodities, or assets.
3. Future events can be mapped against customer-specific exposure.

Primary endpoint:

- `POST /api/v1/ingestion/exposure/csv`

Backend services involved:

- [backend/app/services/exposure_import_service.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/services/exposure_import_service.py)

### Operation 4. Explain event exposure

What happens:

1. Analyst opens a canonical event.
2. GeoSyn explains which customer objects are exposed.
3. Risk score and reasoning are attached.

Primary endpoints:

- `GET /api/v1/events/v2/{event_id}`
- `GET /api/v1/events/v2/{event_id}/exposure`
- `GET /api/v1/events/v2/{event_id}/risk`

### Operation 5. Generate customer alerts

What happens:

1. GeoSyn scans current events against customer exposure.
2. It creates or refreshes alerts.
3. Each alert contains severity, summary, recommended action, and metadata.

Primary endpoints:

- `POST /api/v1/alerts/v2/generate`
- `GET /api/v1/alerts/v2`
- `GET /api/v1/alerts/v2/{alert_id}/evidence`

Backend services involved:

- [backend/app/services/alert_service_v2.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/services/alert_service_v2.py)

### Operation 6. Human review and evaluation

What happens:

1. Analyst reviews event or alert.
2. Analyst records whether the event was material, useful, or a false positive.
3. Evaluation data feeds quality measurement and backtesting.

Primary endpoints:

- `POST /api/v1/events/v2/{event_id}/evaluation`
- `GET /api/v1/events/v2/{event_id}/evaluation`
- `GET /api/v1/evaluation/metrics`
- `GET /api/v1/evaluation/runs`
- `POST /api/v1/evaluation/runs`

### Operation 7. Topic-based intelligence brief

What happens:

1. User searches a topic.
2. GeoSyn generates a narrative-style intelligence brief.
3. Brief can include timeline and market context.

Primary endpoint:

- `GET /api/v1/intelligence/brief`

### Operation 8. Graph exploration

What happens:

1. User opens the Nexus screen.
2. GeoSyn returns graph nodes and links.
3. User explores relationships and syncs graph updates if needed.

Primary endpoints:

- `GET /api/v1/nexus/graph`
- `POST /api/v1/nexus/sync`

## What The Product Actually Offers Today

### Strongest offered capability

The strongest product story in the current codebase is:

> GeoSyn helps teams monitor geopolitical events and convert them into exposure-aware operational alerts.

That means the product can already offer:

- event ingestion,
- event clustering,
- customer-scoped event views,
- exposure matching,
- risk scoring,
- customer alerts,
- evidence and rationale,
- analyst evaluation hooks.

### Secondary offered capability

The product also offers analyst and research support through:

- intelligence briefs,
- live document feed,
- graph exploration,
- claims extraction,
- trend analytics,
- market correlation panels.

### Areas that exist but are less mature

- stock-move explanation as a rigorous causal product
- portfolio-grade trading signal generation
- polished external reporting workflows
- deeply differentiated proprietary data integrations

## Customer Journey Example

Example customer:

- a semiconductor operations or supply-chain risk team

Example flow:

1. The customer imports suppliers, routes, ports, and watched commodities through `POST /api/v1/ingestion/exposure/csv`.
2. GeoSyn ingests global news and compliance feeds.
3. GeoSyn clusters related reports into a canonical event such as export control escalation.
4. GeoSyn links the event to a supplier and shipping route in the customer’s exposure graph.
5. GeoSyn computes a risk score and generates an alert through `POST /api/v1/alerts/v2/generate`.
6. The analyst opens the event in the `Groups` view, checks timeline and evidence, then reviews the alert in the alert panel.
7. The analyst marks the event useful or material through `POST /api/v1/events/v2/{event_id}/evaluation`.

## Product Gaps And Clarity Notes

The codebase is functional, but the product narrative is still split across three identities:

- geopolitical intelligence dashboard,
- market and macro analysis tool,
- exposure-aware operational risk platform.

The clearest and most defensible product is the third one.

That means this document should be read with one main interpretation:

GeoSyn is best understood as an operational geopolitical risk system with analyst tooling attached, not as a pure market terminal or pure news dashboard.

## Recommended Next Documentation Artifact

After this guide, the best follow-up document would be:

`geoSyn_operator_playbook.md`

Suggested contents:

- how a customer onboards,
- how exposure CSVs should be structured,
- how an analyst triages alerts,
- what each alert status means,
- what “review”, “monitor”, “escalate”, and “dismiss” mean operationally.
