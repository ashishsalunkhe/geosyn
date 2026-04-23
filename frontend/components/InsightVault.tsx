"use client";

import React, { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import {
  AlertTriangle,
  CheckCircle2,
  Database,
  FileSpreadsheet,
  Loader2,
  Radar,
  Shield,
  Upload,
} from "lucide-react";
import {
  addWatchlistItem,
  createEvaluationRun,
  createWatchlist,
  deleteWatchlistItem,
  fetchCurrentCustomer,
  fetchEvaluationMetrics,
  fetchWatchlists,
  importExposureCsv,
  validateExposureCsv,
  type CustomerOverview,
  type WatchlistV2,
} from "@/lib/api";

interface ValidationResult {
  row_count: number;
  supported_rows: number;
  duplicate_rows: number;
  error_count: number;
  warning_count: number;
  preview_rows: Array<Record<string, unknown>>;
  errors: string[];
  warnings: string[];
  supported_source_object_types: string[];
}

const InsightVault: React.FC = () => {
  const [customer, setCustomer] = useState<CustomerOverview | null>(null);
  const [metrics, setMetrics] = useState<Record<string, unknown> | null>(null);
  const [validation, setValidation] = useState<ValidationResult | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(true);
  const [validating, setValidating] = useState(false);
  const [importing, setImporting] = useState(false);
  const [creatingRun, setCreatingRun] = useState(false);
  const [creatingWatchlist, setCreatingWatchlist] = useState(false);
  const [addingWatchlistItem, setAddingWatchlistItem] = useState(false);
  const [watchlists, setWatchlists] = useState<WatchlistV2[]>([]);
  const [watchlistName, setWatchlistName] = useState("");
  const [selectedWatchlistId, setSelectedWatchlistId] = useState("");
  const [watchlistItemName, setWatchlistItemName] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadOperatorData = async () => {
    try {
      const [customerData, metricData, watchlistData] = await Promise.all([
        fetchCurrentCustomer(),
        fetchEvaluationMetrics(),
        fetchWatchlists(),
      ]);
      setCustomer(customerData);
      setMetrics(metricData as Record<string, unknown>);
      setWatchlists(watchlistData);
      setSelectedWatchlistId((current) => current || watchlistData[0]?.id || "");
    } catch (err) {
      console.error("Operator workspace load error", err);
      setError("Failed to load operator workspace.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadOperatorData();
  }, []);

  const readinessTone = customer?.onboarding.ready_for_exposure_alerting ? "text-success" : "text-hazard";

  const metricCards = useMemo(
    () => [
      {
        label: "Exposure Links",
        value: customer?.counts.exposure_links ?? 0,
        hint: "Mapped customer-specific exposure records",
      },
      {
        label: "Open Alerts",
        value: customer?.counts.alerts_open ?? 0,
        hint: "Alerts still needing workflow resolution",
      },
      {
        label: "Active Events",
        value: customer?.counts.active_events ?? 0,
        hint: "Canonical events currently active or emerging",
      },
      {
        label: "Alert Precision",
        value: typeof metrics?.precision_at_top_n === "number" ? `${Math.round(Number(metrics.precision_at_top_n) * 100)}%` : "N/A",
        hint: "Evaluation metric from backtest layer",
      },
    ],
    [customer, metrics],
  );

  const handleValidate = async () => {
    if (!selectedFile) return;
    try {
      setValidating(true);
      setError(null);
      setMessage(null);
      const result = await validateExposureCsv(selectedFile);
      setValidation(result as ValidationResult);
      setMessage("Exposure file validated. Review preview before import.");
    } catch (err) {
      console.error(err);
      setError("Exposure validation failed.");
    } finally {
      setValidating(false);
    }
  };

  const handleImport = async () => {
    if (!selectedFile) return;
    try {
      setImporting(true);
      setError(null);
      setMessage(null);
      const result = await importExposureCsv(selectedFile);
      setMessage(`Exposure import complete. Created ${result.created_links ?? 0} exposure links.`);
      await loadOperatorData();
    } catch (err) {
      console.error(err);
      setError("Exposure import failed.");
    } finally {
      setImporting(false);
    }
  };

  const handleCreateRun = async () => {
    try {
      setCreatingRun(true);
      setError(null);
      setMessage(null);
      const runName = `Operator run ${new Date().toISOString().slice(0, 10)}`;
      await createEvaluationRun(runName, true);
      const metricData = await fetchEvaluationMetrics();
      setMetrics(metricData as Record<string, unknown>);
      setMessage("Backtest run created for current customer scope.");
    } catch (err) {
      console.error(err);
      setError("Could not create evaluation run.");
    } finally {
      setCreatingRun(false);
    }
  };

  const handleCreateWatchlist = async () => {
    if (!watchlistName.trim()) return;
    try {
      setCreatingWatchlist(true);
      setError(null);
      setMessage(null);
      await createWatchlist({ name: watchlistName.trim(), watchlist_type: "custom", is_default: false });
      setWatchlistName("");
      await loadOperatorData();
      setMessage("Watchlist created.");
    } catch (err) {
      console.error(err);
      setError("Could not create watchlist.");
    } finally {
      setCreatingWatchlist(false);
    }
  };

  const handleAddWatchlistItem = async () => {
    if (!selectedWatchlistId || !watchlistItemName.trim()) return;
    try {
      setAddingWatchlistItem(true);
      setError(null);
      setMessage(null);
      await addWatchlistItem(selectedWatchlistId, {
        canonical_name: watchlistItemName.trim(),
        entity_type: "company",
        item_type: "entity",
      });
      setWatchlistItemName("");
      await loadOperatorData();
      setMessage("Watchlist item added.");
    } catch (err) {
      console.error(err);
      setError("Could not add watchlist item.");
    } finally {
      setAddingWatchlistItem(false);
    }
  };

  const handleDeleteWatchlistItem = async (itemId: string) => {
    try {
      setError(null);
      setMessage(null);
      await deleteWatchlistItem(itemId);
      await loadOperatorData();
      setMessage("Watchlist item removed.");
    } catch (err) {
      console.error(err);
      setError("Could not remove watchlist item.");
    }
  };

  if (loading) {
    return (
      <div className="p-12 text-center">
        <div className="mb-4 inline-block h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        <p className="animate-pulse text-[10px] font-black uppercase tracking-widest text-text-muted">
          Loading operator workspace...
        </p>
      </div>
    );
  }

  return (
    <div className="animate-in fade-in slide-in-from-bottom-4 space-y-8 p-1 duration-700">
      <section className="grid grid-cols-1 gap-4 lg:grid-cols-12">
        <div className="glass-panel rounded-2xl border-border bg-panel-bg p-6 lg:col-span-8">
          <div className="mb-5 flex flex-wrap items-start justify-between gap-4">
            <div>
              <div className="mb-2 flex items-center gap-2">
                <Shield size={14} className="text-primary" />
                <span className="text-[10px] font-black uppercase tracking-[0.2em] text-text-muted">
                  Operator Workspace
                </span>
              </div>
              <h2 className="text-xl font-black uppercase italic tracking-tight text-foreground">
                {customer?.customer.name || "Customer"}
              </h2>
              <p className="mt-1 text-[10px] font-bold uppercase tracking-widest text-text-muted">
                {customer?.customer.industry || "general"} / {customer?.customer.primary_region || "global"}
              </p>
            </div>
            <div className="rounded-2xl border border-border bg-background/40 px-4 py-3">
              <div className="text-[8px] font-black uppercase tracking-widest text-text-muted">Alerting Readiness</div>
              <div className={`mt-1 text-sm font-black uppercase italic ${readinessTone}`}>
                {customer?.onboarding.ready_for_exposure_alerting ? "Ready" : "Needs Exposure Data"}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
            {metricCards.map((card) => (
              <div key={card.label} className="rounded-2xl border border-border bg-background/40 p-4">
                <div className="text-[8px] font-black uppercase tracking-widest text-text-muted">{card.label}</div>
                <div className="mt-2 text-xl font-black italic text-foreground">{card.value}</div>
                <div className="mt-2 text-[9px] font-bold leading-snug text-text-muted">{card.hint}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="glass-panel rounded-2xl border-border bg-panel-bg p-6 lg:col-span-4">
          <div className="mb-4 flex items-center gap-2">
            <Radar size={14} className="text-primary" />
            <span className="text-[10px] font-black uppercase tracking-[0.2em] text-foreground">Onboarding Checklist</span>
          </div>
          <div className="space-y-3">
            {([
              ["Customer profile", customer?.onboarding.has_customer_profile],
              ["Watchlists created", customer?.onboarding.has_watchlists],
              ["Watchlist items linked", customer?.onboarding.has_watchlist_items],
              ["Exposure links imported", customer?.onboarding.has_exposure_links],
            ] as Array<[string, boolean | undefined]>).map(([label, complete]) => (
              <div key={String(label)} className="flex items-center justify-between rounded-xl border border-border bg-background/30 px-3 py-2.5">
                <span className="text-[10px] font-black uppercase tracking-widest text-foreground">{label}</span>
                {complete ? (
                  <CheckCircle2 size={14} className="text-success" />
                ) : (
                  <AlertTriangle size={14} className="text-hazard" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-6 xl:grid-cols-12">
        <div className="glass-panel rounded-2xl border-border bg-panel-bg p-6 xl:col-span-7">
          <div className="mb-5 flex items-center gap-2">
            <FileSpreadsheet size={16} className="text-primary" />
            <div>
              <h3 className="text-sm font-black uppercase italic tracking-widest text-foreground">Exposure Import</h3>
              <p className="text-[10px] font-bold uppercase tracking-widest text-text-muted">
                Validate and import supplier, facility, port, route, commodity, or asset mappings
              </p>
            </div>
          </div>

          <div className="rounded-2xl border border-dashed border-border bg-background/30 p-4">
            <label className="flex cursor-pointer flex-col items-center justify-center gap-3 rounded-xl border border-border bg-panel-bg/40 px-4 py-8 text-center transition-all hover:border-primary/30">
              <Upload size={20} className="text-primary" />
              <div>
                <div className="text-[10px] font-black uppercase tracking-widest text-foreground">
                  {selectedFile ? selectedFile.name : "Choose Exposure CSV"}
                </div>
                <div className="mt-1 text-[9px] font-bold text-text-muted">
                  Required columns: source_object_type, source_object_id, relationship_type, target_entity_name
                </div>
              </div>
              <input
                type="file"
                accept=".csv,text/csv"
                className="hidden"
                onChange={(event) => {
                  const file = event.target.files?.[0] || null;
                  setSelectedFile(file);
                  setValidation(null);
                  setMessage(null);
                  setError(null);
                }}
              />
            </label>
          </div>

          <div className="mt-4 flex flex-wrap gap-3">
            <button
              onClick={() => void handleValidate()}
              disabled={!selectedFile || validating}
              className="rounded-xl border border-primary/20 bg-primary/10 px-4 py-2 text-[10px] font-black uppercase tracking-widest text-primary transition-all hover:bg-primary/20 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {validating ? "Validating..." : "Validate File"}
            </button>
            <button
              onClick={() => void handleImport()}
              disabled={!selectedFile || importing}
              className="rounded-xl border border-success/20 bg-success/10 px-4 py-2 text-[10px] font-black uppercase tracking-widest text-success transition-all hover:bg-success/20 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {importing ? "Importing..." : "Import Exposure"}
            </button>
          </div>

          {message ? <p className="mt-4 text-[10px] font-bold text-success">{message}</p> : null}
          {error ? <p className="mt-4 text-[10px] font-bold text-error">{error}</p> : null}

          {validation ? (
            <div className="mt-6 space-y-4">
              <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
                {([
                  ["Rows", validation.row_count],
                  ["Supported", validation.supported_rows],
                  ["Duplicates", validation.duplicate_rows],
                  ["Errors", validation.error_count],
                ] as Array<[string, number]>).map(([label, value]) => (
                  <div key={String(label)} className="rounded-xl border border-border bg-background/40 p-3">
                    <div className="text-[8px] font-black uppercase tracking-widest text-text-muted">{label}</div>
                    <div className="mt-2 text-lg font-black italic text-foreground">{value}</div>
                  </div>
                ))}
              </div>

              <div className="rounded-2xl border border-border bg-background/30 p-4">
                <div className="mb-3 text-[9px] font-black uppercase tracking-widest text-primary">Preview Rows</div>
                <div className="space-y-2">
                  {validation.preview_rows.slice(0, 5).map((row, index) => (
                    <div key={index} className="rounded-xl border border-border bg-panel-bg/40 p-3 text-[9px]">
                      <div className="font-black uppercase tracking-widest text-foreground">
                        Row {String(row.row_number)}: {String(row.source_object_type)} / {String(row.source_object_id)}
                      </div>
                      <div className="mt-1 font-bold text-text-muted">
                        {String(row.relationship_type)}
                        {" -> "}
                        {String(row.target_entity_name)}
                      </div>
                      {"error" in row ? (
                        <div className="mt-1 font-bold text-error">{String(row.error)}</div>
                      ) : row.duplicate ? (
                        <div className="mt-1 font-bold text-hazard">Duplicate of an existing exposure link</div>
                      ) : null}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : null}
        </div>

        <div className="glass-panel rounded-2xl border-border bg-panel-bg p-6 xl:col-span-5">
          <div className="mb-5 flex items-center gap-2">
            <Database size={16} className="text-primary" />
            <div>
              <h3 className="text-sm font-black uppercase italic tracking-widest text-foreground">Evaluation Ops</h3>
              <p className="text-[10px] font-bold uppercase tracking-widest text-text-muted">
                Trigger customer-scoped backtest runs and inspect quality metrics
              </p>
            </div>
          </div>

          <div className="space-y-3">
            {([
              ["Lead time", metrics?.lead_time_hours],
              ["Precision @ top N", metrics?.precision_at_top_n],
              ["Useful alert rate", metrics?.useful_alert_rate],
              ["False positive rate", metrics?.false_positive_rate],
            ] as Array<[string, unknown]>).map(([label, value]) => (
              <div key={String(label)} className="flex items-center justify-between rounded-xl border border-border bg-background/30 px-4 py-3">
                <span className="text-[10px] font-black uppercase tracking-widest text-foreground">{label}</span>
                <span className="text-[10px] font-black italic text-primary">
                  {typeof value === "number" ? value.toFixed(2) : "N/A"}
                </span>
              </div>
            ))}
          </div>

          <button
            onClick={() => void handleCreateRun()}
            disabled={creatingRun}
            className="mt-5 flex w-full items-center justify-center gap-2 rounded-xl border border-primary/20 bg-primary/10 px-4 py-3 text-[10px] font-black uppercase tracking-widest text-primary transition-all hover:bg-primary/20 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {creatingRun ? <Loader2 size={14} className="animate-spin" /> : <Radar size={14} />}
            {creatingRun ? "Creating Run..." : "Create Evaluation Run"}
          </button>
        </div>
      </section>

      <section className="glass-panel rounded-2xl border-border bg-panel-bg p-6">
        <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-black uppercase italic tracking-widest text-foreground">Watchlist Manager</h3>
            <p className="text-[10px] font-bold uppercase tracking-widest text-text-muted">
              Maintain the customer monitoring scope used for event matching
            </p>
          </div>
          <div className="rounded-xl border border-border bg-background/40 px-3 py-2 text-[9px] font-black uppercase tracking-widest text-primary">
            {watchlists.length} watchlists
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6 xl:grid-cols-12">
          <div className="space-y-4 xl:col-span-4">
            <div className="rounded-2xl border border-border bg-background/30 p-4">
              <div className="mb-3 text-[9px] font-black uppercase tracking-widest text-primary">Create Watchlist</div>
              <input
                value={watchlistName}
                onChange={(event) => setWatchlistName(event.target.value)}
                placeholder="Critical counterparties"
                className="w-full rounded-xl border border-border bg-panel-bg/40 px-3 py-2 text-[10px] font-bold text-foreground outline-none"
              />
              <button
                onClick={() => void handleCreateWatchlist()}
                disabled={creatingWatchlist || !watchlistName.trim()}
                className="mt-3 w-full rounded-xl border border-primary/20 bg-primary/10 px-4 py-2 text-[10px] font-black uppercase tracking-widest text-primary transition-all hover:bg-primary/20 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {creatingWatchlist ? "Creating..." : "Create Watchlist"}
              </button>
            </div>

            <div className="rounded-2xl border border-border bg-background/30 p-4">
              <div className="mb-3 text-[9px] font-black uppercase tracking-widest text-primary">Add Watch Item</div>
              <select
                value={selectedWatchlistId}
                onChange={(event) => setSelectedWatchlistId(event.target.value)}
                className="w-full rounded-xl border border-border bg-panel-bg/40 px-3 py-2 text-[10px] font-bold text-foreground outline-none"
              >
                <option value="">Select watchlist</option>
                {watchlists.map((watchlist) => (
                  <option key={watchlist.id} value={watchlist.id}>
                    {watchlist.name}
                  </option>
                ))}
              </select>
              <input
                value={watchlistItemName}
                onChange={(event) => setWatchlistItemName(event.target.value)}
                placeholder="TSMC / Red Sea / LNG"
                className="mt-3 w-full rounded-xl border border-border bg-panel-bg/40 px-3 py-2 text-[10px] font-bold text-foreground outline-none"
              />
              <button
                onClick={() => void handleAddWatchlistItem()}
                disabled={addingWatchlistItem || !selectedWatchlistId || !watchlistItemName.trim()}
                className="mt-3 w-full rounded-xl border border-success/20 bg-success/10 px-4 py-2 text-[10px] font-black uppercase tracking-widest text-success transition-all hover:bg-success/20 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {addingWatchlistItem ? "Adding..." : "Add Watch Item"}
              </button>
            </div>
          </div>

          <div className="space-y-4 xl:col-span-8">
            {watchlists.map((watchlist) => (
              <div key={watchlist.id} className="rounded-2xl border border-border bg-background/30 p-4">
                <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
                  <div>
                    <div className="text-[10px] font-black uppercase tracking-widest text-foreground">{watchlist.name}</div>
                    <div className="text-[8px] font-bold uppercase tracking-widest text-text-muted">
                      {watchlist.watchlist_type || "custom"} / {watchlist.item_count} items
                    </div>
                  </div>
                  {watchlist.is_default ? (
                    <span className="rounded-full border border-primary/20 bg-primary/10 px-2 py-1 text-[8px] font-black uppercase tracking-widest text-primary">
                      default
                    </span>
                  ) : null}
                </div>

                {watchlist.items.length ? (
                  <div className="flex flex-wrap gap-2">
                    {watchlist.items.map((item) => (
                      <button
                        key={item.id}
                        onClick={() => void handleDeleteWatchlistItem(item.id)}
                        className="inline-flex items-center gap-2 rounded-full border border-border bg-panel-bg/40 px-3 py-2 text-[8px] font-black uppercase tracking-widest text-text-muted transition-all hover:border-error/30 hover:text-error"
                      >
                        <span>{item.canonical_name || item.display_name || "Unnamed entity"}</span>
                        <span className="text-[7px] text-primary">{item.entity_type || item.item_type}</span>
                      </button>
                    ))}
                  </div>
                ) : (
                  <p className="text-[9px] font-bold text-text-muted">No watchlist items yet.</p>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default InsightVault;
