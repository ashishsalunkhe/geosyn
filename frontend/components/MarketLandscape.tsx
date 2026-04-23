"use client";

import React from "react";
import { motion } from "framer-motion";
import { 
  Globe, 
  TrendingUp, 
  AlertCircle, 
  ShieldCheck, 
  ExternalLink,
  ChevronRight,
  Target,
  Users
} from "lucide-react";
import { getSeverityTone, getStatusTone } from "@/lib/status-theme";

interface Scenario {
  id: string;
  topic: string;
  status: "EMERGING" | "ACTIVE" | "CRITICAL" | "STABILIZED" | "RESOLVING";
  region: string;
  sector: string;
  risk_score: number;
  community_interest?: string;
}

interface MarketLandscapeProps {
  scenarios: Scenario[];
  trending: Scenario[];
  alerts?: any[];
  onSelect: (topic: string) => void;
}

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

function buildExposureSummary(alert: any) {
  const topExposure = alert?.metadata?.top_exposure_match;
  if (!topExposure) {
    return alert?.summary_text || alert?.recommended_action || "Exposure-linked alert ready for review.";
  }

  const sourceName =
    topExposure.source_object_name ||
    humanizeToken(topExposure.source_object_id) ||
    "this mapped asset";
  const targetName =
    topExposure.target_entity_name ||
    alert?.headline ||
    "the related event";
  const relation = relationToPhrase(topExposure.relationship_type);

  return `${sourceName} could be affected because it ${relation} ${targetName}.`;
}

function buildExposureTrigger(alert: any) {
  const topExposure = alert?.metadata?.top_exposure_match;
  const targetName = topExposure?.target_entity_name || alert?.headline;
  if (!targetName) return "Exposure linked to a live risk event.";
  return `Triggered by ${targetName}.`;
}

function buildExposureAction(alert: any) {
  if (alert?.recommended_action) {
    return alert.recommended_action;
  }
  const severity = (alert?.severity || "").toLowerCase();
  const fallback: Record<string, string> = {
    critical: "Escalate now and confirm business continuity coverage.",
    high: "Review impact and assign an owner this shift.",
    medium: "Monitor closely and reassess within 24 hours.",
    low: "Track for changes before taking action.",
  };
  return fallback[severity] || "Review the mapped exposure and decide next steps.";
}

