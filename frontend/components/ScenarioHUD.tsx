"use client";

import React from "react";
import { motion } from "framer-motion";
import { Zap, AlertTriangle, ShieldCheck, Activity, TrendingUp } from "lucide-react";

interface ScenarioHUDProps {
  scenarios: any[];
}

export default function ScenarioHUD({ scenarios }: ScenarioHUDProps) {
  const getCount = (status: string) => scenarios.filter(s => s.status === status).length;

  const TILES = [
    { label: "Total Tracked", val: scenarios.length, icon: Activity, color: "text-zinc-100", bg: "bg-zinc-500/10" },
    { label: "Emerging Risks", val: getCount("EMERGING"), icon: Zap, color: "text-amber-500", bg: "bg-amber-500/10" },
    { label: "Active Crises", val: getCount("ACTIVE"), icon: TrendingUp, color: "text-primary", bg: "bg-primary/10" },
    { label: "Critical Alerts", val: getCount("CRITICAL"), icon: AlertTriangle, color: "text-rose-500", bg: "bg-rose-500/10" },
    { label: "Stabilized", val: getCount("STABILIZED") + getCount("RESOLVING"), icon: ShieldCheck, color: "text-emerald-500", bg: "bg-emerald-500/10" },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-10">
      {TILES.map((tile, idx) => (
        <motion.div
          key={tile.label}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: idx * 0.05 }}
          className="glass-panel p-5 bg-white/[0.03] border-zinc-800 hover:bg-white/[0.06] transition-all group relative overflow-hidden"
        >
          <div className="flex items-start justify-between mb-4">
            <div className={`p-2 rounded-lg ${tile.bg} ${tile.color}`}>
              <tile.icon size={18} />
            </div>
            {/* Minimal Sparkline Placeholder */}
            <div className="flex gap-0.5 items-end h-6 pt-2">
                {[0.4, 0.7, 0.5, 0.9, 0.6, 1.0].map((h, i) => (
                    <div key={i} className={`w-1 rounded-full ${tile.color} opacity-20`} style={{ height: `${h * 100}%` }} />
                ))}
            </div>
          </div>
          
          <div className="flex flex-col">
            <span className="text-[10px] font-black text-zinc-500 uppercase tracking-widest mb-1">{tile.label}</span>
            <div className="text-2xl font-black text-white italic">{tile.val}</div>
          </div>

          <div className={`absolute bottom-0 left-0 h-1 ${tile.bg.replace('/10', '/30')} group-hover:w-full transition-all w-0`} />
        </motion.div>
      ))}
    </div>
  );
}
