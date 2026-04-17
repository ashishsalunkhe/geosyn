# GeoSyn Board Memo

## Executive Summary

GeoSyn is building a geopolitical intelligence platform that ingests public news and macro signals, clusters events, and attempts to translate those signals into market and operational relevance. The opportunity is real: executives, risk teams, and operators do not have good tooling for turning geopolitical noise into structured decisions. The current product direction is promising, but the company should narrow its wedge and strengthen its evidence layer before expanding go-to-market.

The central recommendation is to focus GeoSyn on a single high-value workflow:

> Map geopolitical events to customer-specific operational exposure, with evidence, timing, and escalation guidance.

That wedge is more defensible than a broad "intelligence for everyone" narrative and easier to validate than a trading-alpha claim.

## Current Position

GeoSyn already has meaningful product scaffolding:

- A FastAPI backend with continuous ingestion and background synchronization ([backend/app/main.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/main.py:11)).
- Connectors for GDELT, RSS, FRED, IMF, World Bank, Yahoo Finance, Event Registry, OSINT, and YouTube sources.
- Event clustering, market synchronization, alerting, and a causal graph abstraction.
- A Next.js frontend with intelligence, nexus, map, watchlist, and KPI surfaces.

This is more than a pitch. It is a functioning early intelligence system.

## What Is Strong

- The team is attacking an important problem with good intuition around user experience.
- The product architecture already separates ingestion, analysis, market linkage, and UI well enough to evolve cleanly.
- The system is naturally positioned at the intersection of geopolitical monitoring, supply-chain resilience, and strategic risk.
- The current implementation can become a strong internal platform for experimentation and customer pilots.

## What Is Missing

### 1. A single buyer and a single job-to-be-done

The current narrative spans hedge funds, corporate risk, analysts, policy researchers, and founders. Those are different products, different evidence standards, and different sales motions. A narrow ICP is required.

### 2. An exposure graph

GeoSyn can describe events, but it does not yet robustly answer:

- Which facility is exposed?
- Which supplier tier is exposed?
- Which route, port, or commodity is exposed?
- Which business unit or program is exposed?
- What should the user do next?

Without this layer, the platform is informative but not operational.

### 3. Stronger proprietary or workflow-specific data

Public news and public macro data are necessary but not sufficient for a moat. The strongest missing data layers are:

- Supplier and facility data
- Shipping and logistics data
- Sanctions, watchlists, and ownership data
- Trade/customs or import-export proxies
- Portfolio, watchlist, or internal exposure inputs from customers

### 4. Decision-grade validation

GeoSyn currently presents mathematically flavored outputs, but the proof layer is still early.

Examples from the current system:

- The GPR layer is a local keyword-hit ratio, not a faithful implementation of the published Caldara-Iacoviello methodology ([backend/app/services/gpr_index_service.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/services/gpr_index_service.py:25)).
- The correlation layer uses short-window Pearson correlations ([backend/app/services/correlation_service.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/services/correlation_service.py:17)).
- The Granger layer is prototype-grade and should not yet carry marketing claims of institutional econometric rigor ([backend/app/services/causality_engine.py](/Users/ashishsalunkhe/My Projects/geosyn/backend/app/services/causality_engine.py:17)).

The company needs benchmarked, out-of-sample evaluation before making strong predictive claims.

## Recommended Strategic Wedge

### Primary ICP

Corporate supply-chain risk, strategic sourcing, and operational resilience teams in:

- Semiconductors
- Energy
- Defense and aerospace
- Automotive and EV battery
- Critical minerals
- Data center and digital infrastructure

### Core Product Promise

> GeoSyn translates geopolitical events into exposure-aware operational intelligence.

That means:

- detect the event,
- resolve the entities and places involved,
- map the event to customer exposure,
- score urgency,
- explain the evidence,
- recommend escalation paths.

## Why This Wedge Wins

- Easier to demonstrate ROI than trading-alpha products.
- Better fit for public + proprietary exposure data.
- Higher tolerance for human-in-the-loop workflows.
- Strong alignment with enterprise procurement, compliance, and resilience budgets.
- Clearer differentiation from generic alerting and research tools.

## Product Risks

### Scientific risk

Overclaiming causality or predictive precision before the system has robust validation.

### Product risk

Becoming a beautiful intelligence dashboard that does not change operational decisions.

### Go-to-market risk

Trying to serve too many personas and ending up with no clear champion.

### Data risk

Using low-latency signals and low-frequency macro data in the same narrative without enough separation of timing, lag, and revision logic.

## 12-Month Board-Level Priorities

1. Lock one ICP and one core workflow.
2. Build the exposure graph and customer-specific watchlist model.
3. Add at least two differentiated data layers beyond public news.
4. Establish an evaluation framework with precision, lead time, and business-impact metrics.
5. Convert the current platform into 2-3 lighthouse pilots in one sector.

## Metrics That Matter

For the next 12 months, avoid vanity metrics like article counts or number of charts. Focus on:

- Alert precision at top-N
- Median lead time before customer-recognized disruption
- Share of alerts tied to explicit customer exposure
- Analyst-hours saved per week
- Pilot-to-paid conversion
- Time from event detection to user action

## Board Ask

The company should explicitly support a focused repositioning:

- Narrow the ICP
- Reduce broad predictive language
- Invest in exposure mapping and evaluation
- Prioritize customer workflow depth over breadth

If GeoSyn does that, it has a credible path to become a serious operational intelligence product rather than a broad but diffuse geopolitical dashboard.
