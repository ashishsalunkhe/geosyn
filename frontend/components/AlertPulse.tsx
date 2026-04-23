"use client";

import React, { useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AlertCircle, Activity, Clock, MessageSquare, Loader2, ShieldAlert, ArrowRightLeft, ListChecks, FileText } from "lucide-react";
import { addAlertActionV2, fetchAlertActionsV2, fetchAlertEvidenceV2, fetchAlertV2, fetchAlertWorkflowConfig, type AlertActionV2, type AlertV2 } from "@/lib/api";

interface AlertPulseProps {
  alerts: AlertV2[];
  onRefresh?: () => Promise<void> | void;
}

const severityClasses: Record<string, string> = {
  critical: "bg-error/8 border-error/30 shadow-[0_4px_20px_rgba(229,62,62,0.08)]",
  high: "bg-hazard/8 border-hazard/30 shadow-[0_4px_20px_rgba(255,168,0,0.06)]",
  medium: "bg-primary/8 border-primary/20 shadow-sm",
  low: "bg-panel-bg border-border",
};

function humanizeToken(value?: string | null) {
  if (!value) return "";
  return value.replace(/[_-]+/g, " ").replace(/\s+/g, " ").trim();
}

function relationToPhrase(value?: string | null) {
  const normalized = (value || "").toLowerCase();
  const mapping: Record<string, string> = {
    depends_on: "depends on",
    correlates_with: "moves with",
    exposed_to: "is exposed to",
    located_in: "operates in",
    ships_through: "ships through",
    sourced_from: "is sourced from",
    linked_to: "is linked to",
    supplied_by: "is supplied by",
    impacts: "is affected by",
  };
  return mapping[normalized] || humanizeToken(normalized).toLowerCase();
}

function buildExposureExplanation(detail: AlertV2) {
  const topExposure = detail.metadata?.top_exposure_match;
  if (!topExposure) {
    return detail.summary_text || "This alert was generated because the event overlaps with a mapped business exposure.";
  }

  const sourceName =
    topExposure.source_object_name ||
    humanizeToken(topExposure.source_object_id) ||
    "this mapped asset";
  const targetName =
    topExposure.target_entity_name ||
    detail.headline ||
    "the related event";
  const relation = relationToPhrase(topExposure.relationship_type);

  return `${sourceName} could be affected because it ${relation} ${targetName}.`;
}