export default function MarketLandscape({ scenarios, trending, alerts = [], onSelect }: MarketLandscapeProps) {
  const watchAlerts = alerts.filter((a) => a.alert_type === "event_exposure" || a.metadata?.top_exposure_match);
  return (
    <div className="space-y-16 animate-in fade-in duration-1000">
      
      {/* Tracked Scenarios Grid */}
      <section>
        <div className="flex flex-wrap items-center justify-between gap-3 mb-8">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary rounded-xl text-white shadow-sm">
                <Target size={18} />
              </div>
              <div>
                <h3 className="text-sm font-black tracking-widest text-foreground uppercase italic">Active Portfolio Landscape</h3>
                <p className="text-[10px] font-bold text-text-muted uppercase tracking-tighter">Your Persistent Tactical Vault</p>
              </div>
            </div>
            <div className="text-[10px] font-black text-text-muted uppercase tracking-widest border border-border px-4 py-1.5 rounded-2xl bg-panel-bg shadow-sm">
                {scenarios.length} Tracked Records
            </div>
        </div>

        {scenarios.length === 0 ? (
          <div className="py-20 text-center glass-panel border-dashed border-border bg-panel-bg/40">
             <Target size={40} className="text-text-muted/20 mx-auto mb-4" />
             <p className="text-[10px] font-black text-text-muted uppercase tracking-widest italic">No tracked scenarios in current filter orbit.</p>
             <p className="text-[8px] font-bold text-text-muted/60 uppercase mt-2">Discover and follow topics from the global mesh.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {scenarios.map((s, idx) => (
              <ScenarioCard key={s.id} scenario={s} idx={idx} onClick={() => onSelect(s.topic)} />
            ))}
          </div>
        )}
      </section>

      {/* Global Community Discovery */}
      <section>
        <div className="flex flex-wrap items-center justify-between gap-3 mb-8">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-secondary rounded-xl text-primary border border-border">
                <Globe size={18} />
              </div>
              <div>
                <h3 className="text-sm font-black tracking-widest text-foreground uppercase italic">Community Discovery Feed</h3>
                <p className="text-[10px] font-bold text-text-muted uppercase tracking-tighter">Global Strategic Priorities (Simulated Community)</p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-[9px] font-black text-text-muted uppercase tracking-widest">
                <Users size={12} className="text-primary" /> Live Orbit Analysis
            </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-5">
          {trending.map((s, idx) => (
            <motion.div 
              key={s.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 + (idx * 0.1) }}
              onClick={() => onSelect(s.topic)}
              className="glass-panel min-h-[182px] p-5 bg-panel-bg border-border group hover:border-primary transition-all cursor-pointer relative overflow-hidden rounded-2xl shadow-sm flex flex-col"
            >
              <div className="mb-4">
                 <span className="block max-w-[70%] text-[10px] font-bold text-primary uppercase tracking-[0.18em] leading-snug">
                   {s.region} / {s.sector}
                 </span>
              </div>
              <div className="flex min-h-[84px] flex-1 items-center justify-center">
                <h4 className="mx-auto max-w-[12rem] wrap-pretty text-center text-[14px] font-black text-foreground italic uppercase tracking-tight leading-[1.08] group-hover:text-primary transition-colors">
                  {s.topic}
                </h4>
              </div>
              <div className="mt-4 flex justify-center">
                <div className={`rounded-md border px-2.5 py-1 text-[9px] font-bold flex items-center gap-1 leading-none transition-colors ${getStatusTone(s.status).pill}`}>
                  <TrendingUp size={8} /> {s.community_interest || "HIGH"} INTEREST
                </div>
              </div>
              <div className="absolute -bottom-2 -right-2 opacity-[0.03] group-hover:opacity-[0.08] transition-opacity pointer-events-none">
                 <Globe size={80} />
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Strategic Market Assets to Watch */}
      <section>
        <div className="flex flex-wrap items-center justify-between gap-3 mb-8">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-hazard/20 border border-hazard/30 rounded-xl text-hazard shadow-sm">
                <AlertCircle size={18} />
              </div>
              <div>
                <h3 className="text-sm font-black tracking-widest text-foreground uppercase italic">Assets & Commodities Watchlist</h3>
                <p className="text-[10px] font-bold text-text-muted uppercase tracking-tighter">High-Volatility Tickers with Historical Differences</p>
              </div>
            </div>
            <div className="text-[10px] font-black text-text-muted uppercase tracking-widest border border-border px-4 py-1.5 rounded-2xl bg-panel-bg shadow-sm">
                {watchAlerts.length} Exposure Alerts
            </div>
        </div>

        {watchAlerts.length === 0 ? (
          <div className="py-20 text-center glass-panel border-dashed border-border bg-panel-bg/40">
             <TrendingUp size={40} className="text-text-muted/20 mx-auto mb-4" />
             <p className="text-[10px] font-black text-text-muted uppercase tracking-widest italic">No significant market deviations detected.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
            {watchAlerts
              .slice(0, 8)
              .map((alert, idx) => {
                const topExposure = alert.metadata?.top_exposure_match;
                const diff = topExposure?.exposure_weight || alert.metadata?.risk_score?.score_value || 0;
                const severityTone = getSeverityTone(alert.severity);
                return (
                  <motion.div 
                    key={alert.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 * idx }}
                    className="glass-panel min-h-[270px] p-6 bg-panel-bg border-border group hover:border-border/80 transition-all rounded-2xl shadow-sm relative overflow-hidden flex flex-col"
                  >
                    <div className="mb-5 flex items-start justify-between gap-4">
                       <div className="min-w-0 flex-1">
                           <span className="block text-[10px] font-bold text-text-muted tracking-[0.18em] uppercase leading-snug mb-2">
                               {humanizeToken(topExposure?.source_object_type || alert.alert_type)}
                            </span>
                           <h4 className={`wrap-pretty text-center text-[16px] font-black italic uppercase tracking-tight leading-[1.06] transition-colors ${severityTone.text}`}>
                               {topExposure?.source_object_name || alert.headline}
                            </h4>
                       </div>
                       <div className={`shrink-0 text-[18px] leading-none font-black px-3 py-2 rounded-xl border ${severityTone.pill}`}>
                           {(diff * 100).toFixed(0)}%
                       </div>
                    </div>
                    <div className="flex flex-1 items-center justify-center py-4">
                      <div className="mx-auto max-w-[13rem]">
                        <h4 className={`wrap-pretty text-center text-[16px] font-black italic uppercase tracking-tight leading-[1.08] ${severityTone.text}`}>
                          {topExposure?.source_object_name || alert.headline}
                        </h4>
                      </div>
                    </div>
                    <div className="mt-auto space-y-3 border-t border-border/60 pt-4">
                      <div>
                        <div className="mb-1 text-[9px] font-bold uppercase tracking-[0.14em] text-text-muted/70">What changed</div>
                        <p className="wrap-pretty text-[12px] font-semibold leading-relaxed text-foreground/90">
                          {buildExposureTrigger(alert)}
                        </p>
                      </div>
                      <div>
                        <div className="mb-1 text-[9px] font-bold uppercase tracking-[0.14em] text-text-muted/70">Suggested response</div>
                        <p className="wrap-pretty text-[12px] font-semibold leading-relaxed text-text-muted/90">
                          {buildExposureAction(alert)}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                );
            })}
          </div>
        )}
      </section>

    </div>
  );
}

