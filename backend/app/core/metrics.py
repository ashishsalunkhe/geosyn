from prometheus_client import Counter, Histogram


ingestion_runs_total = Counter(
    "geosyn_ingestion_runs_total",
    "Number of ingestion runs by source",
    ["source"],
)

ingestion_documents_total = Counter(
    "geosyn_ingestion_documents_total",
    "Number of ingested documents by source",
    ["source"],
)

clustering_runs_total = Counter(
    "geosyn_clustering_runs_total",
    "Number of clustering runs",
)

market_sync_runs_total = Counter(
    "geosyn_market_sync_runs_total",
    "Number of market sync runs",
)

alerts_generated_total = Counter(
    "geosyn_alerts_generated_total",
    "Number of exposure-aware alerts generated",
    ["customer_slug"],
)

request_cache_hits_total = Counter(
    "geosyn_request_cache_hits_total",
    "Number of Redis cache hits by endpoint",
    ["endpoint"],
)

request_cache_misses_total = Counter(
    "geosyn_request_cache_misses_total",
    "Number of Redis cache misses by endpoint",
    ["endpoint"],
)

task_runtime_seconds = Histogram(
    "geosyn_task_runtime_seconds",
    "Runtime for background and operational tasks",
    ["task_name"],
)
