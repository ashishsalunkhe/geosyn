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
        <p className="text-[10px] font-black text-text-muted uppercase tracking-widest animate-pulse">Loading saved reports...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 p-1 animate-in fade-in slide-in-from-bottom-4 duration-1000">
      {/* Header Stat row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="glass-panel p-4 bg-panel-bg border-l-4 border-primary">
            <div className="flex items-center gap-2 mb-1">
                <Database size={12} className="text-primary" />
                <span className="text-[10px] font-black text-text-muted tracking-widest uppercase">ARCHIVED INSIGHTS</span>
            </div>
            <div className="text-xl font-black text-foreground italic">{trends?.archive_count || 0}</div>
          </div>
          
          <div className="glass-panel p-4 bg-panel-bg border-l-4 border-success">
            <div className="flex items-center gap-2 mb-1">
                <Shield size={12} className="text-success" />
                <span className="text-[10px] font-black text-text-muted tracking-widest uppercase">AVG DATA QUALITY</span>
            </div>
            <div className="text-xl font-black text-foreground italic">
               {trends?.confidence_trend?.length > 0 
                 ? (trends.confidence_trend.reduce((a:any, b:any) => a + b.v, 0) / trends.confidence_trend.length * 100).toFixed(0)
                 : 0}%
            </div>
          </div>

          <div className="glass-panel p-4 bg-panel-bg border-l-4 border-error md:col-span-2">
            <div className="flex items-center gap-2 mb-1">
                <TrendingUp size={12} className="text-error" />
                <span className="text-[10px] font-black text-text-muted tracking-widest uppercase">TOP RISK THEME</span>
            </div>
            <div className="text-xl font-black text-foreground italic flex items-center gap-3">
               {Object.entries(trends?.thematic_dimensions || {}).sort((a:any, b:any) => b[1] - a[1])[0]?.[0].toUpperCase() || "NONE"}
               <span className="text-[10px] text-text-muted normal-case font-bold not-italic font-sans">(Most active this week)</span>
            </div>
          </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          {/* Main Heatmap */}
          <div className="xl:col-span-2 space-y-4">
             <GeopoliticalMap points={trends?.geo_points || []} />
             <div className="glass-panel p-6 bg-panel-bg border-border border-l-4 border-l-primary/40">
                <h3 className="text-xs font-black uppercase tracking-[0.2em] text-foreground flex items-center gap-3 mb-6 border-b border-border pb-4">
                    <Hash size={16} className="text-primary" />
                     Most Tracked Topics
                </h3>
                <div className="space-y-3">
                   {trends?.top_topics?.map((t: any, idx: number) => (
                      <div key={idx} className="flex items-center justify-between p-3 bg-foreground/5 rounded-xl border border-transparent hover:border-primary/40 transition-all cursor-default group">
                         <div className="flex items-center gap-4">
                            <span className="text-[10px] font-black text-text-muted/40 w-4 tracking-tighter">0{idx+1}</span>
                            <span className="text-[12px] font-black text-foreground uppercase italic">{t.topic}</span>
                         </div>
                         <div className="flex items-center gap-4 text-text-muted">
                             <span className="text-[9px] font-black tracking-widest">{t.count} ANALYSES</span>
                            <ArrowRight size={12} className="group-hover:translate-x-1 transition-transform text-text-muted/60" />
                         </div>
                      </div>
                   ))}
                </div>
             </div>
          </div>

          {/* Right Radar & Trends */}
          <div className="space-y-6">
              <div className="glass-panel p-6 bg-panel-bg border-border">
                <h3 className="text-xs font-black uppercase tracking-[0.2em] text-foreground flex items-center gap-3 mb-6">
                    <BarChart3 size={16} className="text-primary" />
                     Risk Theme Breakdown
                </h3>
                {trends?.thematic_dimensions && <ThematicRadar data={trends.thematic_dimensions} />}
                 <p className="mt-4 text-[9px] font-bold text-text-muted italic leading-snug border-t border-border pt-4">
                     Shows which risk themes (e.g., conflict, economic, energy) are most active across all your tracked topics. A larger spike = more coverage in that area.
                 </p>
              </div>

              <div className="glass-panel p-6 bg-panel-bg border-border h-[280px] flex flex-col items-center justify-center text-center opacity-40">
                  <Clock size={32} className="mb-4 text-text-muted/60" />
                  <span className="text-[10px] font-black uppercase tracking-widest text-text-muted/80">Sentiment Over Time</span>
                  <p className="text-[8px] font-bold text-text-muted mt-2 px-8">Coming Soon: Track how news tone shifts on your most-followed topics.</p>
              </div>
          </div>
      </div>
    </div>
  );
};

export default InsightVault;