function ScenarioCard({ scenario, idx, onClick }: { scenario: Scenario, idx: number, onClick: () => void }) {
  const statusTone = getStatusTone(scenario.status);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: idx * 0.1 }}
      onClick={onClick}
      className="glass-panel min-h-[220px] p-6 bg-panel-bg border-border group hover:border-primary transition-all cursor-pointer relative overflow-hidden flex flex-col rounded-2xl shadow-sm"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
            <span className="block text-[9px] font-bold text-text-muted tracking-[0.14em] uppercase leading-snug mb-2">
              {scenario.region} // {scenario.sector}
            </span>
        </div>
        <div className={`shrink-0 rounded-xl px-3 py-2 text-[9px] font-bold tracking-[0.12em] transition-all border leading-none ${statusTone.pill}`}>
            {scenario.status}
        </div>
      </div>

      <div className="flex flex-1 items-center justify-center py-6">
        <h4 className="mx-auto max-w-[13rem] wrap-pretty text-center text-[15px] font-black text-foreground italic uppercase tracking-tight leading-[1.08] group-hover:text-primary transition-colors">
          {scenario.topic}
        </h4>
      </div>

      <div className="mt-auto space-y-4 border-t border-border/60 pt-4">
        <div className="flex justify-between items-end">
            <div className="flex flex-col gap-1">
               <span className="text-[8px] font-bold text-text-muted uppercase tracking-[0.14em]">Tactical Risk Score</span>
               <div className="flex items-center gap-2">
                  <div className={`text-xl font-black italic ${scenario.risk_score > 0.7 ? 'text-error' : statusTone.text}`}>
                    {(scenario.risk_score * 100).toFixed(0)}%
                  </div>
                  <div className="h-1 w-16 bg-secondary rounded-full overflow-hidden">
                     <div className={`h-full ${scenario.risk_score > 0.7 ? 'bg-error' : statusTone.solid}`} style={{ width: `${scenario.risk_score * 100}%` }} />
                  </div>
               </div>
            </div>
            <div className="p-2 border border-border rounded-xl text-text-muted group-hover:text-primary group-hover:border-primary transition-all bg-secondary/30">
               <ChevronRight size={16} />
            </div>
        </div>
      </div>

      {/* Aesthetic Background Pattern */}
      <div className="absolute -bottom-4 -right-4 opacity-[0.03] group-hover:opacity-[0.08] transition-opacity pointer-events-none">
         {scenario.status === 'CRITICAL' ? <AlertCircle size={100} /> : <ShieldCheck size={100} />}
      </div>
    </motion.div>
  );
}
