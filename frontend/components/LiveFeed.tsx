"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Radio, Globe, TrendingUp, TrendingDown, Minus, ExternalLink, Target } from "lucide-react";
import { fetchLiveIntelligence } from "@/lib/api";

interface LiveFeedProps {
  onAnalyze?: (topic: string) => void;
}

export default function LiveFeed({ onAnalyze }: LiveFeedProps) {
  const [articles, setArticles] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isMounted, setIsMounted] = useState(false);

  const loadFeed = async () => {
    try {
      const data = await fetchLiveIntelligence("geopolitics OR markets OR conflict");
      setArticles(data);
    } catch (err) {
      console.error("Feed error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setIsMounted(true);
    loadFeed();
    const interval = setInterval(loadFeed, 60000); // Poll every minute
    return () => clearInterval(interval);
  }, []);

  if (!isMounted) return <div className="h-full bg-black/40 animate-pulse border-r border-zinc-800" />;

  return (
    <div className="flex flex-col h-full bg-black/40 glass-panel border-zinc-800 border-r-0 rounded-r-none">
      <div className="p-4 border-b border-zinc-800 flex items-center justify-between bg-black/20">
        <div className="flex items-center gap-2">
          <Radio size={14} className="text-rose-500 animate-pulse" />
          <h2 className="text-[10px] font-black tracking-[0.2em] text-zinc-400 uppercase">Live Intelligence Stream</h2>
        </div>
        <div className="flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-[9px] font-black text-emerald-500 uppercase tracking-widest">Connected</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar">
        <AnimatePresence mode="popLayout">
          {loading && articles.length === 0 ? (
            <div className="p-8 text-center space-y-4">
              <div className="inline-block w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
              <p className="text-[9px] font-black text-zinc-600 uppercase tracking-widest italic">Tuning Signal...</p>
            </div>
          ) : (
            articles.map((art, idx) => {
              const tone = float(art.tone || 0);
              return (
                <motion.div
                  key={art.url + idx}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="p-4 border-b border-zinc-800/50 hover:bg-white/[0.03] transition-colors group cursor-default"
                >
                  <div className="flex items-start gap-3 mb-2">
                    <div className={`mt-1 w-1 h-8 rounded-full ${
                      tone < -10 ? 'bg-rose-500' : tone > 10 ? 'bg-emerald-500' : 'bg-primary'
                    }`} />
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[10px] font-black uppercase tracking-widest truncate">
                          {art.source || "GLOBAL MONITOR"}
                        </span>
                        <div className="flex items-center gap-1">
                           {tone > 0 ? <TrendingUp size={10} className="text-emerald-500" /> : <TrendingDown size={10} className="text-rose-500" />}
                           <span className={`text-[9px] font-bold ${tone < 0 ? 'text-rose-500' : 'text-emerald-500'}`}>
                              {tone > 0 ? '+' : ''}{tone.toFixed(1)}
                           </span>
                        </div>
                      </div>
                      <div className="flex items-start justify-between gap-2">
                        <a 
                          href={art.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-xs font-bold text-zinc-200 leading-snug group-hover:text-white transition-colors block decoration-primary/20 hover:underline underline-offset-4 break-words flex-1"
                        >
                          {art.title}
                        </a>
                        {onAnalyze && (
                          <button 
                            onClick={(e) => { e.preventDefault(); onAnalyze(art.title); }}
                            className="mt-1 p-1.5 rounded-lg bg-primary/10 border border-primary/20 text-primary opacity-0 group-hover:opacity-100 transition-all hover:bg-primary hover:text-black shadow-lg shadow-primary/20"
                            title="Focus Tactical Analysis"
                          >
                            <Target size={12} />
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center justify-between pl-4">
                    <span className="text-[8px] font-black text-zinc-600 uppercase tracking-widest">
                      {new Date(art.seendate || Date.now()).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', timeZoneName: 'short' })}
                    </span>
                    <ExternalLink size={10} className="text-zinc-700 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                </motion.div>
              );
            })
          )}
        </AnimatePresence>
      </div>

      <div className="p-3 bg-black/60 border-t border-zinc-800">
         <button 
           onClick={() => loadFeed()}
           className="w-full py-2 bg-zinc-900 hover:bg-zinc-800 text-[9px] font-black text-zinc-400 uppercase tracking-[0.2em] transition-colors rounded border border-zinc-800 flex items-center justify-center gap-2"
         >
           <Globe size={10} /> FORCE RE-SYNC
         </button>
      </div>
    </div>
  );
}

const float = (v: any) => typeof v === 'number' ? v : parseFloat(v) || 0;
