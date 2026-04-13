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
  onSelect: (topic: string) => void;
}

export default function MarketLandscape({ scenarios, trending, onSelect }: MarketLandscapeProps) {
  return (
    <div className="space-y-16 animate-in fade-in duration-1000">
      
      {/* Tracked Scenarios Grid */}
      <section>
        <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary rounded-xl text-black">
                <Target size={18} />
              </div>
              <div>
                <h3 className="text-sm font-black tracking-widest text-white uppercase italic">Active Portfolio Landscape</h3>
                <p className="text-[10px] font-bold text-zinc-600 uppercase tracking-tighter">Your Persistent Tactical Vault</p>
              </div>
            </div>
            <div className="text-[10px] font-black text-zinc-500 uppercase tracking-widest border border-zinc-900 px-3 py-1 rounded-lg">
                {scenarios.length} Tracked Records
            </div>
        </div>

        {scenarios.length === 0 ? (
          <div className="py-20 text-center glass-panel border-dashed border-zinc-800">
             <Target size={40} className="text-zinc-900 mx-auto mb-4" />
             <p className="text-[10px] font-black text-zinc-600 uppercase tracking-widest italic">No tracked scenarios in current filter orbit.</p>
             <p className="text-[8px] font-bold text-zinc-700 uppercase mt-2">Discover and follow topics from the global mesh.</p>
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
        <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-zinc-900 rounded-xl text-primary">
                <Globe size={18} />
              </div>
              <div>
                <h3 className="text-sm font-black tracking-widest text-white uppercase italic">Community Discovery Feed</h3>
                <p className="text-[10px] font-bold text-zinc-600 uppercase tracking-tighter">Global Strategic Priorities (Simulated Community)</p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-[9px] font-black text-zinc-500 uppercase tracking-widest">
                <Users size={12} className="text-primary/60" /> Live Orbit Analysis
            </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {trending.map((s, idx) => (
            <motion.div 
              key={s.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 + (idx * 0.1) }}
              onClick={() => onSelect(s.topic)}
              className="glass-panel p-5 bg-zinc-950/40 border-zinc-900 group hover:border-primary/40 hover:bg-zinc-900/40 transition-all cursor-pointer relative overflow-hidden"
            >
              <div className="flex items-center justify-between mb-4">
                 <span className="text-[7px] font-black text-primary tracking-[0.3em] uppercase">{s.region} / {s.sector}</span>
                 <div className="px-1.5 py-0.5 bg-black/40 border border-zinc-800 rounded text-[7px] font-black text-zinc-500 flex items-center gap-1 group-hover:text-primary transition-colors">
                    <TrendingUp size={8} /> {s.community_interest || "HIGH"} INTEREST
                 </div>
              </div>
              <h4 className="text-[11px] font-black text-white italic uppercase tracking-tight leading-snug group-hover:text-primary transition-colors mb-2">
                {s.topic}
              </h4>
              <div className="absolute -bottom-2 -right-2 opacity-[0.02] group-hover:opacity-[0.05] transition-opacity">
                 <Globe size={80} />
              </div>
            </motion.div>
          ))}
        </div>
      </section>

    </div>
  );
}

function ScenarioCard({ scenario, idx, onClick }: { scenario: Scenario, idx: number, onClick: () => void }) {
  const statusColors = {
      CRITICAL: "text-rose-500 bg-rose-500/10 border-rose-500/20 shadow-[0_0_15px_rgba(244,63,94,0.3)]",
      ACTIVE: "text-amber-500 bg-amber-500/10 border-amber-500/20 shadow-[0_0_15px_rgba(245,158,11,0.2)]",
      EMERGING: "text-primary bg-primary/10 border-primary/20",
      STABILIZED: "text-emerald-500 bg-emerald-500/10 border-emerald-500/20",
      RESOLVING: "text-zinc-500 bg-zinc-500/10 border-zinc-500/20"
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: idx * 0.1 }}
      onClick={onClick}
      className="glass-panel p-6 bg-white/[0.02] border-zinc-900 group hover:border-primary/40 hover:bg-white/[0.04] transition-all cursor-pointer relative overflow-hidden min-h-[180px] flex flex-col"
    >
      <div className="flex items-start justify-between mb-6">
        <div className="flex flex-col">
            <span className="text-[8px] font-black text-zinc-600 tracking-widest uppercase mb-1">{scenario.region} // {scenario.sector}</span>
            <h4 className="text-[15px] font-black text-white italic group-hover:text-primary transition-colors leading-tight uppercase tracking-tight">
                {scenario.topic}
            </h4>
        </div>
        <div className={`px-2 py-1 rounded text-[8px] font-black tracking-widest transition-all ${statusColors[scenario.status]}`}>
            {scenario.status}
        </div>
      </div>

      <div className="mt-auto space-y-4 pt-4 border-t border-zinc-900/50">
        <div className="flex justify-between items-end">
            <div className="flex flex-col gap-1">
               <span className="text-[7px] font-black text-zinc-600 uppercase tracking-widest">TACTICAL RISK SCORE</span>
               <div className="flex items-center gap-2">
                  <div className={`text-xl font-black italic ${scenario.risk_score > 0.7 ? 'text-rose-500' : 'text-primary'}`}>
                    {(scenario.risk_score * 100).toFixed(0)}%
                  </div>
                  <div className="h-1 w-16 bg-zinc-900 rounded-full overflow-hidden">
                     <div className={`h-full ${scenario.risk_score > 0.7 ? 'bg-rose-500' : 'bg-primary'}`} style={{ width: `${scenario.risk_score * 100}%` }} />
                  </div>
               </div>
            </div>
            <div className="p-2 border border-zinc-900 rounded-lg text-zinc-700 group-hover:text-primary group-hover:border-primary/20 transition-all">
               <ChevronRight size={16} />
            </div>
        </div>
      </div>

      {/* Aesthetic Background Pattern */}
      <div className="absolute -bottom-4 -right-4 opacity-[0.03] group-hover:opacity-[0.08] transition-opacity">
         {scenario.status === 'CRITICAL' ? <AlertCircle size={100} /> : <ShieldCheck size={100} />}
      </div>
    </motion.div>
  );
}
