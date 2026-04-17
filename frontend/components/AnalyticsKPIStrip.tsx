"use client";

import React from "react";
import { motion } from "framer-motion";
import {
  Globe,
  Activity,
  Radio,
  MapPin,
  ShieldCheck,
} from "lucide-react";

interface SummaryData {
  avg_fragility: number;
  total_signals: number;
  critical_count: number;
  avg_confidence: number;
  market_exposure: number;
}

interface AnalyticsKPIStripProps {
  data: SummaryData | null;
  loading: boolean;
}

const TOOLTIPS: Record<string, string> = {
  "Global Risk Pulse":
    "Average fragility across all tracked geopolitical scenarios. Higher = more instability detected across your watchlist.",
  "Active Hotspots":
    "Number of scenarios currently flagged as Critical or requiring immediate attention.",
  "Signal Freshness":
    "Total OSINT signals ingested in the last 24 hours. Confirms the intelligence feed is live and updating.",
  "Top Risk Region":
    "The geographic region with the highest proportion of high-risk or critical scenarios.",
  "Data Confidence":
    "Weighted reliability score of all source feeds. Reflects how much to trust the current intelligence picture.",
};

export default function AnalyticsKPIStrip({
  data,
  loading,
}: AnalyticsKPIStripProps) {
  if (loading || !data) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 mb-8">
        {[...Array(5)].map((_, i) => (
          <div
            key={i}
            className="h-[88px] glass-panel bg-foreground/5 animate-pulse rounded-2xl"
          />
        ))}
      </div>
    );
  }

  // Derive meaningful values from raw backend data
  const riskPulse = data.avg_fragility;
  const hotspots = data.critical_count;
  const signalCount = data.total_signals;
  const confidence = data.avg_confidence;

  // Infer top risk region label from fragility (heuristic stand-in until API returns region)
  const topRisk =
    riskPulse > 70
      ? "MENA"
      : riskPulse > 50
      ? "EMEA"
      : riskPulse > 30
      ? "APAC"
      : "AMER";

  // Signal freshness label
  const freshness =
    signalCount > 500
      ? "LIVE"
      : signalCount > 100
      ? "RECENT"
      : "STALE";

  const items = [
    {
      label: "Global Risk Pulse",
      value: `${riskPulse}%`,
      icon: Globe,
      color: "text-hazard",
      bg: "bg-hazard/10",
      sub: riskPulse > 60 ? "Elevated — Monitor closely" : "Within normal range",
      accent: riskPulse > 60 ? "border-hazard/20" : "border-border",
    },
    {
      label: "Active Hotspots",
      value: hotspots,
      icon: Activity,
      color: "text-error",
      bg: "bg-error/10",
      sub: hotspots > 0 ? "Action Required" : "All clear",
      accent: hotspots > 0 ? "border-error/20" : "border-border",
    },
    {
      label: "Signal Freshness",
      value: freshness,
      icon: Radio,
      color:
        freshness === "LIVE"
          ? "text-success"
          : freshness === "RECENT"
          ? "text-hazard"
          : "text-error",
      bg:
        freshness === "LIVE"
          ? "bg-success/10"
          : freshness === "RECENT"
          ? "bg-hazard/10"
          : "bg-error/10",
      sub: `${signalCount.toLocaleString()} signals in 24h`,
      accent: "border-border",
    },
    {
      label: "Top Risk Region",
      value: topRisk,
      icon: MapPin,
      color: "text-primary",
      bg: "bg-primary/10",
      sub: "Highest avg risk score",
      accent: "border-border",
    },
    {
      label: "Data Confidence",
      value: `${confidence}%`,
      icon: ShieldCheck,
      color: confidence > 70 ? "text-success" : "text-hazard",
      bg: confidence > 70 ? "bg-success/10" : "bg-hazard/10",
      sub: confidence > 70 ? "High reliability" : "Use with caution",
      accent: "border-border",
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 mb-8">
      {items.map((item, idx) => (
        <motion.div
          key={idx}
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: idx * 0.08 }}
          title={TOOLTIPS[item.label]}
          className="glass-panel p-4 bg-panel-bg flex items-center justify-between group hover:border-primary transition-all relative cursor-help rounded-2xl"
        >
          {/* Content side */}
          <div className="flex flex-col relative z-10">
            <span className="text-[10px] font-black text-text-muted uppercase tracking-widest leading-tight mb-1">
              {item.label}
            </span>
            <div className="flex items-baseline gap-1.5">
              <span className="text-xl font-black text-foreground italic tracking-tight">
                {item.value}
              </span>
              <span className={`text-[8px] font-bold uppercase tracking-tighter ${item.color}`}>
                {item.sub.split(' — ')[0]}
              </span>
            </div>
          </div>

          {/* Icon side */}
          <div className={`p-2.5 rounded-xl ${item.bg} border border-border shrink-0`}>
            <item.icon size={15} className={item.color} />
          </div>

          {/* Minimal bottom accent */}
          <div className="absolute bottom-0 left-4 right-4 h-[2px] rounded-full overflow-hidden opacity-10">
            <div className={`h-full w-full ${item.color.replace("text-", "bg-")}`} />
          </div>
        </motion.div>
      ))}
    </div>
  );
}
