"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Globe,
  Inbox,
  Filter,
  ChevronRight,
  ChevronDown,
  Star,
  Briefcase,
  Layers,
  BookMarked,
  ShieldAlert,
  TrendingUp,
  Zap,
} from "lucide-react";
import { getStatusTone } from "@/lib/status-theme";

interface TacticalSidebarProps {
  onFilterChange: (region: string, sector: string) => void;
  activeRegion: string;
  activeSector: string;
  scenarios: any[];
  onSelectScenario: (topic: string) => void;
}

const TAXONOMY = [
  {
    id: "industries",
    label: "Advanced Industries",
    icon: Briefcase,
    children: [
      { id: "AERO", label: "Aerospace & Defense" },
      { id: "AUTO", label: "Automotive & Logistics" },
      { id: "ELECT", label: "Advanced Electronics" },
    ],
  },
  {
    id: "energy",
    label: "Energy & Materials",
    icon: Layers,
    children: [
      { id: "POWER", label: "Power & Utilities" },
      { id: "MINING", label: "Rare Earth & Critical" },
      { id: "RENEW", label: "Renewable Systems" },
    ],
  },
  {
    id: "digital",
    label: "Digital Infrastructure",
    icon: Globe,
    children: [
      { id: "TELCO", label: "Telecommunications" },
      { id: "DATA", label: "Data Centers" },
      { id: "CYBER", label: "Cyber Sovereignty" },
    ],
  },
];

const REGIONS = [
  { id: "GLOBAL", label: "Global Presence" },
  { id: "APAC", label: "East Asia & Pacific" },
  { id: "EMEA", label: "Europe & Central Asia" },
  { id: "MENA", label: "Middle East & North Africa" },
  { id: "AMER", label: "Americas" },
];

const STATUS_ICONS: Record<string, any> = {
  CRITICAL: ShieldAlert,
  ACTIVE: TrendingUp,
  EMERGING: Zap,
  STABILIZED: Star,
  RESOLVING: Star,
};

