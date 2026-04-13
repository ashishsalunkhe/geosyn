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
      <div className="flex flex-col items-center justify-center p-20 glass-panel border-dashed border-zinc-800">
        <Target className="text-zinc-700 mb-4 animate-pulse" size={48} />
        <h3 className="text-sm font-black text-zinc-500 uppercase tracking-widest italic">
          No Intelligence Clusters Formed
        </h3>
        <p className="text-[10px] text-zinc-600 mt-2 text-center max-w-xs uppercase leading-loose">
          System is currently ingesting OSINT signals. Mathematical grouping occurs every 5-minute cycle.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-xl font-black tracking-tight text-white uppercase italic">Active Intelligence Clusters</h2>
          <p className="text-[10px] font-bold text-primary tracking-widest uppercase italic mt-1">TF-IDF Vectorized Mathematical Grouping</p>
        </div>
        <div className="px-4 py-2 bg-zinc-900 border border-zinc-800 rounded-xl flex items-center gap-3">
          <div className="flex flex-col">
            <span className="text-[7px] font-black text-zinc-600 uppercase">Formation Rate</span>
            <span className="text-[10px] font-black text-emerald-500 italic">OPTIMAL</span>
          </div>
          <div className="h-8 w-[1px] bg-zinc-800" />
          <div className="flex flex-col">
             <span className="text-[7px] font-black text-zinc-600 uppercase">Cluster Density</span>
             <span className="text-[10px] font-black text-white italic">{clusters.length} NODES</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {clusters.map((cluster, idx) => (
          <motion.div
            key={cluster.id || idx}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.05 }}
            onClick={() => onAnalyze(cluster.title)}
            className="glass-panel p-6 bg-white/[0.02] hover:bg-white/[0.05] border-zinc-800 transition-all group overflow-hidden relative cursor-pointer"
          >
            {/* Background Glow */}
            <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 blur-3xl rounded-full -mr-16 -mt-16 group-hover:bg-primary/10 transition-colors" />
            
            <div className="flex items-start justify-between mb-4 relative z-10">
              <div className="flex items-center gap-2">
                <div className="p-1.5 bg-primary/20 rounded-lg">
                  <Shield size={14} className="text-primary" />
                </div>
                <span className="text-[9px] font-black text-zinc-500 uppercase tracking-widest">
                  {new Date(cluster.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                </span>
              </div>
              <div className="flex items-center gap-1 group/share cursor-pointer" onClick={(e) => e.stopPropagation()}>
                 <Share2 size={12} className="text-zinc-700 group-hover/share:text-primary transition-colors" />
              </div>
            </div>

            <h3 className="text-sm font-black text-white uppercase tracking-tight mb-2 leading-tight italic group-hover:text-primary transition-colors">
              {cluster.title}
            </h3>
            
            <p className="text-[11px] font-bold text-zinc-400 mb-6 line-clamp-2 italic leading-relaxed">
              {cluster.summary || cluster.description}
            </p>

            <div className="flex items-center gap-4 pt-4 border-t border-zinc-900 relative z-10">
              <div className="flex items-center gap-1.5">
                <BarChart3 size={12} className="text-emerald-500" />
                <span className="text-[9px] font-black text-emerald-500 uppercase tracking-tighter italic">High Affinity</span>
              </div>
              <div className="flex items-center gap-1.5">
                <MessageSquare size={12} className="text-zinc-600" />
                <span className="text-[9px] font-black text-zinc-600 uppercase tracking-tighter">Verified OSINT</span>
              </div>
              
              <div className="ml-auto w-8 h-8 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center group-hover:bg-primary group-hover:border-primary group-hover:text-black transition-all group/btn">
                <ChevronRight size={16} className="group-hover/btn:translate-x-0.5 transition-transform" />
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
