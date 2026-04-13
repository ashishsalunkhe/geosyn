"use client";

import React from "react";
import { motion } from "framer-motion";
import { User, Shield, AlertCircle, TrendingDown, TrendingUp } from "lucide-react";

interface Participant {
  name: string;
  type: string;
  exposure_score: number; // 0-100
  sentiment: "Bullish" | "Bearish" | "Neutral";
}

interface ParticipantDirectoryProps {
  records: any[];
}

export default function ParticipantDirectory({ records }: ParticipantDirectoryProps) {
  // Simple extraction of unique 'Sources' as participants for now
  const sources = Array.from(new Set(records.map(r => r.source)));
  
  const participants: Participant[] = sources.map(name => {
      const related = records.filter(r => r.source === name);
      const avgTone = related.reduce((acc, curr) => acc + curr.tone, 0) / related.length;
      return {
          name,
          type: "Organization",
          exposure_score: Math.min(100, related.length * 10),
          sentiment: avgTone < -2 ? "Bearish" : avgTone > 2 ? "Bullish" : "Neutral"
      };
  }).sort((a, b) => b.exposure_score - a.exposure_score);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-in fade-in duration-700">
      {participants.map((p, idx) => (
        <motion.div
          key={idx}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: idx * 0.05 }}
          className="glass-panel p-6 bg-white/[0.02] border-zinc-900 group hover:border-primary/30 transition-all overflow-hidden relative"
        >
          <div className="flex items-start justify-between mb-6">
            <div className="p-3 bg-zinc-900 rounded-2xl text-zinc-600 group-hover:text-primary transition-colors">
              <User size={24} />
            </div>
            <div className={`px-2 py-1 rounded text-[8px] font-black uppercase tracking-tighter flex items-center gap-1.5 ${
                p.sentiment === "Bearish" ? "bg-rose-500/10 text-rose-500" :
                p.sentiment === "Bullish" ? "bg-emerald-500/10 text-emerald-500" :
                "bg-zinc-500/10 text-zinc-500"
            }`}>
                {p.sentiment === "Bearish" ? <TrendingDown size={10}/> : p.sentiment === "Bullish" ? <TrendingUp size={10}/> : <Shield size={10}/>}
                {p.sentiment}
            </div>
          </div>

          <div className="mb-6">
            <h4 className="text-sm font-black text-white italic truncate">{p.name}</h4>
            <span className="text-[9px] font-bold text-zinc-600 uppercase tracking-widest">{p.type}</span>
          </div>

          <div className="space-y-2 pt-4 border-t border-zinc-900">
            <div className="flex justify-between text-[8px] font-black text-zinc-500 uppercase tracking-widest">
                <span>Exposure Intensity</span>
                <span>{p.exposure_score.toFixed(0)}%</span>
            </div>
            <div className="h-1 bg-zinc-900 rounded-full overflow-hidden">
                <div 
                  className={`h-full transition-all duration-1000 ${p.exposure_score > 70 ? 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.4)]' : 'bg-primary shadow-[0_0_8px_rgba(99,102,241,0.4)]'}`} 
                  style={{ width: `${p.exposure_score}%` }} 
                />
            </div>
          </div>

          <div className="absolute -bottom-2 -right-2 opacity-[0.03] group-hover:opacity-[0.08] transition-opacity">
             <AlertCircle size={80} />
          </div>
        </motion.div>
      ))}
    </div>
  );
}
