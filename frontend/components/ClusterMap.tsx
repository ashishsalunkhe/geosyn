"use client";

import React from "react";
import { motion } from "framer-motion";
import { Shield, Target, Clock, MessageSquare, ChevronRight, Share2, BarChart3 } from "lucide-react";

interface EventClusterProps {
  clusters: any[];
  onAnalyze: (topic: string) => void;
}

export default function ClusterMap({ clusters, onAnalyze }: EventClusterProps) {
  if (!clusters || clusters.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-20 glass-panel border-dashed border-border">
        <Target className="text-text-muted/40 mb-4 animate-pulse" size={48} />
        <h3 className="text-sm font-black text-text-muted uppercase tracking-widest italic">
          No News Groups Found Yet
        </h3>
        <p className="text-[10px] text-text-muted/60 mt-2 text-center max-w-xs uppercase leading-loose">
          The system is reading global news articles. Topics will be grouped automatically every 5 minutes.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-xl font-black tracking-tight text-foreground uppercase italic">Active Topic Groups</h2>
          <p className="text-[10px] font-bold text-primary tracking-widest uppercase italic mt-1">AI-Grouped by Topic · Updated Every 5 Minutes</p>
        </div>
        <div className="px-4 py-2 bg-panel-bg border border-border rounded-xl flex items-center gap-3 shadow-sm">
          <div className="flex flex-col">
            <span className="text-[7px] font-black text-foreground uppercase">Update Rate</span>
            <span className="text-[10px] font-black text-success italic uppercase tracking-widest">Optimal</span>
          </div>
          <div className="h-8 w-[1px] bg-border" />
          <div className="flex flex-col">
             <span className="text-[7px] font-black text-text-muted uppercase">Groups Found</span>
             <span className="text-[10px] font-black text-foreground italic">{clusters.length}</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {clusters.map((cluster, idx) => (
          <motion.div
            key={cluster.id || idx}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="glass-panel p-4 bg-panel-bg shadow-sm rounded-2xl border border-border group hover:border-primary transition-all relative overflow-hidden"
          >
            <div className="flex items-center justify-between mb-3 relative z-10">
              <div className="flex items-center gap-2">
                <div className="p-1.5 bg-primary/20 rounded-lg">
                  <Shield size={12} className="text-primary" />
                </div>
                <span className="text-[9px] font-black text-foreground uppercase tracking-widest">
                  {new Date(cluster.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                </span>
              </div>
              <div className="flex -space-x-1.5">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="w-4 h-4 rounded-full border border-background bg-secondary" />
                ))}
              </div>
            </div>

            <h3 className="text-sm font-black text-foreground uppercase leading-tight tracking-tight mb-2 group-hover:text-primary transition-colors italic">
              {cluster.title || cluster.name}
            </h3>
            
            <p className="text-[10px] font-bold text-text-muted leading-relaxed line-clamp-2 mb-4">
              {cluster.summary || "Strategically significant cluster of geopolitical events requiring immediate tactical evaluation."}
            </p>

            <div className="flex items-center gap-4 pt-4 border-t border-border relative z-10">
              <div className="flex items-center gap-1.5">
                <BarChart3 size={11} className="text-success" />
                <span className="text-[9px] font-black text-success uppercase tracking-tighter italic">Match Control</span>
              </div>
              <div className="flex items-center gap-1.5">
                <MessageSquare size={11} className="text-text-muted" />
                <span className="text-[9px] font-black text-text-muted uppercase tracking-tighter">Insights</span>
              </div>
              <div className="ml-auto flex items-center gap-1 group/btn" onClick={() => onAnalyze(cluster.title)}>
                <span className="text-[8px] font-black uppercase tracking-widest text-primary opacity-0 group-hover:opacity-100 transition-opacity">Analyze</span>
                <ChevronRight size={14} className="text-primary group-hover:translate-x-0.5 transition-transform" />
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
