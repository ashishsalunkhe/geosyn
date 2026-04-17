-- GeoSyn v2 PostgreSQL schema skeleton
-- This is an implementation-oriented starting point for the new event and
-- exposure-aware data model. It is intentionally additive and designed for a
-- phased rollout alongside the current legacy schema.

create extension if not exists "pgcrypto";

-- =========================================================
-- ENUMS
-- =========================================================

do $$
begin
    if not exists (select 1 from pg_type where typname = 'entity_type_enum') then
        create type entity_type_enum as enum (
            'company',
            'government',
            'person',
            'location',
            'port',
            'route',
            'facility',
            'commodity',
            'vessel',
            'financial_asset',
            'regulator'
        );
    end if;

    if not exists (select 1 from pg_type where typname = 'event_status_enum') then
        create type event_status_enum as enum (
            'emerging',
            'active',
            'critical',
            'resolving',
            'stabilized'
        );
    end if;

    if not exists (select 1 from pg_type where typname = 'alert_status_enum') then
        create type alert_status_enum as enum (
            'new',
            'monitor',
            'review',
            'escalated',
            'mitigated',
            'dismissed'
        );
    end if;

    if not exists (select 1 from pg_type where typname = 'alert_severity_enum') then
        create type alert_severity_enum as enum (
            'low',
            'medium',
            'high',
            'critical'
        );
    end if;
end $$;

-- =========================================================
-- EVIDENCE & SOURCES
-- =========================================================

