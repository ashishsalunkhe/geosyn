"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Target, Zap, Clock, MapPin, Building2, ArrowRight, Info, ShieldCheck, Database, GitBranch, User } from "lucide-react";
import { fetchIntelligenceBrief } from "@/lib/api";
import IntelligenceLedger from "./IntelligenceLedger";
import ParticipantDirectory from "./ParticipantDirectory";
import FragilityGauge from "./FragilityGauge";

interface IntelligenceBriefProps {
  topic: string;
  ticker?: string;
}

export default function IntelligenceBrief({ topic, ticker }: IntelligenceBriefProps) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"narrative" | "mesh" | "nexus" | "exposure">("narrative");

  useEffect(() => {
    if (!topic) return;

    async function loadBrief() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetchIntelligenceBrief(topic, ticker);
        setData(res);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadBrief();
  }, [topic, ticker]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-12 glass-panel h-full min-h-[400px]">
        <motion.div 
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          className="p-4 rounded-full bg-primary/10 mb-6"
        >
          <Zap className="text-primary" size={40} />
        </motion.div>
        <h3 className="text-sm font-black tracking-[0.2em] text-zinc-500 uppercase italic animate-pulse">
          Synthesizing Intelligence Brief...
        </h3>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-8 glass-panel border-dashed border-rose-500/30 flex flex-col items-center">
        <Info className="text-rose-500 mb-4" size={32} />
        <p className="text-xs font-black text-rose-500 uppercase tracking-widest leading-loose text-center">
          {error || "Select a Tactical Topic to begin analysis"}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12">
      {/* Header Info */}
      <section>
        <div className="flex items-center justify-between mb-8">
          <div className="flex flex-col">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] font-black text-zinc-500 tracking-[0.2em] uppercase italic">Tactical Precision</span>
              {data.search_metadata?.type && (
                <span className={`text-[8px] font-black px-1.5 py-0.5 rounded tracking-widest uppercase ${
                  data.search_metadata.type === 'EXACT' ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20' :
                  data.search_metadata.type === 'RELAXED' ? 'bg-amber-500/10 text-amber-500 border border-amber-500/20' :
                  'bg-zinc-500/10 text-zinc-500 border border-zinc-500/20'
                }`}>
                  {data.search_metadata.type.replace('_', ' ')}
                </span>
              )}
            </div>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary rounded-lg shadow-lg shadow-primary/20">
                <Target size={20} className="text-black" />
              </div>
              <h2 className="text-2xl font-black tracking-tight text-white uppercase italic">
                {topic}
              </h2>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {data.llm_enhanced && (
              <div className="flex items-center gap-2 px-3 py-1 bg-primary/10 border border-primary/20 rounded-full">
                <div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                <span className="text-[10px] font-black text-primary tracking-widest uppercase italic">AI Augmented</span>
              </div>
            )}
          </div>
        </div>

        {/* GeoSyn Fragility Index (GFI) - Dual Weighted HUD */}
        <div className="mb-10 p-6 glass-panel bg-white/[0.02] border-zinc-900 flex flex-col md:flex-row gap-8 items-center border-t-2 border-t-primary/20 shadow-2xl shadow-primary/5">
            <div className="flex flex-col gap-1 items-center md:items-start min-w-[140px]">
               <div className="text-[10px] font-black text-primary tracking-[0.3em] uppercase mb-1">Fragility Index</div>
               <div className={`text-4xl font-black italic tracking-tighter ${
                 data.gfi_metrics?.status === 'CRITICAL' ? 'text-rose-500' : 
                 data.gfi_metrics?.status === 'VOLATILE' ? 'text-amber-500' : 'text-emerald-500'
               }`}>
                 {data.gfi_metrics?.aggregate_score}%
               </div>
               <div className="text-[8px] font-bold text-zinc-600 uppercase tracking-widest bg-zinc-900 px-2 py-0.5 rounded">
                  {data.gfi_metrics?.status || 'STABLE'} TACTICAL STATE
               </div>
            </div>

            <div className="flex-1 flex flex-col md:flex-row gap-10 w-full">
               <FragilityGauge 
                 label="Signal Volume Ratio" 
                 value={data.gfi_metrics?.volume_index || 0} 
                 color="text-amber-500" 
                 subtext="Mention prevalence across 5,000+ OSINT signals"
               />
               <FragilityGauge 
                 label="Tone Intensity Delta" 
                 value={data.gfi_metrics?.intensity_index || 0} 
                 color="text-rose-500" 
                 subtext="Weighted sentiment delta in critical narratives"
               />
            </div>
        </div>

        {/* Tactical Tabs Navigation */}
        <div className="flex items-center gap-1 p-1 bg-zinc-900/50 border border-zinc-800 rounded-2xl mb-12 w-fit">
           {[
             { id: "narrative", label: "Briefing", icon: Info },
             { id: "mesh", label: "Data Mesh", icon: Database },
             { id: "nexus", label: "Causal Nexus", icon: GitBranch },
             { id: "exposure", label: "Exposure List", icon: User },
           ].map((tab) => (
             <button
               key={tab.id}
               onClick={() => setActiveTab(tab.id as any)}
               className={`flex items-center gap-2 px-6 py-2.5 rounded-xl text-[9px] font-black uppercase tracking-widest transition-all ${
                 activeTab === tab.id ? "bg-white/10 text-white shadow-lg" : "text-zinc-500 hover:text-white"
               }`}
             >
               <tab.icon size={12} className={activeTab === tab.id ? 'text-primary' : 'text-zinc-700'} />
               {tab.label}
             </button>
           ))}
        </div>

        <AnimatePresence mode="wait">
          {activeTab === "narrative" && (
            <motion.div
              key="narrative"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 10 }}
              className="space-y-10"
            >
              <div className="p-6 glass-panel bg-primary/5 border-primary/20 border-l-8">
                <p className="text-sm font-bold text-zinc-200 leading-relaxed italic">
                  "{data.narrative_summary || "Strategic synthesis in progress..."}"
                </p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="glass-panel p-4 bg-white/5 border-l-4 border-primary">
                  <span className="text-[10px] font-black text-zinc-500 tracking-widest uppercase block mb-1">AGGREGATED SIGNAL</span>
                  <div className="text-lg font-black text-white italic">
                    {data.timeline.length > 0 ? (data.timeline[0].tone > 0 ? "BULLISH" : "BEARISH") : "NEUTRAL"}
                  </div>
                </div>
                <div className="glass-panel p-4 bg-white/5 border-l-4 border-emerald-500">
                  <span className="text-[10px] font-black text-zinc-500 tracking-widest uppercase block mb-1">EVIDENCE NODES</span>
                  <div className="text-lg font-black text-white italic">{data.timeline.length} VERIFIED</div>
                </div>
                <div className="glass-panel p-4 bg-white/5 border-l-4 border-zinc-500 relative group transition-all">
                  <span className="text-[10px] font-black text-zinc-500 tracking-widest uppercase block mb-1">SYSTEM CONFIDENCE</span>
                  <div className="text-lg font-black text-white italic">
                    {data.confidence_metadata?.total_score || 0}%
                  </div>
                </div>
              </div>

              {/* Asset Projections */}
              {data.possible_effects && data.possible_effects.length > 0 && (
                 <div className="space-y-6 pt-6 border-t border-zinc-900">
                    <h3 className="text-[10px] font-black text-zinc-500 tracking-[0.2em] uppercase mb-4 flex items-center gap-2">
                      <Zap size={12} className="text-primary" /> MARKET PROJECTED IMPACTS
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                       {data.possible_effects.map((effect: any, idx: number) => (
                          <AssetCard key={idx} effect={effect} idx={idx} />
                       ))}
                    </div>
                 </div>
              )}

              <div className="space-y-6">
                <h3 className="text-xs font-black tracking-[0.2em] text-zinc-500 uppercase flex items-center gap-2">
                   <Clock size={14} className="text-primary" /> CHRONOLOGICAL INTELLIGENCE PIVOTS
                </h3>
                <div className="grid grid-cols-1 gap-4">
                  {data.timeline.map((item: any, idx: number) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      className="glass-panel p-6 bg-white/[0.02] border-zinc-900 flex flex-col md:flex-row md:items-center justify-between gap-6 hover:bg-white/[0.04] transition-all group"
                    >
                      <div className="flex items-start gap-4 flex-1">
                        <div className="flex flex-col items-center gap-1 min-w-[60px] py-1 border-r border-zinc-800 mr-2">
                           <span className="text-[10px] font-black text-primary tracking-tighter italic">Signal</span>
                           <span className="text-[8px] font-black text-zinc-600 uppercase tracking-widest">{idx + 1}</span>
                        </div>
                        <div className="flex flex-col gap-1">
                          <div className="flex items-center gap-3">
                             <span className="text-[8px] font-black text-primary/60 uppercase tracking-widest">{item.source}</span>
                             <span className="text-[9px] font-mono text-zinc-700">{item.seendate ? new Date(item.seendate).toLocaleDateString() : 'N/A'}</span>
                          </div>
                          <h4 className="text-[13px] font-black text-white italic leading-snug group-hover:text-primary transition-colors cursor-pointer" onClick={() => window.open(item.url, '_blank')}>
                             {item.title}
                          </h4>
                        </div>
                      </div>
                      <div className="flex items-center gap-6 md:border-l border-zinc-800 md:pl-8">
                         <div className="flex flex-col gap-1 items-end min-w-[80px]">
                            <span className="text-[8px] font-black text-zinc-600 uppercase tracking-widest">TACTICAL TONE</span>
                            <span className={`text-xs font-black italic ${item.tone < 0 ? 'text-rose-500' : 'text-emerald-500'}`}>{item.tone}</span>
                         </div>
                         <div className="p-2 bg-zinc-900 rounded-lg text-zinc-700 group-hover:text-primary transition-all">
                            <ChevronRight size={16} />
                         </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === "mesh" && (
            <motion.div
              key="mesh"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
            >
              <IntelligenceLedger records={data.standardized_mesh || []} />
            </motion.div>
          )}

          {activeTab === "nexus" && (
             <motion.div
               key="nexus"
               initial={{ opacity: 0, scale: 0.98 }}
               animate={{ opacity: 1, scale: 1 }}
               exit={{ opacity: 0, scale: 0.98 }}
               className="space-y-6"
             >
                <div className="glass-panel bg-black/40 p-10 border-zinc-800 text-center">
                    <Database size={40} className="text-zinc-800 mx-auto mb-6" />
                    <h3 className="text-[10px] font-black text-white tracking-[0.2em] uppercase mb-4">Causal Chain Matrix</h3>
                    <div className="space-y-6 relative max-w-2xl mx-auto text-left">
                        {(data.causal_chain || []).map((step: any, idx: number) => (
                            <div key={idx} className="flex gap-6 items-start relative pb-10">
                                {idx < (data.causal_chain || []).length - 1 && <div className="absolute left-[13px] top-8 bottom-0 w-0.5 bg-zinc-900" />}
                                <div className="h-7 w-7 rounded-full bg-zinc-900 border border-zinc-800 flex items-center justify-center relative z-10">
                                   <span className="text-[9px] font-black text-primary italic">{idx + 1}</span>
                                </div>
                                <div className="flex-1 pt-1">
                                    <h4 className="text-[10px] font-black text-zinc-400 tracking-widest uppercase mb-1">{step.event || "Causal Pivot"}</h4>
                                    <p className="text-sm font-bold text-white italic leading-relaxed">{step.leads_to || step.effect}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
             </motion.div>
          )}

          {activeTab === "exposure" && (
            <motion.div
              key="exposure"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
            >
              <ParticipantDirectory records={data.standardized_mesh || []} />
            </motion.div>
          )}
        </AnimatePresence>
      </section>
    </div>
  );
}

const ChevronRight = ({ size, className }: { size: number, className?: string }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className={className}><polyline points="9 18 15 12 9 6"></polyline></svg>
);

const AssetCard = ({ effect, idx }: { effect: any, idx: number }) => {
  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: idx * 0.1 }}
      className="glass-panel p-4 bg-white/[0.02] border-zinc-900 group transition-all hover:border-primary/40"
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex flex-col">
          <span className="text-[7px] font-black text-primary tracking-widest uppercase">{effect.category}</span>
          <h4 className="text-[11px] font-black text-white italic uppercase truncate w-32">{effect.asset}</h4>
        </div>
        <div className={`text-lg font-black ${effect.direction === 'UP' ? 'text-emerald-500' : 'text-rose-500'}`}>
          {effect.direction === 'UP' ? '↑' : '↓'}
        </div>
      </div>
      <p className="text-[9px] font-bold text-zinc-500 italic leading-tight mb-3 h-8 overflow-hidden">
        {effect.basis}
      </p>
      <div className="flex justify-between items-center pt-2 border-t border-zinc-900">
         <span className="text-[7px] font-black text-zinc-600 uppercase">Confidence</span>
         <span className="text-[9px] font-mono text-zinc-400 font-bold">{Math.round(effect.confidence * 100)}%</span>
      </div>
    </motion.div>
  );
};
