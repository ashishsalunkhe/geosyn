"use client";

import React, { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  Building2,
  CheckCircle2,
  Clock3,
  ExternalLink,
  Eye,
  Flag,
  Link2,
  Shield,
  Target,
  X,
} from "lucide-react";
import {
  createEventEvaluation,
  fetchEventEvaluation,
  fetchEventExposure,
  fetchEventTimeline,
  fetchEventV2,
  type EventEvaluationLabel,
  type EventExposureExplanation,
  type EventTimelineItem,
  type EventV2,
} from "@/lib/api";

interface EventDetailPanelProps {
  eventId: string | null;
  fallbackEvents?: EventV2[];
  onClose: () => void;
  onAnalyze: (topic: string) => void;
}

const severityTone: Record<string, string> = {
  critical: "text-error",
  high: "text-hazard",
  medium: "text-primary",
  low: "text-success",
};

export default function EventDetailPanel({ eventId, fallbackEvents = [], onClose, onAnalyze }: EventDetailPanelProps) {
  const [eventDetail, setEventDetail] = useState<EventV2 | null>(null);
  const [exposure, setExposure] = useState<EventExposureExplanation | null>(null);
  const [timeline, setTimeline] = useState<EventTimelineItem[]>([]);
  const [evaluation, setEvaluation] = useState<EventEvaluationLabel[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actionKey, setActionKey] = useState<string | null>(null);

  const fallbackEvent = useMemo(
    () => fallbackEvents.find((item) => item.id === eventId) || null,
    [eventId, fallbackEvents],
  );

  useEffect(() => {
    if (!eventId) {
      setEventDetail(null);
      setExposure(null);
      setTimeline([]);
      setEvaluation([]);
      setError(null);
      return;
    }

    let cancelled = false;
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const [detail, exposureSummary, timelineRows, evaluationRows] = await Promise.all([
          fetchEventV2(eventId),
          fetchEventExposure(eventId),
          fetchEventTimeline(eventId),
          fetchEventEvaluation(eventId),
        ]);
        if (cancelled) return;
        setEventDetail(detail);
        setExposure(exposureSummary);
        setTimeline(timelineRows);
        setEvaluation(evaluationRows);
      } catch (loadError) {
        if (cancelled) return;
        console.error("Failed to load event review panel", loadError);
        setError("Event review data could not be loaded.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    void load();
    return () => {
      cancelled = true;
    };
  }, [eventId]);

  const resolvedEvent = eventDetail || fallbackEvent;
  const risk = exposure?.risk_score || resolvedEvent?.risk_score || null;
  const watchlists = exposure?.matched_watchlists || resolvedEvent?.matched_watchlists || [];
  const exposures = exposure?.exposure_matches || resolvedEvent?.exposure_matches || [];
  const documents = resolvedEvent?.documents || [];
  const entities = resolvedEvent?.entities || [];
  const headline = resolvedEvent?.canonical_title || "Select an event";

  const quickLabel = async (label_type: string, label_value: string) => {
    if (!eventId) return;
    const key = `${eventId}:${label_type}:${label_value}`;
    try {
      setActionKey(key);
      await createEventEvaluation(eventId, { label_type, label_value, labeled_by: "frontend-user" });
      const rows = await fetchEventEvaluation(eventId);
      setEvaluation(rows);
    } catch (labelError) {
      console.error("Failed to create event evaluation", labelError);
    } finally {
      setActionKey(null);
    }
  };

  if (!eventId) {
    return (
      <div className="glass-panel flex min-h-[520px] flex-col items-center justify-center border-dashed border-border p-8 text-center">
        <Target className="mb-4 text-text-muted/40" size={44} />
        <h3 className="text-sm font-black uppercase tracking-widest text-foreground">Event Review</h3>
        <p className="mt-3 max-w-sm text-[11px] font-bold leading-relaxed text-text-muted">
          Select an event from the mesh to review exposure, watchlist matches, supporting evidence, timeline progression, and analyst feedback in one place.
        </p>
      </div>
    );
  }

  return (
    <section className="glass-panel min-h-[520px] overflow-hidden border-primary/10">
      <div className="flex items-start justify-between gap-4 border-b border-border px-4 py-4 md:px-5">
        <div className="min-w-0">
          <div className="mb-2 flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-1 rounded-full border border-primary/20 bg-primary/10 px-2 py-1 text-[8px] font-black uppercase tracking-widest text-primary">
              <Eye size={10} />
              Review Workspace
            </span>
            {risk?.severity ? (
              <span className={`text-[8px] font-black uppercase tracking-widest ${severityTone[risk.severity] || "text-primary"}`}>
                {risk.severity}
              </span>
            ) : null}
          </div>
          <h3 className="wrap-pretty text-sm font-black uppercase italic leading-tight text-foreground sm:text-base">{headline}</h3>
          <p className="mt-2 text-[10px] font-bold leading-relaxed text-text-muted">
            {exposure?.summary || resolvedEvent?.summary_text || resolvedEvent?.exposure_summary || "Exposure-aware canonical event under analyst review."}
          </p>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="rounded-xl border border-border bg-panel-bg/60 p-2 text-text-muted transition-all hover:border-primary/30 hover:text-primary"
          aria-label="Close event review"
        >
          <X size={14} />
        </button>
      </div>

      <div className="max-h-[calc(100vh-15rem)] space-y-4 overflow-y-auto p-4 custom-scrollbar md:p-5">
        {loading ? (
          <div className="rounded-2xl border border-border bg-background/30 p-4 text-[10px] font-black uppercase tracking-widest text-text-muted">
            Loading event review...
          </div>
        ) : null}

        {error ? (
          <div className="rounded-2xl border border-error/20 bg-error/5 p-4 text-[10px] font-black uppercase tracking-widest text-error">
            {error}
          </div>
        ) : null}

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          <StatCard label="Risk Score" value={risk?.score_value ? risk.score_value.toFixed(2) : "--"} icon={Shield} />
          <StatCard label="Exposure Hits" value={String(exposures.length)} icon={Link2} />
          <StatCard label="Timeline Rows" value={String(timeline.length || resolvedEvent?.timeline_count || 0)} icon={Clock3} />
        </div>

        <div className="rounded-2xl border border-primary/20 bg-primary/5 p-4">
          <div className="mb-2 flex items-center gap-2">
            <AlertTriangle size={13} className="text-primary" />
            <span className="text-[8px] font-black uppercase tracking-widest text-primary">Exposure Summary</span>
          </div>
          {exposures.length ? (
            <div className="space-y-2">
              {exposures.slice(0, 4).map((item) => (
                <div key={item.id} className="rounded-xl border border-primary/10 bg-background/20 p-3">
                  <div className="wrap-anywhere text-[9px] font-black uppercase tracking-widest text-foreground">
                    {item.source_object_name || item.source_object_id}
                  </div>
                  <div className="wrap-anywhere mt-1 text-[9px] font-bold leading-relaxed text-text-muted">
                    {item.relationship_type} {"->"} {item.target_entity_name || item.target_entity_id || "mapped entity"}
                  </div>
                  <div className="mt-2 flex flex-wrap gap-2 text-[8px] font-black uppercase tracking-widest text-primary">
                    {typeof item.criticality_score === "number" ? <span>{Math.round(item.criticality_score * 100)}% criticality</span> : null}
                    {typeof item.confidence_score === "number" ? <span>{Math.round(item.confidence_score * 100)}% confidence</span> : null}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-[10px] font-bold text-text-muted">No customer exposure matches were found for this event.</p>
          )}
        </div>

        <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
          <DetailSection title="Watchlist Matches" icon={Target}>
            {watchlists.length ? (
              <div className="flex flex-wrap gap-2">
                {watchlists.map((item, index) => (
                  <span
                    key={`${item.watchlist_id}-${item.entity_id || index}`}
                    className="inline-flex items-center gap-1 rounded-full border border-primary/20 bg-primary/10 px-2 py-1 text-[8px] font-black uppercase tracking-widest text-primary"
                  >
                    {item.item_type}
                    {typeof item.criticality_score === "number" ? ` ${Math.round(item.criticality_score * 100)}%` : ""}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-[10px] font-bold text-text-muted">No watchlist matches were recorded.</p>
            )}
          </DetailSection>

          <DetailSection title="Linked Entities" icon={Building2}>
            {entities.length ? (
              <div className="flex flex-wrap gap-2">
                {entities.slice(0, 10).map((entity) => (
                  <span
                    key={entity.id}
                    className="inline-flex items-center gap-1 rounded-full border border-border bg-panel-bg/30 px-2 py-1 text-[8px] font-black uppercase tracking-widest text-text-muted"
                  >
                    <span className="wrap-anywhere">{entity.canonical_name}</span>
                    <span className="text-primary">{entity.entity_type}</span>
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-[10px] font-bold text-text-muted">No linked entities are available for review.</p>
            )}
          </DetailSection>
        </div>

        <DetailSection title="Supporting Evidence" icon={ExternalLink}>
          {documents.length ? (
            <div className="space-y-2">
              {documents.slice(0, 6).map((doc) => (
                <div key={doc.id} className="rounded-xl border border-border bg-background/30 p-3">
                  <div className="wrap-anywhere text-[10px] font-black leading-snug text-foreground">{doc.title}</div>
                  <div className="mt-1 text-[8px] font-bold uppercase tracking-widest text-text-muted">
                    {doc.published_at ? new Date(doc.published_at).toLocaleDateString() : "Unknown date"}
                    {doc.is_primary ? " / primary evidence" : ""}
                  </div>
                  {doc.url ? (
                    <a
                      href={doc.url}
                      target="_blank"
                      rel="noreferrer"
                      className="mt-2 inline-flex items-center gap-1 text-[8px] font-black uppercase tracking-widest text-primary hover:underline"
                    >
                      Open source
                      <ExternalLink size={10} />
                    </a>
                  ) : null}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-[10px] font-bold text-text-muted">No supporting documents are attached yet.</p>
          )}
        </DetailSection>

        <DetailSection title="Timeline" icon={Clock3}>
          {timeline.length ? (
            <div className="space-y-3">
              {timeline.slice(0, 6).map((item) => (
                <div key={item.id} className="border-l border-primary/30 pl-3">
                  <div className="text-[8px] font-black uppercase tracking-widest text-text-muted">
                    {item.occurred_at ? new Date(item.occurred_at).toLocaleDateString() : "No date"}
                  </div>
                  <div className="mt-1 text-[10px] font-black text-foreground">{item.title}</div>
                  <div className="text-[9px] leading-relaxed text-text-muted">{item.description}</div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-[10px] font-bold text-text-muted">No timeline items are available for this event.</p>
          )}
        </DetailSection>

        <DetailSection title="Analyst Evaluation" icon={Flag}>
          <div className="flex flex-wrap gap-2">
            {[
              { label_type: "event_was_material", label_value: "true", label: "Mark Material" },
              { label_type: "alert_was_useful", label_value: "true", label: "Mark Useful" },
              { label_type: "false_positive", label_value: "true", label: "False Positive" },
            ].map((action) => {
              const loadingAction = actionKey === `${eventId}:${action.label_type}:${action.label_value}`;
              return (
                <button
                  key={action.label_type}
                  type="button"
                  onClick={() => void quickLabel(action.label_type, action.label_value)}
                  className="rounded-xl border border-border bg-panel-bg px-3 py-2 text-[8px] font-black uppercase tracking-widest text-text-muted transition-all hover:border-primary/30 hover:text-foreground"
                >
                  {loadingAction ? "Saving..." : action.label}
                </button>
              );
            })}
            {resolvedEvent ? (
              <button
                type="button"
                onClick={() => onAnalyze(resolvedEvent.canonical_title)}
                className="rounded-xl border border-primary/20 bg-primary/10 px-3 py-2 text-[8px] font-black uppercase tracking-widest text-primary transition-all hover:bg-primary/15"
              >
                Open Intel Brief
              </button>
            ) : null}
          </div>

          {evaluation.length ? (
            <div className="mt-4 flex flex-wrap gap-2">
              {evaluation.map((row) => (
                <span
                  key={row.id}
                  className="inline-flex items-center gap-1 rounded-full border border-success/20 bg-success/10 px-2 py-1 text-[8px] font-black uppercase tracking-widest text-success"
                >
                  <CheckCircle2 size={10} />
                  {row.label_type}:{row.label_value}
                </span>
              ))}
            </div>
          ) : (
            <p className="mt-3 text-[10px] font-bold text-text-muted">No analyst feedback has been recorded yet.</p>
          )}
        </DetailSection>
      </div>
    </section>
  );
}

function StatCard({
  icon: Icon,
  label,
  value,
}: {
  icon: React.ComponentType<{ size?: number; className?: string }>;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-2xl border border-border bg-background/30 p-3">
      <div className="mb-1 flex items-center gap-2">
        <Icon size={11} className="text-primary" />
        <span className="text-[8px] font-black uppercase tracking-widest text-text-muted">{label}</span>
      </div>
      <div className="text-[11px] font-black italic text-foreground">{value}</div>
    </div>
  );
}

function DetailSection({
  title,
  icon: Icon,
  children,
}: {
  title: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-border bg-background/30 p-4">
      <div className="mb-3 flex items-center gap-2">
        <Icon size={12} className="text-primary" />
        <span className="text-[8px] font-black uppercase tracking-widest text-primary">{title}</span>
      </div>
      {children}
    </div>
  );
}
