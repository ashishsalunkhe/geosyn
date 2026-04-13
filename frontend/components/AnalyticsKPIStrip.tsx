"use client";

import React from "react";
import { motion } from "framer-motion";
import { 
  Zap, 
  Activity, 
  ShieldAlert, 
  UserCheck, 
  TrendingUp,
  BarChart3
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

export default function AnalyticsKPIStrip({ data, loading }: AnalyticsKPIStripProps) {
  if (loading || !data) {
     return (
       <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-8">
         {[...Array(5)].map((_, i) => (
           <div key={i} className="h-24 glass-panel bg-white/5 animate-pulse rounded-2xl" />
         ))}
       </div>
     );
  }

  const items = [
    {
      label: "Portfolio Fragility",
      value: `${data.avg_fragility}%`,
      icon: Activity,
      color: "text-amber-500",
      bg: "bg-amber-500/10",
      sub: "Aggregated Risk Index"
    },
    {
      label: "Prospective Signals",
      value: data.total_signals.toLocaleString(),
      icon: Zap,
      color: "text-primary",
      bg: "bg-primary/10",
      sub: "Mesh Throughput (24H)"
    },
    {
      label: "Critical Nodes",
      value: data.critical_count,
      icon: ShieldAlert,
      color: "text-rose-500",
      bg: "bg-rose-500/10",
      sub: "Action Required"
    },
    {
      label: "Source Reliability",
      value: `${data.avg_confidence}%`,
      icon: UserCheck,
      color: "text-emerald-500",
      bg: "bg-emerald-500/10",
      sub: "Weighted Confidence"
    },
    {
      label: "Market Exposure",
      value: `$${data.market_exposure}T`,
      icon: TrendingUp,
      color: "text-blue-500",
      bg: "bg-blue-500/10",
      sub: "Asset Correlation Cap"
    }
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-10">
      {items.map((item, idx) => (
        <motion.div
          key={idx}
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: idx * 0.1 }}
          className="glass-panel p-5 bg-zinc-950/40 border-zinc-900 group hover:border-primary/20 transition-all flex flex-col justify-between overflow-hidden relative"
        >
          <div className="flex items-center justify-between relative z-10">
            <span className="text-[9px] font-black text-zinc-500 uppercase tracking-widest">{item.label}</span>
            <item.icon size={14} className={item.color} />
          </div>
          
          <div className="mt-2 relative z-10">
            <div className={`text-xl font-black italic tracking-tighter text-white group-hover:${item.color} transition-colors`}>
              {item.value}
            </div>
            <div className="text-[7px] font-bold text-zinc-700 uppercase tracking-tighter mt-1">{item.sub}</div>
          </div>

          {/* Micro Sparkline Decoration */}
          <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-zinc-900 overflow-hidden">
             <motion.div 
               initial={{ x: "-100%" }}
               animate={{ x: "0%" }}
               transition={{ duration: 1, delay: 0.5 + (idx * 0.1) }}
               className={`h-full ${item.color.replace('text-', 'bg-')}`} 
               style={{ opacity: 0.3 }}
             />
          </div>
          
          <div className={`absolute -right-2 -bottom-2 opacity-[0.02] group-hover:opacity-[0.05] transition-opacity ${item.color}`}>
             <BarChart3 size={60} />
          </div>
        </motion.div>
      ))}
    </div>
  );
}
