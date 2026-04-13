const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export async function fetchDocuments() {
  const res = await fetch(`${API_BASE_URL}/documents/`);
  if (!res.ok) throw new Error("Failed to fetch documents");
  return res.json();
}

export async function fetchEvents() {
  const res = await fetch(`${API_BASE_URL}/events/`);
  if (!res.ok) throw new Error("Failed to fetch events");
  return res.json();
}

export async function triggerIngestion() {
  const res = await fetch(`${API_BASE_URL}/ingestion/trigger`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to trigger ingestion");
  return res.json();
}

export async function triggerClustering() {
  const res = await fetch(`${API_BASE_URL}/clustering/trigger`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to trigger clustering");
  return res.json();
}

export async function fetchScenarios(region?: string, sector?: string) {
  const url = new URL(`${API_BASE_URL}/scenarios/`);
  if (region) url.searchParams.append("region", region);
  if (sector) url.searchParams.append("sector", sector);
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error("Failed to fetch scenarios");
  return res.json();
}

export async function fetchTrendingScenarios() {
  const res = await fetch(`${API_BASE_URL}/scenarios/trending`);
  if (!res.ok) throw new Error("Failed to fetch trending scenarios");
  return res.json();
}

export async function followScenario(topic: string, region: string = "GLOBAL", sector: string = "GENERAL") {
  const res = await fetch(`${API_BASE_URL}/scenarios/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ topic, region, sector }),
  });
  if (!res.ok) throw new Error("Failed to follow scenario");
  return res.json();
}

export async function updateScenarioStatus(id: number, status: string) {
  const res = await fetch(`${API_BASE_URL}/scenarios/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) throw new Error("Failed to update scenario status");
  return res.json();
}

export async function runScenarioSync(topic: string) {
  const res = await fetch(`${API_BASE_URL}/scenarios/run?topic=${encodeURIComponent(topic)}`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to run scenario sync");
  return res.json();
}

export async function fetchClaims() {
  const res = await fetch(`${API_BASE_URL}/claims/`);
  if (!res.ok) throw new Error("Failed to fetch claims");
  return res.json();
}

export async function extractClaims(docId: number) {
  const res = await fetch(`${API_BASE_URL}/claims/extract/${docId}`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to extract claims");
  return res.json();
}

export async function verifyEventClaims(eventId: number) {
  const res = await fetch(`${API_BASE_URL}/claims/verify/event/${eventId}`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to verify claims");
  return res.json();
}

export async function fetchMarketCorrelation(ticker: string) {
  const res = await fetch(`${API_BASE_URL}/markets/correlation/${ticker}`);
  if (!res.ok) throw new Error("Failed to fetch market data");
  return res.json();
}

export async function syncMarkets() {
  const res = await fetch(`${API_BASE_URL}/markets/sync`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to sync markets");
  return res.json();
}

export async function fetchAlerts() {
  const res = await fetch(`${API_BASE_URL}/alerts/`);
  if (!res.ok) throw new Error("Failed to fetch alerts");
  return res.json();
}

export async function clearAlerts() {
  const res = await fetch(`${API_BASE_URL}/alerts/clear`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to clear alerts");
  return res.json();
}

export async function fetchNexusGraph() {
  const res = await fetch(`${API_BASE_URL}/nexus/graph`);
  if (!res.ok) throw new Error("Failed to fetch nexus graph");
  return res.json();
}

export async function syncNexus() {
  const res = await fetch(`${API_BASE_URL}/nexus/sync`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to sync nexus");
  return res.json();
}

export async function fetchIntelligenceBrief(topic: string, ticker?: string) {
  const url = new URL(`${API_BASE_URL}/intelligence/brief`);
  url.searchParams.append("topic", topic);
  if (ticker) url.searchParams.append("ticker", ticker);
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error("Failed to fetch intelligence brief");
  return res.json();
}

export async function fetchLiveIntelligence(query: string = "geopolitics") {
  const res = await fetch(`${API_BASE_URL}/intelligence/live?query=${encodeURIComponent(query)}`);
  if (!res.ok) throw new Error("Failed to fetch live intelligence");
  return res.json();
}

export async function fetchAlertExplanation(alertId: number) {
  const res = await fetch(`${API_BASE_URL}/intelligence/explain/${alertId}`);
  if (!res.ok) throw new Error("Failed to fetch alert explanation");
  return res.json();
}

export async function fetchIntelligenceTrends() {
  const res = await fetch(`${API_BASE_URL}/analytics/trends`);
  if (!res.ok) throw new Error("Failed to fetch intelligence trends");
  return res.json();
}

export async function fetchTopicHistory(topic: string) {
  const res = await fetch(`${API_BASE_URL}/analytics/topic/${encodeURIComponent(topic)}`);
  if (!res.ok) throw new Error("Failed to fetch topic history");
  return res.json();
}

export async function fetchPortfolioSummary() {
  const res = await fetch(`${API_BASE_URL}/scenarios/summary`);
  if (!res.ok) throw new Error("Failed to fetch portfolio summary");
  return res.json();
}