create table if not exists ingest_sources (
    id uuid primary key default gen_random_uuid(),
    name text not null unique,
    source_type text not null,
    source_tier text,
    base_url text,
    country_code text,
    language_code text,
    reliability_score numeric(5,4),
    license_class text,
    is_active boolean not null default true,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists evidence_documents (
    id uuid primary key default gen_random_uuid(),
    source_id uuid not null references ingest_sources(id),
    external_id text not null,
    canonical_url text,
    title text,
    body_text text,
    summary_text text,
    language_code text,
    country_code text,
    published_at timestamptz,
    event_time timestamptz,
    ingested_at timestamptz not null default now(),
    content_hash text,
    raw_payload_ref text,
    source_confidence numeric(5,4),
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (source_id, external_id)
);

create index if not exists idx_evidence_documents_published_at
    on evidence_documents (published_at desc);

create index if not exists idx_evidence_documents_content_hash
    on evidence_documents (content_hash);

create table if not exists document_fragments (
    id uuid primary key default gen_random_uuid(),
    document_id uuid not null references evidence_documents(id) on delete cascade,
    fragment_type text not null,
    fragment_text text not null,
    start_offset integer,
    end_offset integer,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

-- =========================================================
-- ENTITIES
-- =========================================================

create table if not exists entities_v2 (
    id uuid primary key default gen_random_uuid(),
    entity_type entity_type_enum not null,
    canonical_name text not null,
    display_name text,
    country_code text,
    region_code text,
    external_refs jsonb not null default '{}'::jsonb,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists idx_entities_v2_canonical_name
    on entities_v2 (canonical_name);

create table if not exists entity_aliases (
    id uuid primary key default gen_random_uuid(),
    entity_id uuid not null references entities_v2(id) on delete cascade,
    alias text not null,
    alias_type text,
    language_code text,
    created_at timestamptz not null default now()
);

create index if not exists idx_entity_aliases_alias
    on entity_aliases (alias);

create table if not exists document_entities_v2 (
    id uuid primary key default gen_random_uuid(),
    document_id uuid not null references evidence_documents(id) on delete cascade,
    entity_id uuid not null references entities_v2(id) on delete cascade,
    mention_text text,
    mention_role text,
    confidence_score numeric(5,4),
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create index if not exists idx_document_entities_v2_doc_entity
    on document_entities_v2 (document_id, entity_id);

create table if not exists entity_relationships (
    id uuid primary key default gen_random_uuid(),
    source_entity_id uuid not null references entities_v2(id),
    target_entity_id uuid not null references entities_v2(id),
    relationship_type text not null,
    weight numeric(8,4),
    valid_from timestamptz,
    valid_to timestamptz,
    source_document_id uuid references evidence_documents(id),
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create index if not exists idx_entity_relationships_source
    on entity_relationships (source_entity_id, relationship_type);

create index if not exists idx_entity_relationships_target
    on entity_relationships (target_entity_id, relationship_type);

-- =========================================================
-- EVENTS
-- =========================================================

create table if not exists events (
    id uuid primary key default gen_random_uuid(),
    canonical_title text not null,
    event_type text,
    event_subtype text,
    status event_status_enum not null default 'emerging',
    first_seen_at timestamptz not null,
    last_seen_at timestamptz not null,
    primary_geo_entity_id uuid references entities_v2(id),
    severity_score numeric(6,4),
    confidence_score numeric(6,4),
    summary_text text,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists idx_events_status_last_seen
    on events (status, last_seen_at desc);

create table if not exists event_evidence (
    id uuid primary key default gen_random_uuid(),
    event_id uuid not null references events(id) on delete cascade,
    document_id uuid not null references evidence_documents(id) on delete cascade,
    contribution_type text,
    relevance_score numeric(6,4),
    is_primary boolean not null default false,
    created_at timestamptz not null default now(),
    unique (event_id, document_id)
);

create index if not exists idx_event_evidence_event_relevance
    on event_evidence (event_id, relevance_score desc);

create table if not exists event_entities (
    id uuid primary key default gen_random_uuid(),
    event_id uuid not null references events(id) on delete cascade,
    entity_id uuid not null references entities_v2(id) on delete cascade,
    event_role text,
    confidence_score numeric(6,4),
    is_primary boolean not null default false,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    unique (event_id, entity_id, event_role)
);

create table if not exists event_timelines (
    id uuid primary key default gen_random_uuid(),
    event_id uuid not null references events(id) on delete cascade,
    occurred_at timestamptz not null,
    title text not null,
    description text,
    source_document_id uuid references evidence_documents(id),
    timeline_type text,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

-- =========================================================
-- CUSTOMERS & EXPOSURE
-- =========================================================

create table if not exists customers (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    slug text not null unique,
    industry text,
    primary_region text,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists watchlists (
    id uuid primary key default gen_random_uuid(),
    customer_id uuid not null references customers(id) on delete cascade,
    name text not null,
    watchlist_type text,
    is_default boolean not null default false,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create table if not exists watchlist_items (
    id uuid primary key default gen_random_uuid(),
    watchlist_id uuid not null references watchlists(id) on delete cascade,
    entity_id uuid references entities_v2(id),
    item_type text not null,
    criticality_score numeric(6,4),
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create table if not exists suppliers (
    id uuid primary key default gen_random_uuid(),
    customer_id uuid not null references customers(id) on delete cascade,
    entity_id uuid references entities_v2(id),
    supplier_name text not null,
    tier_level integer,
    country_code text,
    criticality_score numeric(6,4),
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists facilities (
    id uuid primary key default gen_random_uuid(),
    customer_id uuid not null references customers(id) on delete cascade,
    entity_id uuid references entities_v2(id),
    facility_name text not null,
    facility_type text,
    country_code text,
    lat numeric(10,6),
    lng numeric(10,6),
    criticality_score numeric(6,4),
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists ports (
    id uuid primary key default gen_random_uuid(),
    entity_id uuid references entities_v2(id),
    port_code text,
    country_code text,
    lat numeric(10,6),
    lng numeric(10,6),
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create table if not exists routes (
    id uuid primary key default gen_random_uuid(),
    entity_id uuid references entities_v2(id),
    route_name text not null,
    route_type text,
    origin_port_id uuid references ports(id),
    destination_port_id uuid references ports(id),
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create table if not exists commodities (
    id uuid primary key default gen_random_uuid(),
    entity_id uuid references entities_v2(id),
    commodity_code text,
    sector text,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create table if not exists customer_assets (
    id uuid primary key default gen_random_uuid(),
    customer_id uuid not null references customers(id) on delete cascade,
    entity_id uuid references entities_v2(id),
    asset_label text not null,
    asset_type text,
    criticality_score numeric(6,4),
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists exposure_links (
    id uuid primary key default gen_random_uuid(),
    customer_id uuid not null references customers(id) on delete cascade,
    source_object_type text not null,
    source_object_id uuid not null,
    target_entity_id uuid references entities_v2(id),
    relationship_type text not null,
    criticality_score numeric(6,4),
    exposure_weight numeric(8,4),
    confidence_score numeric(6,4),
    valid_from timestamptz,
    valid_to timestamptz,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create index if not exists idx_exposure_links_customer_source
    on exposure_links (customer_id, source_object_type, source_object_id);

create index if not exists idx_exposure_links_customer_target
    on exposure_links (customer_id, target_entity_id, relationship_type);

-- =========================================================
-- ALERTS & WORKFLOW
-- =========================================================

create table if not exists alerts_v2 (
    id uuid primary key default gen_random_uuid(),
    customer_id uuid not null references customers(id) on delete cascade,
    event_id uuid not null references events(id) on delete cascade,
    alert_type text not null,
    severity alert_severity_enum not null,
    status alert_status_enum not null default 'new',
    headline text not null,
    summary_text text,
    recommended_action text,
    triggered_at timestamptz not null,
    resolved_at timestamptz,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists idx_alerts_v2_customer_status_triggered
    on alerts_v2 (customer_id, status, triggered_at desc);

create table if not exists alert_evidence (
    id uuid primary key default gen_random_uuid(),
    alert_id uuid not null references alerts_v2(id) on delete cascade,
    document_id uuid not null references evidence_documents(id),
    evidence_type text,
    relevance_score numeric(6,4),
    fragment_id uuid references document_fragments(id),
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create table if not exists alert_actions (
    id uuid primary key default gen_random_uuid(),
    alert_id uuid not null references alerts_v2(id) on delete cascade,
    action_type text not null,
    actor_id text,
    notes text,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

-- =========================================================
-- MARKETS, MACRO, EVALUATION
-- =========================================================

create table if not exists macro_series (
    id uuid primary key default gen_random_uuid(),
    series_code text not null unique,
    provider_name text not null,
    name text not null,
    frequency text,
    unit text,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create table if not exists macro_points (
    id uuid primary key default gen_random_uuid(),
    series_id uuid not null references macro_series(id) on delete cascade,
    period_start date,
    period_end date,
    as_of_date date,
    release_date date,
    observed_value numeric,
    revision_number integer,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create index if not exists idx_macro_points_series_period
    on macro_points (series_id, period_start desc);

create table if not exists risk_scores (
    id uuid primary key default gen_random_uuid(),
    customer_id uuid references customers(id) on delete cascade,
    event_id uuid references events(id) on delete cascade,
    alert_id uuid references alerts_v2(id) on delete cascade,
    score_type text not null,
    score_value numeric(8,4) not null,
    component_scores jsonb not null default '{}'::jsonb,
    scored_at timestamptz not null default now()
);

create index if not exists idx_risk_scores_customer_event
    on risk_scores (customer_id, event_id, score_type);

create table if not exists evaluation_labels (
    id uuid primary key default gen_random_uuid(),
    event_id uuid references events(id) on delete cascade,
    customer_id uuid references customers(id) on delete cascade,
    label_type text not null,
    label_value text not null,
    metadata jsonb not null default '{}'::jsonb,
    labeled_at timestamptz not null default now()
);

create index if not exists idx_evaluation_labels_event_customer
    on evaluation_labels (event_id, customer_id, label_type);

create table if not exists backtest_runs (
    id uuid primary key default gen_random_uuid(),
    run_name text not null,
    config_json jsonb not null default '{}'::jsonb,
    metrics_json jsonb not null default '{}'::jsonb,
    started_at timestamptz not null default now(),
    completed_at timestamptz
);
