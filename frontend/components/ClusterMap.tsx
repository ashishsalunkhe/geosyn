"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Shield, Target, AlertTriangle, MessageSquare, ChevronRight, BarChart3, Radar, Network, Clock3, CheckCircle2, Flag } from "lucide-react";
import { createEventEvaluation, fetchEventEvaluation, fetchEventTimeline, type EventEvaluationLabel, type EventTimelineItem, type EventV2 } from "@/lib/api";

interface EventClusterProps {
  clusters: EventV2[];
  onAnalyze: (topic: string) => void;
}

const severityTone: Record<string, string> = {
  critical: "text-error",
  high: "text-hazard",
  medium: "text-primary",
  low: "text-success",
};

export default function ClusterMap({ clusters, onAnalyze }: EventClusterProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [timelines, setTimelines] = useState<Record<string, EventTimelineItem[]>>({});
  const [evaluations, setEvaluations] = useState<Record<string, EventEvaluationLabel[]>>({});
  const [loadingId, setLoadingId] = useState<string | null>(null);
  const [actionId, setActionId] = useState<string | null>(null);

  const loadDetail = async (eventId: string) => {
    if (timelines[eventId] && evaluations[eventId]) return;
    setLoadingId(eventId);
    try {
      const [timelineRows, evaluationRows] = await Promise.all([
        fetchEventTimeline(eventId),
        fetchEventEvaluation(eventId),
      ]);
      setTimelines((prev) => ({ ...prev, [eventId]: timelineRows }));
      setEvaluations((prev) => ({ ...prev, [eventId]: evaluationRows }));
    } catch (error) {
      console.error("Failed to load event detail", error);
    } finally {
      setLoadingId(null);
    }
  };

  const toggleExpand = async (eventId: string) => {
    if (expandedId === eventId) {
      setExpandedId(null);
      return;
    }
    setExpandedId(eventId);
    await loadDetail(eventId);
  };

  const quickLabel = async (eventId: string, label_type: string, label_value: string) => {
    try {
      setActionId(`${eventId}:${label_type}:${label_value}`);
      await createEventEvaluation(eventId, { label_type, label_value, labeled_by: "frontend-user" });
      const rows = await fetchEventEvaluation(eventId);
      setEvaluations((prev) => ({ ...prev, [eventId]: rows }));
    } catch (error) {
      console.error("Failed to create evaluation label", error);
    } finally {
      setActionId(null);
    }
  };

  if (!clusters || clusters.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-20 glass-panel border-dashed border-border">
        <Target className="text-text-muted/40 mb-4 animate-pulse" size={48} />
        <h3 className="text-sm font-black text-text-muted uppercase tracking-widest italic">
          No Canonical Events Yet
        </h3>
        <p className="text-[10px] text-text-muted/60 mt-2 text-center max-w-xs uppercase leading-loose">
          The system is reading global news, mapping evidence into canonical events, and attaching exposure context.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="mb-8 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="min-w-0">
          <h2 className="text-lg font-black tracking-tight text-foreground uppercase italic sm:text-xl">Canonical Event Mesh</h2>
          <p className="text-[10px] font-bold text-primary tracking-widest uppercase italic mt-1">Risk, Exposure, Timeline, Evaluation</p>
        </div>
        <div className="flex w-full items-center gap-3 rounded-xl border border-border bg-panel-bg px-4 py-2 shadow-sm sm:w-auto">
          <div className="flex flex-col">
            <span className="text-[7px] font-black text-foreground uppercase">Active Events</span>
            <span className="text-[10px] font-black text-success italic uppercase tracking-widest">{clusters.length}</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-5 md:grid-cols-2 xl:gap-6">
        {clusters.map((cluster, idx) => {
          const isExpanded = expandedId === cluster.id;
          const timeline = timelines[cluster.id] || [];
          const evaluation = evaluations[cluster.id] || [];
          return (
            <motion.div
              key={cluster.id || idx}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.06 }}
              className="glass-panel p-4 bg-panel-bg shadow-sm rounded-2xl border border-border group hover:border-primary transition-all relative overflow-hidden"
            >
              <div className="relative z-10 mb-3 flex flex-wrap items-center justify-between gap-2">
                <div className="flex min-w-0 items-center gap-2">
                  <div className="p-1.5 bg-primary/20 rounded-lg">
                    <Shield size={12} className="text-primary" />
                  </div>
                  <span className="text-[9px] font-black text-foreground uppercase tracking-widest">
                    {new Date(cluster.last_seen_at || cluster.first_seen_at || Date.now()).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" })}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-[8px] font-black uppercase tracking-widest ${severityTone[cluster.risk_score?.severity || "medium"] || "text-primary"}`}>
                    {cluster.risk_score?.severity || cluster.status}
                  </span>
                  <span className="text-[9px] font-black text-foreground italic">
                    {cluster.risk_score?.score_value ? `${Math.round(cluster.risk_score.score_value * 100)}%` : "N/A"}
                  </span>
                </div>
              </div>

              <h3 className="mb-2 text-sm font-black uppercase italic leading-tight tracking-tight text-foreground transition-colors group-hover:text-primary sm:text-[15px]">
                {cluster.canonical_title}
              </h3>

              <p className="text-[10px] font-bold text-text-muted leading-relaxed line-clamp-2 mb-4">
                {cluster.summary_text || cluster.exposure_summary || "Strategically significant event requiring exposure-aware evaluation."}
              </p>

              <div className="mb-4 grid grid-cols-1 gap-2 sm:grid-cols-3">
                <MetricCard icon={Radar} label="Risk" value={cluster.risk_score?.score_value ? cluster.risk_score.score_value.toFixed(2) : "--"} />
                <MetricCard icon={BarChart3} label="Evidence" value={String(cluster.document_count)} />
                <MetricCard icon={Network} label="Exposure" value={String(cluster.exposure_matches?.length || 0)} />
              </div>

              {cluster.exposure_matches?.length ? (
                <div className="mb-4 rounded-xl border border-primary/20 bg-primary/5 p-3">
                  <div className="flex items-center gap-2 mb-1">
                    <AlertTriangle size={11} className="text-primary" />
                    <span className="text-[8px] font-black uppercase tracking-widest text-primary">Top Exposure Path</span>
                  </div>
                  <p className="text-[9px] font-bold text-foreground leading-snug">
                    {(cluster.exposure_matches[0].source_object_name || cluster.exposure_matches[0].source_object_id)}
                    {" -> "}
                    {cluster.exposure_matches[0].relationship_type}
                    {" -> "}
                    {cluster.exposure_matches[0].target_entity_name || "mapped entity"}
                  </p>
                </div>
              ) : null}

              <AnimatePresence>
                {isExpanded ? (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="overflow-hidden"
                  >
                    <div className="space-y-4 mb-4 pt-4 border-t border-border">
                      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                        <div className="rounded-xl border border-border bg-background/40 p-3">
                          <div className="text-[8px] font-black uppercase tracking-widest text-text-muted mb-1">Timeline</div>
                          <div className="text-[11px] font-black text-foreground italic">{cluster.timeline_count}</div>
                        </div>
                        <div className="rounded-xl border border-border bg-background/40 p-3">
                          <div className="text-[8px] font-black uppercase tracking-widest text-text-muted mb-1">Evaluations</div>
                          <div className="text-[11px] font-black text-foreground italic">{evaluation.length}</div>
                        </div>
                      </div>

                      <div className="rounded-xl border border-border bg-background/40 p-3">
                        <div className="flex items-center gap-2 mb-2">
                          <Clock3 size={12} className="text-primary" />
                          <span className="text-[8px] font-black uppercase tracking-widest text-primary">Timeline Sample</span>
                        </div>
                        {loadingId === cluster.id ? (
                          <p className="text-[9px] font-bold text-text-muted uppercase tracking-widest">Loading timeline...</p>
                        ) : timeline.length ? (
                          <div className="space-y-2">
                            {timeline.slice(0, 3).map((item) => (
                              <div key={item.id} className="border-l border-primary/30 pl-3">
                                <div className="text-[8px] font-black uppercase tracking-widest text-text-muted">
                                  {item.occurred_at ? new Date(item.occurred_at).toLocaleDateString() : "No date"}
                                </div>
                                <div className="text-[9px] font-black text-foreground">{item.title}</div>
                                <div className="text-[9px] text-text-muted leading-snug">{item.description}</div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-[9px] font-bold text-text-muted">No timeline rows yet.</p>
                        )}
                      </div>

                      <div className="rounded-xl border border-border bg-background/40 p-3">
                        <div className="flex items-center gap-2 mb-2">
                          <Flag size={12} className="text-success" />
                          <span className="text-[8px] font-black uppercase tracking-widest text-success">Evaluation Actions</span>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {[
                            { label_type: "event_was_material", label_value: "true", label: "Material" },
                            { label_type: "alert_was_useful", label_value: "true", label: "Useful" },
                            { label_type: "false_positive", label_value: "true", label: "False Positive" },
                          ].map((action) => {
                            const loading = actionId === `${cluster.id}:${action.label_type}:${action.label_value}`;
                            return (
                              <button
                                key={action.label_type}
                                onClick={() => void quickLabel(cluster.id, action.label_type, action.label_value)}
                                className="px-3 py-2 rounded-xl border border-border bg-panel-bg text-[8px] font-black uppercase tracking-widest text-text-muted hover:text-foreground hover:border-primary/30 transition-all"
                              >
                                {loading ? "Saving..." : action.label}
                              </button>
                            );
                          })}
                        </div>
                        {evaluation.length ? (
                          <div className="mt-3 flex flex-wrap gap-2">
                            {evaluation.slice(0, 4).map((row) => (
                              <span key={row.id} className="inline-flex items-center gap-1 rounded-full border border-success/20 bg-success/10 px-2 py-1 text-[8px] font-black uppercase tracking-widest text-success">
                                <CheckCircle2 size={10} />
                                {row.label_type}:{row.label_value}
                              </span>
                            ))}
                          </div>
                        ) : null}
                      </div>
                    </div>
                  </motion.div>
                ) : null}
              </AnimatePresence>

              <div className="relative z-10 flex flex-wrap items-center gap-3 border-t border-border pt-4">
                <div className="flex items-center gap-1.5">
                  <BarChart3 size={11} className="text-success" />
                  <span className="text-[9px] font-black text-success uppercase tracking-tighter italic">{cluster.timeline_count || 0} Timeline</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <MessageSquare size={11} className="text-text-muted" />
                  <span className="text-[9px] font-black text-text-muted uppercase tracking-tighter">{cluster.entity_count} Entities</span>
                </div>
                <button
                  className="flex items-center gap-1 sm:ml-auto group/btn"
                  onClick={() => void toggleExpand(cluster.id)}
                >
                  <span className="text-[8px] font-black uppercase tracking-widest text-primary opacity-0 group-hover:opacity-100 transition-opacity">
                    {isExpanded ? "Collapse" : "Inspect"}
                  </span>
                  <ChevronRight size={14} className={`text-primary transition-transform ${isExpanded ? "rotate-90" : "group-hover:translate-x-0.5"}`} />
                </button>
                <button className="flex items-center gap-1 group/btn" onClick={() => onAnalyze(cluster.canonical_title)}>
                  <span className="text-[8px] font-black uppercase tracking-widest text-primary opacity-0 group-hover:opacity-100 transition-opacity">Analyze</span>
                  <ChevronRight size={14} className="text-primary group-hover:translate-x-0.5 transition-transform" />
                </button>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}

function MetricCard({ icon: Icon, label, value }: { icon: React.ComponentType<{ size?: number; className?: string }>; label: string; value: string }) {
  return (
    <div className="rounded-xl border border-border bg-background/40 p-3">
      <div className="flex items-center gap-2 mb-1">
        <Icon size={11} className="text-primary" />
        <span className="text-[8px] font-black uppercase tracking-widest text-text-muted">{label}</span>
      </div>
      <div className="text-[11px] font-black text-foreground italic">{value}</div>
    </div>
  );
}
