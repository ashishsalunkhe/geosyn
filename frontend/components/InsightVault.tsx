"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Database, Shield, TrendingUp, Map as MapIcon, Hash, BarChart3, Clock, ArrowRight } from "lucide-react";
import { fetchIntelligenceTrends } from "@/lib/api";
import GeopoliticalMap from "./GeopoliticalMap";
import ThematicRadar from "./ThematicRadar";

const InsightVault: React.FC = () => {
  const [trends, setTrends] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadTrends = async () => {
      try {
        const data = await fetchIntelligenceTrends();
        setTrends(data);
      } catch (err) {
        console.error("Trends Load Error:", err);
      } finally {
        setLoading(false);
      }
    };
    loadTrends();
  }, []);

  if (loading) {
    return (
      <div className="p-12 text-center">
        <div className="inline-block w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4" />
        <p className="text-[10px] font-black text-zinc-600 uppercase tracking-widest animate-pulse">Initializing Insight Vault...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 p-1 animate-in fade-in slide-in-from-bottom-4 duration-1000">
      {/* Header Stat row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="glass-panel p-4 bg-white/5 border-l-4 border-primary">
            <div className="flex items-center gap-2 mb-1">
                <Database size={12} className="text-primary" />
                <span className="text-[10px] font-black text-zinc-500 tracking-widest uppercase">ARCHIVED INSIGHTS</span>
            </div>
            <div className="text-xl font-black text-white italic">{trends?.archive_count || 0}</div>
          </div>
          
          <div className="glass-panel p-4 bg-white/5 border-l-4 border-emerald-500">
            <div className="flex items-center gap-2 mb-1">
                <Shield size={12} className="text-emerald-500" />
                <span className="text-[10px] font-black text-zinc-500 tracking-widest uppercase">AVG SYSTEM CONF</span>
            </div>
            <div className="text-xl font-black text-white italic">
               {trends?.confidence_trend?.length > 0 
                 ? (trends.confidence_trend.reduce((a:any, b:any) => a + b.v, 0) / trends.confidence_trend.length * 100).toFixed(0)
                 : 0}%
            </div>
          </div>

          <div className="glass-panel p-4 bg-white/5 border-l-4 border-rose-500 md:col-span-2">
            <div className="flex items-center gap-2 mb-1">
                <TrendingUp size={12} className="text-rose-500" />
                <span className="text-[10px] font-black text-zinc-500 tracking-widest uppercase">DOMINANT DIMENSION</span>
            </div>
            <div className="text-xl font-black text-white italic flex items-center gap-3">
               {Object.entries(trends?.thematic_dimensions || {}).sort((a:any, b:any) => b[1] - a[1])[0]?.[0].toUpperCase() || "NONE"}
               <span className="text-[10px] text-zinc-500 normal-case font-bold not-italic font-sans">(Tactical Majority)</span>
            </div>
          </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          {/* Main Heatmap */}
          <div className="xl:col-span-2 space-y-4">
             <GeopoliticalMap points={[]} /> {/* Map with overall focus later */}
             <div className="glass-panel p-6 bg-black/40 border-zinc-800">
                <h3 className="text-xs font-black uppercase tracking-[0.2em] text-white flex items-center gap-3 mb-6 border-b border-zinc-800 pb-4">
                    <Hash size={16} className="text-primary" />
                    Top Intelligence Topics
                </h3>
                <div className="space-y-3">
                   {trends?.top_topics?.map((t: any, idx: number) => (
                      <div key={idx} className="flex items-center justify-between p-3 bg-white/5 rounded-xl border border-white/5 hover:border-primary/40 transition-all cursor-default group">
                         <div className="flex items-center gap-4">
                            <span className="text-[10px] font-black text-zinc-700 w-4 tracking-tighter">0{idx+1}</span>
                            <span className="text-[12px] font-black text-white uppercase italic">{t.topic}</span>
                         </div>
                         <div className="flex items-center gap-4 text-zinc-500">
                            <span className="text-[9px] font-black tracking-widest">{t.count} SYNTHESES</span>
                            <ArrowRight size={12} className="group-hover:translate-x-1 transition-transform text-zinc-800" />
                         </div>
                      </div>
                   ))}
                </div>
             </div>
          </div>

          {/* Right Radar & Trends */}
          <div className="space-y-6">
              <div className="glass-panel p-6 bg-black/40 border-zinc-800">
                <h3 className="text-xs font-black uppercase tracking-[0.2em] text-white flex items-center gap-3 mb-6">
                    <BarChart3 size={16} className="text-primary" />
                    Global Threat Radius
                </h3>
                {trends?.thematic_dimensions && <ThematicRadar data={trends.thematic_dimensions} />}
                <p className="mt-4 text-[9px] font-bold text-zinc-500 italic leading-snug border-t border-zinc-900 pt-4">
                    Aggregated tactical dimensions across all archived intelligence briefs. Radar spike indicates sectoral vulnerability.
                </p>
              </div>

              <div className="glass-panel p-6 bg-black/40 border-zinc-800 h-[280px] flex flex-col items-center justify-center text-center opacity-40">
                  <Clock size={32} className="mb-4 text-zinc-700" />
                  <span className="text-[10px] font-black uppercase tracking-widest text-zinc-700">Chronological Narrative Drift</span>
                  <p className="text-[8px] font-bold text-zinc-800 mt-2 px-8">Coming Soon: Sequential sentiment tracking for high-velocity topics.</p>
              </div>
          </div>
      </div>
    </div>
  );
};

export default InsightVault;
