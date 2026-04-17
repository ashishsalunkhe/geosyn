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
      <div className="flex flex-col items-center justify-center p-12 glass-panel bg-panel-bg h-full min-h-[400px] rounded-2xl border border-border">
        <motion.div 
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          className="p-4 rounded-full bg-primary/10 mb-6"
        >
          <Zap className="text-primary" size={40} />
        </motion.div>
        <h3 className="text-[11px] font-black tracking-[0.2em] text-text-muted uppercase italic animate-pulse">
          Analyzing tactical topic...
        </h3>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-8 glass-panel bg-panel-bg border-dashed border-error/30 flex flex-col items-center rounded-2xl">
        <Info className="text-error mb-4" size={32} />
        <p className="text-xs font-black text-error uppercase tracking-widest leading-loose text-center italic">
          {error || "Select an active topic group to begin analysis"}
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
              <span className="text-[10px] font-black text-text-muted tracking-[0.2em] uppercase italic">Strategic Analysis</span>
              {data.search_metadata?.type && (
                <span className={`text-[8px] font-black px-1.5 py-0.5 rounded-lg tracking-widest uppercase border ${
                  data.search_metadata.type === 'EXACT' ? 'bg-success/10 text-success border-success/20' :
                  data.search_metadata.type === 'RELAXED' ? 'bg-secondary text-foreground border-border' :
                  'bg-panel-bg text-text-muted border-border'
                }`}>
                  {data.search_metadata.type.replace('_', ' ')}
                </span>
              )}
            </div>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary rounded-xl text-white shadow-sm">
                <Target size={18} />
              </div>
              <h2 className="text-2xl font-black tracking-tight text-foreground uppercase italic leading-tight">
                {topic}
              </h2>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {data.llm_enhanced && (
              <div className="flex items-center gap-2 px-4 py-1.5 bg-secondary border border-border rounded-2xl">
                <div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                <span className="text-[10px] font-black text-foreground tracking-widest uppercase italic">AI Augmented</span>
              </div>
            )}
          </div>
        </div>

        {/* GeoSyn Fragility Index (GFI) - Dual Weighted HUD */}
        <div className="mb-10 p-6 glass-panel bg-panel-bg border border-border flex flex-col md:flex-row gap-8 items-center rounded-2xl shadow-sm">
            <div className="flex flex-col gap-1 items-center md:items-start min-w-[140px]">
               <div className="text-[10px] font-black text-text-muted tracking-[0.3em] uppercase mb-1">Risk Level</div>
               <div className={`text-4xl font-black italic tracking-tighter leading-none ${
                 data.gfi_metrics?.status === 'CRITICAL' ? 'text-error' : 
                 data.gfi_metrics?.status === 'VOLATILE' ? 'text-hazard' : 'text-success'
               }`}>
                 {data.gfi_metrics?.aggregate_score}%
               </div>
               <div className="text-[8px] font-black text-text-muted uppercase tracking-widest bg-secondary px-2 py-0.5 rounded-lg mt-2">
                  {data.gfi_metrics?.status || 'STABLE'} STATUS
               </div>
            </div>

            <div className="flex-1 flex flex-col md:flex-row gap-10 w-full">
               <FragilityGauge 
                 label="News Coverage Level" 
                 value={data.gfi_metrics?.volume_index || 0} 
                 color="text-secondary" 
                 subtext="Topic frequency across global news streams"
               />
               <FragilityGauge 
                 label="News Alarm Level" 
                 value={data.gfi_metrics?.intensity_index || 0} 
                 color="text-error" 
                 subtext="Intensity of language in recent reports"
               />
            </div>
        </div>

        {/* Tactical Tabs Navigation */}
        <div className="flex items-center gap-1 p-1 bg-secondary/30 border border-border rounded-2xl mb-12 w-fit">
           {[
             { id: "narrative", label: "Summary", icon: Info },
             { id: "mesh", label: "Sources", icon: Database },
             { id: "nexus", label: "Event Chain", icon: GitBranch },
             { id: "exposure", label: "Parties", icon: User },
           ].map((tab) => (
             <button
               key={tab.id}
               onClick={() => setActiveTab(tab.id as any)}
               className={`flex items-center gap-2 px-6 py-2.5 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all ${
                 activeTab === tab.id ? "bg-panel-bg text-foreground shadow-sm border border-primary/20" : "text-text-muted hover:text-foreground hover:bg-foreground/5"
               }`}
             >
               <tab.icon size={12} className={activeTab === tab.id ? 'text-primary' : 'text-text-muted'} />
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
              <div className="p-6 glass-panel bg-panel-bg border border-border border-l-4 border-l-primary rounded-2xl shadow-sm">
                <p className="text-sm font-bold text-foreground leading-relaxed italic">
                  "{data.narrative_summary || "Strategic synthesis in progress..."}"
                </p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="glass-panel p-5 bg-panel-bg border border-border border-l-4 border-l-primary rounded-2xl shadow-sm">
                  <span className="text-[10px] font-black text-text-muted tracking-widest uppercase block mb-1">AGGREGATED SIGNAL</span>
                  <div className="text-lg font-black text-foreground italic">
                    {data.timeline.length > 0 ? (data.timeline[0].tone > 0 ? "BULLISH" : "BEARISH") : "NEUTRAL"}
                  </div>
                </div>
                <div className="glass-panel p-5 bg-panel-bg border border-border border-l-4 border-l-success rounded-2xl shadow-sm">
                  <span className="text-[10px] font-black text-text-muted tracking-widest uppercase block mb-1">EVIDENCE NODES</span>
                  <div className="text-lg font-black text-foreground italic">{data.timeline.length} VERIFIED</div>
                </div>
                <div className="glass-panel p-5 bg-panel-bg border border-border border-l-4 border-l-text-muted/20 rounded-2xl shadow-sm">
                  <span className="text-[10px] font-black text-text-muted tracking-widest uppercase block mb-1">SYSTEM CONFIDENCE</span>
                  <div className="text-lg font-black text-foreground italic">
                    {data.confidence_metadata?.total_score || 0}%
                  </div>
                </div>
              </div>

              {/* Asset Projections */}
              {data.possible_effects && data.possible_effects.length > 0 && (
                 <div className="space-y-8 pt-6 border-t border-border">
                    <h3 className="text-[10px] font-black text-text-muted tracking-[0.2em] uppercase mb-4 flex items-center gap-2 italic">
                       <Zap size={12} className="text-primary" /> POTENTIAL MARKET EFFECTS
                     </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                       {data.possible_effects.map((effect: any, idx: number) => (
                          <AssetCard key={idx} effect={effect} idx={idx} />
                       ))}
                    </div>
                 </div>
              )}

              <div className="space-y-6">
                <h3 className="text-[10px] font-black tracking-[0.2em] text-text-muted uppercase flex items-center gap-2 italic">
                   <Clock size={14} className="text-primary" /> NEWS TIMELINE
                </h3>
                <div className="grid grid-cols-1 gap-4">
                  {data.timeline.map((item: any, idx: number) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      className="glass-panel p-4 bg-panel-bg border border-border flex flex-col md:flex-row md:items-center justify-between gap-6 hover:border-primary transition-all group rounded-2xl shadow-sm"
                    >
                      <div className="flex items-start gap-4 flex-1">
                        <div className="flex flex-col items-center gap-1 min-w-[60px] py-1 border-r border-border mr-2">
                           <span className="text-[10px] font-black text-primary tracking-tighter italic leading-none">Signal</span>
                           <span className="text-[8px] font-black text-text-muted uppercase tracking-widest leading-none mt-1">{idx + 1}</span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-3 mb-1">
                             <span className="text-[8px] font-black text-primary/60 uppercase tracking-widest">{item.source}</span>
                             <span className="text-[9px] font-bold text-text-muted italic">{item.seendate ? new Date(item.seendate).toLocaleDateString() : 'N/A'}</span>
                          </div>
                          <h4 className="text-[13px] font-black text-foreground italic leading-tight group-hover:text-primary transition-colors cursor-pointer truncate uppercase" onClick={() => window.open(item.url, '_blank')}>
                             {item.title}
                          </h4>
                        </div>
                      </div>
                      <div className="flex items-center gap-6 md:border-l border-border md:pl-8">
                         <div className="flex flex-col gap-1 items-end min-w-[80px]">
                            <span className="text-[8px] font-black text-text-muted uppercase tracking-widest leading-none">SENTIMENT</span>
                            <span className={`text-[13px] font-black italic leading-none mt-1 ${item.tone < 0 ? 'text-error' : 'text-success'}`}>{item.tone}</span>
                         </div>
                         <div className="p-2 border border-border rounded-xl text-text-muted group-hover:text-primary group-hover:border-primary transition-all bg-secondary/30">
                            <ChevronRight size={14} />
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
              <IntelligenceLedger records={data.timeline || []} />
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
                <div className="glass-panel bg-panel-bg p-10 border border-border text-center rounded-2xl shadow-sm">
                    <Database size={40} className="text-text-muted/10 mx-auto mb-6" />
                    <h3 className="text-[10px] font-black text-foreground tracking-[0.2em] uppercase mb-10 italic">Causal Transition Mapping</h3>
                    <div className="space-y-6 relative max-w-2xl mx-auto text-left">
                        {(Array.isArray(data.causal_chain) ? data.causal_chain : Object.values(data.causal_chain || {})).map((step: any, idx: number) => (
                            <div key={idx} className="flex gap-6 items-start relative pb-10">
                                {idx < (Array.isArray(data.causal_chain) ? data.causal_chain : Object.values(data.causal_chain || {})).length - 1 && <div className="absolute left-[13px] top-8 bottom-0 w-0.5 bg-border" />}
                                <div className="h-7 w-7 rounded-full bg-secondary border border-border flex items-center justify-center relative z-10 shadow-sm">
                                   <span className="text-[9px] font-black text-primary italic">{idx + 1}</span>
                                </div>
                                <div className="flex-1 pt-1">
                                    <h4 className="text-[10px] font-black text-text-muted tracking-widest uppercase mb-1 italic leading-none">{step.event || "Tactical Pivot"}</h4>
                                    <p className="text-sm font-bold text-foreground italic leading-relaxed uppercase">{step.leads_to || step.effect}</p>
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
              <ParticipantDirectory records={data.timeline || []} />
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
      className="glass-panel p-5 bg-panel-bg border border-border group transition-all hover:border-primary rounded-2xl shadow-sm"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex flex-col">
          <span className="text-[8px] font-black text-primary tracking-widest uppercase mb-1">{effect.category}</span>
          <h4 className="text-[13px] font-black text-foreground italic uppercase truncate w-32 leading-none">{effect.asset}</h4>
        </div>
        <div className={`text-xl font-black leading-none ${effect.direction === 'UP' ? 'text-success' : 'text-error'}`}>
          {effect.direction === 'UP' ? '↑' : '↓'}
        </div>
      </div>
      <p className="text-[10px] font-bold text-text-muted italic leading-tight mb-4 h-8 overflow-hidden uppercase">
        {typeof effect.basis === 'object' ? JSON.stringify(effect.basis) : effect.basis}
      </p>
      <div className="flex justify-between items-center pt-3 border-t border-border/60">
         <span className="text-[8px] font-black text-text-muted uppercase tracking-widest leading-none">Confidence</span>
         <span className="text-[10px] font-black text-foreground leading-none">{Math.round(effect.confidence * 100)}%</span>
      </div>
    </motion.div>
  );
};