const AlertPulse: React.FC<AlertPulseProps> = ({ alerts, onRefresh }) => {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [isMounted, setIsMounted] = useState(false);
  const [statusFilter, setStatusFilter] = useState("all");
  const [alertActions, setAlertActions] = useState<Record<string, AlertActionV2[]>>({});
  const [workflowConfig, setWorkflowConfig] = useState<Record<string, any> | null>(null);
  const [alertEvidence, setAlertEvidence] = useState<Record<string, any[]>>({});
  const [alertDetails, setAlertDetails] = useState<Record<string, AlertV2>>({});

  React.useEffect(() => {
    setIsMounted(true);
    fetchAlertWorkflowConfig().then(setWorkflowConfig).catch(console.error);
  }, []);

  const handleAction = async (alertId: string, actionType: string) => {
    try {
      setActionLoading(`${alertId}:${actionType}`);
      await addAlertActionV2(alertId, { action_type: actionType, actor_id: "frontend-user" });
      await onRefresh?.();
    } catch (error) {
      console.error("Failed to update alert action", error);
    } finally {
      setActionLoading(null);
    }
  };

  const handleExpand = async (alertId: string, isExpanded: boolean) => {
    const nextExpanded = isExpanded ? null : alertId;
    setExpandedId(nextExpanded);
    if (!isExpanded) {
      try {
        const [detail, evidence, rows] = await Promise.all([
          alertDetails[alertId] ? Promise.resolve(alertDetails[alertId]) : fetchAlertV2(alertId),
          alertEvidence[alertId] ? Promise.resolve(alertEvidence[alertId]) : fetchAlertEvidenceV2(alertId),
          alertActions[alertId] ? Promise.resolve(alertActions[alertId]) : fetchAlertActionsV2(alertId),
        ]);
        setAlertDetails((prev) => ({ ...prev, [alertId]: detail }));
        setAlertEvidence((prev) => ({ ...prev, [alertId]: evidence }));
        setAlertActions((prev) => ({ ...prev, [alertId]: rows }));
      } catch (error) {
        console.error("Failed to load alert detail", error);
      }
    }
  };

  const filteredAlerts = useMemo(() => {
    if (statusFilter === "all") return alerts;
    return alerts.filter((alert) => alert.status === statusFilter);
  }, [alerts, statusFilter]);

  if (!isMounted) return <div className="h-64 animate-pulse bg-panel-bg rounded-2xl" />;

  if (filteredAlerts.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full opacity-30 grayscale py-12">
        <Activity size={32} className="mb-4 text-text-muted/40" />
        <p className="text-[10px] font-black uppercase tracking-widest text-center text-text-muted">
          No Active Exposure Alerts
        </p>
      </div>
    );
  }

  return (
    <div className="flex h-full max-h-[800px] flex-col">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3 px-1 md:mb-8 md:px-2">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-lg bg-hazard/10 border border-hazard/20 flex items-center justify-center text-hazard">
            <AlertCircle size={18} />
          </div>
          <h3 className="text-sm font-black uppercase tracking-[0.2em] text-foreground">Exposure Alerts</h3>
        </div>
        {onRefresh ? (
          <div className="flex items-center gap-2">
            <select
              value={statusFilter}
              onChange={(event) => setStatusFilter(event.target.value)}
              className="rounded-xl border border-border bg-background/40 px-2 py-1.5 text-[9px] font-black uppercase tracking-widest text-text-muted outline-none"
            >
              {["all", "new", "review", "monitor", "escalated", "dismissed", "mitigated"].map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
            <button
              onClick={() => void onRefresh()}
              className="text-[9px] font-black text-text-muted hover:text-foreground uppercase tracking-widest transition-all"
            >
              Refresh
            </button>
          </div>
        ) : null}
      </div>

      <div className="custom-scrollbar flex-1 space-y-4 overflow-y-auto px-1 pb-8 md:px-2 md:pb-12">
        {filteredAlerts.map((alert, i) => {
          const isExpanded = expandedId === alert.id;
          const detail = alertDetails[alert.id] || alert;
          const risk = detail.metadata?.risk_score;
          const topExposure = detail.metadata?.top_exposure_match;
          const history = alertActions[alert.id] || [];
          const evidence = alertEvidence[alert.id] || [];
          const allowedActions: string[] =
            (workflowConfig?.transitions?.[detail.status] as string[] | undefined) ||
            ["review", "monitor", "escalated", "dismissed"];

          return (
            <motion.div
              key={alert.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
              className={`p-5 rounded-2xl border transition-all group relative overflow-hidden cursor-pointer ${severityClasses[alert.severity] || severityClasses.low}`}
              onClick={() => void handleExpand(alert.id, isExpanded)}
            >
              <div className="mb-3 flex flex-wrap items-start justify-between gap-2">
                <div className="flex min-w-0 flex-wrap items-center gap-2 sm:gap-3">
                  <span className="px-2 py-0.5 rounded text-[8px] font-black uppercase tracking-widest bg-background/50 text-primary border border-primary/20">
                    {detail.alert_type}
                  </span>
                  <span className="text-[10px] font-black text-foreground italic tracking-wider">
                    {detail.severity}
                  </span>
                </div>
                <div className="flex items-center gap-1.5 text-text-muted opacity-70">
                  <Clock size={10} />
                  <span className="text-[9px] font-bold">
                    {new Date(detail.triggered_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                  </span>
                </div>
              </div>

              <h4 className="wrap-pretty text-xs font-black text-foreground mb-2 leading-tight uppercase tracking-tight group-hover:text-primary transition-colors">
                {detail.headline}
              </h4>

              <p className="text-[10px] text-text-muted font-bold leading-relaxed mb-4">
                {buildExposureExplanation(detail)}
              </p>

              <div className="mb-4 grid grid-cols-1 gap-2 sm:grid-cols-3">
                <div className="rounded-xl border border-border bg-background/40 p-3">
                  <div className="text-[8px] font-black uppercase tracking-widest text-text-muted mb-1">Risk</div>
                  <div className="text-[11px] font-black text-foreground italic">
                    {risk?.score_value ? risk.score_value.toFixed(2) : "--"}
                  </div>
                </div>
                <div className="rounded-xl border border-border bg-background/40 p-3">
                  <div className="text-[8px] font-black uppercase tracking-widest text-text-muted mb-1">Confidence</div>
                  <div className="text-[11px] font-black text-foreground italic">
                    {risk?.confidence_score ? `${Math.round(risk.confidence_score * 100)}%` : "--"}
                  </div>
                </div>
                <div className="rounded-xl border border-border bg-background/40 p-3">
                  <div className="text-[8px] font-black uppercase tracking-widest text-text-muted mb-1">Status</div>
                  <div className="text-[11px] font-black text-foreground italic">{detail.status}</div>
                </div>
              </div>

              <AnimatePresence>
                {isExpanded ? (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="overflow-hidden"
                  >
                    <div className="space-y-4 mb-4">
                      {topExposure ? (
                        <div className="p-3 rounded-xl bg-primary/5 border border-primary/20">
                          <div className="flex items-center gap-2 mb-2">
                            <ArrowRightLeft size={12} className="text-primary" />
                            <span className="text-[8px] font-black text-primary uppercase tracking-widest">Exposure Path</span>
                          </div>
                          <p className="wrap-anywhere text-[9px] font-bold text-foreground leading-snug">
                            {(topExposure.source_object_name || humanizeToken(topExposure.source_object_id))}
                            {" "}
                            {relationToPhrase(topExposure.relationship_type)}
                            {" "}
                            {(topExposure.target_entity_name || "the mapped entity")}
                          </p>
                        </div>
                      ) : null}

                      {risk?.rationale_text ? (
                        <div className="p-3 rounded-xl bg-hazard/5 border border-hazard/20">
                          <div className="flex items-center gap-2 mb-2">
                            <ShieldAlert size={12} className="text-hazard" />
                            <span className="text-[8px] font-black text-hazard uppercase tracking-widest">Risk Rationale</span>
                          </div>
                          <p className="wrap-anywhere text-[9px] font-bold text-foreground italic leading-snug">{risk.rationale_text}</p>
                        </div>
                      ) : null}

                      {detail.recommended_action ? (
                        <div className="p-3 rounded-xl bg-background/40 border border-border">
                          <div className="flex items-center gap-2 mb-2">
                            <MessageSquare size={12} className="text-success" />
                            <span className="text-[8px] font-black text-success uppercase tracking-widest">Recommended Action</span>
                          </div>
                          <p className="wrap-anywhere text-[9px] font-bold text-foreground leading-snug">{detail.recommended_action}</p>
                        </div>
                      ) : null}

                      <div className="rounded-xl border border-border bg-background/40 p-3">
                        <div className="mb-2 flex items-center gap-2">
                          <FileText size={12} className="text-primary" />
                          <span className="text-[8px] font-black uppercase tracking-widest text-primary">Supporting Evidence</span>
                        </div>
                        {evidence.length ? (
                          <div className="space-y-2">
                            {evidence.slice(0, 4).map((row) => (
                              <div key={`${alert.id}-${row.document_id}`} className="rounded-xl border border-border/70 bg-panel-bg/30 p-3">
                                <div className="wrap-anywhere text-[9px] font-black text-foreground leading-snug">{row.title}</div>
                                <div className="mt-1 text-[8px] font-bold uppercase tracking-widest text-text-muted">
                                  {row.evidence_type || "event_support"}
                                  {typeof row.relevance_score === "number" ? ` / ${Math.round(row.relevance_score * 100)}% relevance` : ""}
                                </div>
                                {row.url ? (
                                  <a
                                    href={row.url}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="mt-2 inline-block text-[8px] font-black uppercase tracking-widest text-primary hover:underline"
                                  >
                                    Open source
                                  </a>
                                ) : null}
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-[9px] font-bold text-text-muted">No supporting evidence attached.</p>
                        )}
                      </div>

                      <div className="flex flex-wrap gap-2 pt-1">
                        {allowedActions.map((action) => {
                          const loading = actionLoading === `${alert.id}:${action}`;
                          return (
                            <button
                              key={action}
                              onClick={(event) => {
                                event.stopPropagation();
                                void handleAction(alert.id, action);
                              }}
                              className="rounded-xl border border-border bg-background/40 px-3 py-2 text-[8px] font-black uppercase tracking-widest text-text-muted transition-all hover:border-primary/30 hover:text-foreground"
                            >
                              {loading ? <Loader2 size={12} className="animate-spin" /> : action}
                            </button>
                          );
                        })}
                      </div>

                      <div className="rounded-xl border border-border bg-background/40 p-3">
                        <div className="mb-2 flex items-center gap-2">
                          <ListChecks size={12} className="text-primary" />
                          <span className="text-[8px] font-black uppercase tracking-widest text-primary">Action History</span>
                        </div>
                        {history.length ? (
                          <div className="space-y-2">
                            {history.slice(-4).reverse().map((row) => (
                              <div key={row.id} className="flex items-center justify-between gap-3 border-b border-border/50 pb-2 last:border-b-0 last:pb-0">
                                <div className="min-w-0">
                                  <div className="text-[8px] font-black uppercase tracking-widest text-foreground">{row.action_type}</div>
                                  <div className="text-[8px] font-bold text-text-muted">
                                    {row.actor_id || "system"}{row.notes ? ` - ${row.notes}` : ""}
                                  </div>
                                </div>
                                <div className="text-[8px] font-bold text-text-muted">
                                  {new Date(row.created_at).toLocaleDateString()}
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-[9px] font-bold text-text-muted">No actions recorded yet.</p>
                        )}
                      </div>
                    </div>
                  </motion.div>
                ) : null}
              </AnimatePresence>

              <div className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-border bg-foreground/5 p-3">
                <div className="flex min-w-0 flex-1 items-center gap-3">
                  <div className="h-6 w-6 rounded-lg bg-panel-bg flex-shrink-0 flex items-center justify-center border border-border text-primary">
                    <MessageSquare size={12} />
                  </div>
                  <p className="wrap-anywhere line-clamp-2 text-[9px] font-black text-text-muted uppercase tracking-tighter leading-snug italic">
                    {topExposure?.source_object_type ? `${topExposure.source_object_type} exposure mapped` : "Exposure-aware alert"}
                  </p>
                </div>
                <div className={`text-[8px] font-black uppercase tracking-widest px-2 py-1 rounded transition-colors ${isExpanded ? "text-foreground" : "text-text-muted hover:text-primary"}`}>
                  {isExpanded ? "Collapse" : "Inspect"}
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

export default AlertPulse;