export default function TacticalSidebar({
  onFilterChange,
  activeRegion,
  activeSector,
  scenarios,
  onSelectScenario,
}: TacticalSidebarProps) {
  const [expanded, setExpanded] = useState<string[]>(["industries"]);

  const toggleExpand = (id: string) => {
    setExpanded((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  // Count scenarios per sector for display
  const sectorCounts: Record<string, number> = {};
  scenarios.forEach((s) => {
    if (s.sector) {
      sectorCounts[s.sector] = (sectorCounts[s.sector] || 0) + 1;
    }
  });

  // Count scenarios per region
  const regionCounts: Record<string, number> = {};
  scenarios.forEach((s) => {
    if (s.region) {
      regionCounts[s.region] = (regionCounts[s.region] || 0) + 1;
    }
    regionCounts["GLOBAL"] = (regionCounts["GLOBAL"] || 0);
  });

  return (
    <div className="flex h-full flex-col gap-6 overflow-y-auto border-r border-border bg-panel-bg p-4 select-none transition-colors custom-scrollbar">

      {/* My Watchlist — quick-glance of tracked scenarios */}
      <section className="space-y-1">
        <div className="flex items-center justify-between mb-3 px-1">
          <h3 className="text-[10px] font-black text-foreground tracking-[0.2em] uppercase flex items-center gap-2">
            <BookMarked size={12} className="text-primary" /> My Watchlist
          </h3>
          <span className="text-[9px] font-black text-text-muted bg-panel-bg px-2 py-0.5 rounded-full border border-border">
            {scenarios.length}
          </span>
        </div>

        {scenarios.length === 0 ? (
          <div className="mx-1 p-4 border border-dashed border-border rounded-xl text-center opacity-50">
            <Inbox size={18} className="text-text-muted mx-auto mb-2" />
            <p className="text-[8px] font-bold text-text-muted uppercase tracking-widest leading-relaxed">
              Search a topic and click "Follow Scenario" to track it here.
            </p>
          </div>
        ) : (
          <div className="space-y-1.5 max-h-[220px] overflow-y-auto custom-scrollbar pr-1">
            {scenarios.slice(0, 6).map((s, idx) => {
              const tone = getStatusTone(s.status);
              const Icon = STATUS_ICONS[s.status] || STATUS_ICONS["RESOLVING"];
              return (
                <motion.button
                  key={s.id}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.04 }}
                  onClick={() => onSelectScenario(s.topic)}
                  className="group flex w-full items-center gap-2.5 rounded-2xl border border-transparent px-3 py-2.5 text-left transition-all hover:border-border hover:bg-secondary"
                >
                  <div className={`p-1.5 rounded-xl border ${tone.soft} ${tone.border} shrink-0`}>
                    <Icon size={10} className={tone.text} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="wrap-pretty line-clamp-2 text-[10px] font-black uppercase italic leading-tight text-foreground transition-colors group-hover:text-primary">
                      {s.topic}
                    </p>
                    <p className={`text-[7px] font-black uppercase tracking-widest ${tone.text} mt-0.5`}>
                      {s.status}
                    </p>
                  </div>
                </motion.button>
              );
            })}
            {scenarios.length > 6 && (
              <p className="text-center text-[8px] font-bold text-text-muted uppercase tracking-widest py-1">
                +{scenarios.length - 6} more
              </p>
            )}
          </div>
        )}
      </section>

      <div className="h-px bg-border" />

      {/* Hierarchical Filter Taxonomy */}
      <section>
        <div className="flex items-center justify-between mb-3 px-1">
          <h3 className="text-[10px] font-black text-foreground tracking-[0.2em] uppercase flex items-center gap-2">
            <Filter size={12} className="text-primary" /> Filter by Sector
          </h3>
          <button
            onClick={() => onFilterChange(activeRegion, "GENERAL")}
            className="text-[8px] font-bold text-primary hover:underline uppercase tracking-tighter"
          >
            Reset
          </button>
        </div>

        <div className="space-y-0.5">
          {TAXONOMY.map((category) => (
            <div key={category.id} className="mb-1">
              <button
                onClick={() => toggleExpand(category.id)}
                className="flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-left text-[10px] font-black text-foreground transition-colors hover:bg-secondary hover:text-primary"
              >
                <div className="flex min-w-0 items-center gap-2 uppercase tracking-widest">
                  <category.icon
                    size={12}
                    className={
                      expanded.includes(category.id)
                        ? "text-primary"
                        : "text-text-muted/40"
                    }
                  />
                  <span className="wrap-anywhere leading-tight">{category.label}</span>
                </div>
                {expanded.includes(category.id) ? (
                  <ChevronDown size={11} />
                ) : (
                  <ChevronRight size={11} />
                )}
              </button>

              <AnimatePresence>
                {expanded.includes(category.id) && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="overflow-hidden ml-4 mt-0.5 border-l border-border"
                  >
                    {category.children.map((child) => {
                      const count = sectorCounts[child.id] || 0;
                      const isActive = activeSector === child.id;
                      return (
                        <button
                          key={child.id}
                          onClick={() =>
                            onFilterChange(activeRegion, child.id)
                          }
                          className={`group flex w-full items-center justify-between gap-2 px-4 py-1.5 text-left text-[8px] font-bold uppercase tracking-widest transition-all ${
                            isActive
                              ? "text-primary"
                              : "text-text-muted/60 hover:text-foreground"
                          }`}
                        >
                          <div className="flex min-w-0 items-center gap-2">
                            <div
                              className={`w-1 h-1 rounded-full shrink-0 ${
                                isActive
                                  ? "bg-primary shadow-[0_0_6px_var(--primary)]"
                                  : "bg-border group-hover:bg-text-muted"
                              }`}
                            />
                            <span className="wrap-anywhere leading-tight">{child.label}</span>
                          </div>
                          {count > 0 && (
                            <span
                              className={`text-[7px] font-black px-1.5 py-0.5 rounded-full ${
                                isActive
                                  ? "bg-primary/20 text-primary"
                                  : "bg-border text-text-muted"
                              }`}
                            >
                              {count}
                            </span>
                          )}
                        </button>
                      );
                    })}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ))}
        </div>
      </section>

      {/* Geography Filters */}
      <section>
        <h3 className="text-[10px] font-black text-foreground tracking-[0.2em] uppercase mb-3 px-1 flex items-center gap-2">
          <Globe size={11} className="text-primary/60" /> Filter by Region
        </h3>
        <div className="space-y-0.5">
          {REGIONS.map((reg) => {
            const count =
              reg.id === "GLOBAL"
                ? scenarios.length
                : regionCounts[reg.id] || 0;
            const isActive = activeRegion === reg.id;
            return (
              <button
                key={reg.id}
                onClick={() => onFilterChange(reg.id, activeSector)}
                className={`group flex w-full items-center justify-between gap-2 rounded-2xl px-3 py-2.5 text-left text-[9px] font-black tracking-widest transition-all ${
                  isActive
                    ? "bg-secondary text-primary border border-border shadow-sm"
                    : "text-text-muted hover:bg-secondary hover:text-foreground border border-transparent"
                }`}
              >
                <div className="flex min-w-0 items-center gap-2.5">
                  <Globe
                    size={12}
                    className={
                      isActive
                        ? "text-primary"
                        : "text-text-muted/40 group-hover:text-primary"
                    }
                  />
                  <span className="wrap-anywhere uppercase leading-tight">{reg.label}</span>
                </div>
                <div className="flex items-center gap-1.5 shrink-0">
                  {count > 0 && (
                    <span
                      className={`text-[7px] font-black px-1.5 py-0.5 rounded-full ${
                        isActive
                          ? "bg-primary/20 text-primary"
                          : "bg-border text-text-muted"
                      }`}
                    >
                      {count}
                    </span>
                  )}
                  {isActive && (
                    <div className="w-1 h-1 rounded-full bg-primary" />
                  )}
                </div>
              </button>
            );
          })}
        </div>
      </section>
    </div>
  );
}
