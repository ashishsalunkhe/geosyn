"use client";

import React from "react";
import { motion } from "framer-motion";
import { Zap, AlertTriangle, ShieldCheck, Activity, TrendingUp } from "lucide-react";
import { getStatusTone } from "@/lib/status-theme";

interface ScenarioHUDProps {
  scenarios: any[];
}

export default function ScenarioHUD({ scenarios }: ScenarioHUDProps) {
  const getCount = (status: string) => scenarios.filter(s => s.status === status).length;

  const TILES = [
    { label: "Total Tracked", val: scenarios.length, icon: Activity, color: "text-foreground", bg: "bg-foreground/5" },
    { label: "Emerging Risks", val: getCount("EMERGING"), icon: Zap, color: getStatusTone("EMERGING").text, soft: getStatusTone("EMERGING").soft, border: getStatusTone("EMERGING").border },
    { label: "Active Crises", val: getCount("ACTIVE"), icon: TrendingUp, color: getStatusTone("ACTIVE").text, soft: getStatusTone("ACTIVE").soft, border: getStatusTone("ACTIVE").border },
    { label: "Critical Alerts", val: getCount("CRITICAL"), icon: AlertTriangle, color: getStatusTone("CRITICAL").text, soft: getStatusTone("CRITICAL").soft, border: getStatusTone("CRITICAL").border },
    { label: "Stabilized", val: getCount("STABILIZED") + getCount("RESOLVING"), icon: ShieldCheck, color: getStatusTone("STABILIZED").text, soft: getStatusTone("STABILIZED").soft, border: getStatusTone("STABILIZED").border },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-10">
      {TILES.map((tile, idx) => (
        <motion.div
          key={tile.label}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: idx * 0.05 }}
          className="glass-panel p-4 flex items-center justify-between border border-border bg-panel-bg shadow-sm rounded-2xl"
        >
          <div className="flex flex-col">
            <span className="text-[10px] font-black text-text-muted uppercase tracking-widest mb-1">{tile.label}</span>
            <div className="text-xl font-black text-foreground italic tracking-tight">{tile.val}</div>
          </div>
          
          <div className={`p-2.5 rounded-xl ${"soft" in tile ? tile.soft : tile.bg} border ${"border" in tile ? tile.border : "border-border/40"}`}>
            <tile.icon size={16} className={tile.color} />
          </div>
        </motion.div>
      ))}
    </div>
  );
}
