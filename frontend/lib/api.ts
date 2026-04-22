const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
const CUSTOMER_SLUG = process.env.NEXT_PUBLIC_CUSTOMER_SLUG || "";

function buildHeaders(headers: HeadersInit = {}) {
  const resolved = new Headers(headers);
  if (CUSTOMER_SLUG) {
    resolved.set("X-Customer-Slug", CUSTOMER_SLUG);
  }
  return resolved;
}

async function fetchJson<T = any>(input: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(input, {
    ...init,
    headers: buildHeaders(init.headers),
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export interface EventRiskScore {
  id: string;
  score_type: string;
  score_value: number;
  confidence_score?: number | null;
  severity: string;
  rationale_text?: string | null;
  scored_at?: string | null;
  metadata?: Record<string, unknown> | null;
}

export interface EventTimelineItem {
  id: number;
  event_id: string;
  occurred_at?: string | null;
  title: string;
  description?: string | null;
  source_document_id?: string | null;
  timeline_type: string;
  metadata?: Record<string, unknown> | null;
}

export interface EventDocument {
  id: number;
  title: string;
  url?: string | null;
  published_at?: string | null;
  source_id: number;
  is_primary: boolean;
  raw_payload_ref?: string | null;
  source_confidence?: number | null;
}

export interface EventEntity {
  id: string;
  canonical_name: string;
  display_name?: string | null;
  entity_type: string;
  event_role?: string | null;
}

export interface EventExposureMatch {
  id: string;
  source_object_type: string;
  source_object_id: string;
  source_object_name?: string | null;
  relationship_type: string;
  criticality_score?: number | null;
  exposure_weight?: number | null;
  confidence_score?: number | null;
  target_entity_id?: string | null;
  target_entity_name?: string | null;
  metadata?: Record<string, unknown> | null;
}

export interface EventEvaluationLabel {
  id: string;
  label_type: string;
  label_value: string;
  notes?: string | null;
  labeled_by?: string | null;
  labeled_at: string;
  alert_id?: string | null;
  customer_id?: string | null;
  metadata?: Record<string, unknown> | null;
}

export interface EventV2 {
  id: string;
  canonical_title: string;
  event_type?: string | null;
  event_subtype?: string | null;
  status: string;
  first_seen_at?: string | null;
  last_seen_at?: string | null;
  severity_score?: number | null;
  confidence_score?: number | null;
  summary_text?: string | null;
  document_count: number;
  entity_count: number;
  timeline_count: number;
  documents?: EventDocument[];
  entities?: EventEntity[];
  timeline?: EventTimelineItem[];
  matched_watchlists: Array<{
    watchlist_id: string;
    entity_id?: string | null;
    item_type: string;
    criticality_score?: number | null;
  }>;
  exposure_matches: EventExposureMatch[];
  exposure_summary?: string | null;
  risk_score?: EventRiskScore | null;
}

export interface AlertV2 {
  id: string;
  event_id: string;
  alert_type: string;
  severity: string;
  status: string;
  headline: string;
  summary_text?: string | null;
  recommended_action?: string | null;
  triggered_at: string;
  resolved_at?: string | null;
  metadata?: {
    risk_score?: EventRiskScore | null;
    top_exposure_match?: EventExposureMatch | null;
  } | null;
}

export async function fetchDocuments() {
  return fetchJson(`${API_BASE_URL}/documents/`);
}

export async function fetchEvents() {
  return fetchJson(`${API_BASE_URL}/events/`);
}

export async function fetchEventsV2(limit = 100): Promise<EventV2[]> {
  return fetchJson(`${API_BASE_URL}/events/v2?limit=${limit}`);
}

export async function fetchEventV2(eventId: string): Promise<EventV2> {
  return fetchJson(`${API_BASE_URL}/events/v2/${eventId}`);
}

export async function fetchEventTimeline(eventId: string): Promise<EventTimelineItem[]> {
  return fetchJson(`${API_BASE_URL}/events/v2/${eventId}/timeline`);
}

export async function fetchEventRisk(eventId: string): Promise<EventRiskScore | { detail: string }> {
  return fetchJson(`${API_BASE_URL}/events/v2/${eventId}/risk`);
}

export async function fetchEventEvaluation(eventId: string): Promise<EventEvaluationLabel[]> {
  return fetchJson(`${API_BASE_URL}/events/v2/${eventId}/evaluation`);
}

export async function createEventEvaluation(eventId: string, payload: { label_type: string; label_value: string; notes?: string; labeled_by?: string }) {
  return fetchJson(`${API_BASE_URL}/events/v2/${eventId}/evaluation`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function triggerIngestion() {
  return fetchJson(`${API_BASE_URL}/ingestion/trigger`, { method: "POST" });
}

export async function triggerComplianceIngestion(query = "") {
  const url = new URL(`${API_BASE_URL}/ingestion/compliance`);
  if (query) {
    url.searchParams.append("query", query);
  }
  return fetchJson(url.toString(), { method: "POST" });
}

export async function triggerClustering() {
  return fetchJson(`${API_BASE_URL}/clustering/trigger`, { method: "POST" });
}

export async function fetchScenarios(region?: string, sector?: string) {
  const url = new URL(`${API_BASE_URL}/scenarios/`);
  if (region) url.searchParams.append("region", region);
  if (sector) url.searchParams.append("sector", sector);
  return fetchJson(url.toString());
}

export async function fetchTrendingScenarios() {
  return fetchJson(`${API_BASE_URL}/scenarios/trending`);
}

export async function followScenario(topic: string, region: string = "GLOBAL", sector: string = "GENERAL") {
  return fetchJson(`${API_BASE_URL}/scenarios/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ topic, region, sector }),
  });
}

export async function updateScenarioStatus(id: number, status: string) {
  return fetchJson(`${API_BASE_URL}/scenarios/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
}

export async function runScenarioSync(topic: string) {
  return fetchJson(`${API_BASE_URL}/scenarios/run?topic=${encodeURIComponent(topic)}`, { method: "POST" });
}

export async function fetchClaims() {
  return fetchJson(`${API_BASE_URL}/claims/`);
}

export async function extractClaims(docId: number) {
  return fetchJson(`${API_BASE_URL}/claims/extract/${docId}`, { method: "POST" });
}

export async function verifyEventClaims(eventId: number) {
  return fetchJson(`${API_BASE_URL}/claims/verify/event/${eventId}`, { method: "POST" });
}

export async function fetchMarketCorrelation(ticker: string) {
  return fetchJson(`${API_BASE_URL}/markets/correlation/${ticker}`);
}

export async function syncMarkets() {
  return fetchJson(`${API_BASE_URL}/markets/sync`, { method: "POST" });
}

export async function fetchAlerts() {
  return fetchJson(`${API_BASE_URL}/alerts/`);
}

export async function fetchAlertsV2(limit = 25): Promise<AlertV2[]> {
  return fetchJson(`${API_BASE_URL}/alerts/v2?limit=${limit}`);
}

export async function generateAlertsV2() {
  return fetchJson(`${API_BASE_URL}/alerts/v2/generate`, { method: "POST" });
}

export async function fetchAlertV2(alertId: string): Promise<AlertV2> {
  return fetchJson(`${API_BASE_URL}/alerts/v2/${alertId}`);
}

export async function fetchAlertEvidenceV2(alertId: string) {
  return fetchJson(`${API_BASE_URL}/alerts/v2/${alertId}/evidence`);
}

export async function addAlertActionV2(alertId: string, payload: { action_type: string; actor_id?: string; notes?: string }) {
  return fetchJson(`${API_BASE_URL}/alerts/v2/${alertId}/actions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function clearAlerts() {
  return fetchJson(`${API_BASE_URL}/alerts/clear`, { method: "POST" });
}

export async function fetchNexusGraph() {
  return fetchJson(`${API_BASE_URL}/nexus/graph`);
}

export async function syncNexus() {
  return fetchJson(`${API_BASE_URL}/nexus/sync`, { method: "POST" });
}

export async function fetchIntelligenceBrief(topic: string, ticker?: string) {
  const url = new URL(`${API_BASE_URL}/intelligence/brief`);
  url.searchParams.append("topic", topic);
  if (ticker) url.searchParams.append("ticker", ticker);
  return fetchJson(url.toString());
}

export async function fetchLiveIntelligence(query: string = "geopolitics") {
  return fetchJson(`${API_BASE_URL}/intelligence/live?query=${encodeURIComponent(query)}`);
}

export async function fetchAlertExplanation(alertId: number) {
  return fetchJson(`${API_BASE_URL}/intelligence/explain/${alertId}`);
}

export async function fetchIntelligenceTrends() {
  return fetchJson(`${API_BASE_URL}/analytics/trends`);
}

export async function fetchTopicHistory(topic: string) {
  return fetchJson(`${API_BASE_URL}/analytics/topic/${encodeURIComponent(topic)}`);
}

export async function fetchPortfolioSummary() {
  return fetchJson(`${API_BASE_URL}/scenarios/summary`);
}

export async function fetchEvaluationMetrics(includeCustomerScope = true) {
  const url = new URL(`${API_BASE_URL}/evaluation/metrics`);
  url.searchParams.append("include_customer_scope", String(includeCustomerScope));
  return fetchJson(url.toString());
}

export async function fetchEvaluationRuns(includeCustomerScope = true) {
  const url = new URL(`${API_BASE_URL}/evaluation/runs`);
  url.searchParams.append("include_customer_scope", String(includeCustomerScope));
  return fetchJson(url.toString());
}

export async function createEvaluationRun(run_name: string, includeCustomerScope = true) {
  return fetchJson(`${API_BASE_URL}/evaluation/runs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ run_name, include_customer_scope: includeCustomerScope }),
  });
}

export async function fetchIntelligenceComposite() {
  const [nexus, trends] = await Promise.all([fetchNexusGraph(), fetchIntelligenceTrends()]);
  return { nexus, trends };
}
