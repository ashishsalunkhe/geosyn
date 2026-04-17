# GeoSyn 90-Day Execution Plan

## Goal

Reposition GeoSyn around one high-value workflow and build the minimum architecture needed to support credible customer pilots.

## Guiding Objective

By day 90, GeoSyn should be able to run a pilot for one target sector where the product can:

- detect geopolitical events,
- map them to customer-specific exposure,
- rank urgency,
- and show the evidence chain behind every alert.

## Success Criteria

By the end of 90 days, GeoSyn should have:

- One locked ICP and one sector narrative
- One production-ready exposure graph model
- Two differentiated data layers beyond generic public news
- A measurable alert evaluation framework
- One pilot-ready workflow from event to decision

## Workstream 1: Positioning And Commercial Focus

### Days 1-15

- Lock the primary ICP: supply-chain risk / sourcing / resilience teams
- Lock one initial sector: semiconductors or critical minerals
- Rewrite external narrative around exposure-aware intelligence
- Remove broad claims that imply decision automation or proven alpha

### Deliverables

- Updated pitch narrative
- ICP brief
- Pilot offer definition
- Lighthouse scenario shortlist

## Workstream 2: Data And Entity Foundation

### Days 1-30

- Separate high-frequency event data from low-frequency macro anchors
- Add structured source tiers and provenance metadata
- Normalize entities across people, firms, countries, commodities, ports, and facilities
- Add customer watchlist and asset universe ingestion path

### Days 31-60

- Add one exposure-specific data layer:
  shipping/logistics or sanctions/ownership
- Add one business-context layer:
  supplier lists, facilities, or commodity dependency mappings

### Deliverables

- Canonical entity schema
- Source reliability model
- Exposure graph seed tables
- First differentiated data ingestion pipeline

## Workstream 3: Exposure Graph

### Days 15-45

- Design graph model linking event entities to customer-relevant exposures
- Define relationship types:
  located_in, ships_through, owns, depends_on, supplies, exposed_to, substitutes
- Build graph sync pipeline from normalized records

### Days 46-75

- Add customer-scoped graph filtering
- Add top-path explanation:
  why this event matters to this customer
- Add severity scoring based on event intensity plus exposure criticality

### Deliverables

- Exposure graph schema
- Graph construction job
- Customer-specific alert explanation layer

## Workstream 4: Evaluation And Math Integrity

### Days 1-30

- Define evaluation framework:
  precision, recall, median lead time, false-positive rate, analyst acceptance
- Add labeled test scenarios for 3-5 historical events

### Days 31-60

- Replace raw price-level correlation narratives with event-study and abnormal-move baselines
- Separate exploratory analytics from customer-facing claims
- Add confidence bands and explicit uncertainty labels

### Days 61-90

- Establish backtesting harness for alert quality
- Compare system output against naive baselines
- Add benchmark dashboard for internal model review

### Deliverables

- Evaluation spec
- Historical test set
- Baseline comparison framework
- Internal quality dashboard

## Workstream 5: Product Workflow

### Days 30-60

- Redesign main user flow around:
  event -> exposure -> recommendation
- Reduce dashboard sprawl
- Make every alert answer:
  what happened, why it matters, who is exposed, what to do now

### Days 61-90

- Add watchlists by supplier, route, commodity, and geography
- Add escalation states:
  monitor, review, escalate, mitigate
- Add exportable evidence reports for enterprise users

### Deliverables

- Pilot-ready alert center
- Exposure detail view
- Evidence report export
- Action-state workflow

## Weekly Cadence

### Every week

- Review new alerts generated vs accepted
- Review false positives
- Review source coverage gaps
- Review new entity resolution misses
- Review one customer scenario end-to-end

## Team Priority Order

1. Exposure graph and entity normalization
2. Differentiated data ingestion
3. Evaluation framework
4. Product workflow simplification
5. Additional econometric sophistication

## What Not To Do In The Next 90 Days

- Do not expand to five personas
- Do not overinvest in generalized market prediction claims
- Do not treat annual macro indicators as tactical confirmation signals
- Do not add more dashboard surfaces before the core workflow is sharp
- Do not use "causal" language in sales material unless backed by explicit validation

## Day-90 Outcome

At day 90, GeoSyn should be able to demonstrate one compelling story:

> A real geopolitical event was detected, linked to a real customer exposure path, prioritized correctly, and explained clearly enough for a risk or sourcing team to act on it.

If GeoSyn can do that reliably, it will have a much stronger product and company foundation than a broader but less operational intelligence narrative.
