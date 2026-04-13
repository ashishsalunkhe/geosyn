"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Rss, Video, Activity, Zap } from "lucide-react";

interface IntelligenceFeedProps {
  documents: any[];
}

const IntelligenceFeed: React.FC<IntelligenceFeedProps> = ({ documents }) => {
  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Activity size={18} className="text-primary animate-pulse" />
          <h3 className="text-xs font-black tracking-[0.2em] text-zinc-500 uppercase">Live Intelligence Wire</h3>
        </div>
        <div className="flex items-center gap-1.5 px-2 py-1 rounded-md bg-primary/10 border border-primary/20">
          <div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
          <span className="text-[9px] font-bold text-primary uppercase">Active Sync</span>
        </div>
      </div>

      <div className="space-y-4 overflow-y-auto pr-2 custom-scrollbar">
        <AnimatePresence mode="popLayout">
          {documents.length === 0 ? (
            <motion.div 
              initial={{ opacity: 0 }} 
              animate={{ opacity: 1 }}
              className="py-12 text-center"
            >
              <Zap size={24} className="mx-auto mb-3 text-zinc-700 opacity-20" />
              <p className="text-xs font-bold text-zinc-600 uppercase tracking-wider italic">Awaiting Ground Intel...</p>
            </motion.div>
          ) : (
            documents.slice(0, 15).map((doc, i) => (
              <motion.div
                key={doc.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                className="relative p-4 rounded-xl glass-panel group hover:bg-white/[0.07] transition-all cursor-pointer"
              >
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-6 bg-primary opacity-0 group-hover:opacity-100 transition-opacity" />
                
                <div className="flex justify-between items-center mb-2">
                  <div className="flex items-center gap-2">
                    {doc.source_type === "youtube" ? (
                      <Video size={12} className="text-red-500" />
                    ) : (
                      <Rss size={12} className="text-primary" />
                    )}
                    <span className="text-[10px] font-black text-zinc-500 uppercase tracking-tighter">
                      {doc.source_name || (doc.source_type === "rss" ? "Global Wire" : "Intelligence")}
                    </span>
                  </div>
                  <span className="text-[10px] font-mono font-bold text-zinc-600">
                    {new Date(doc.published_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                
                <p className="text-[13px] font-bold leading-snug text-zinc-200 group-hover:text-white transition-colors line-clamp-2">
                  {doc.title}
                </p>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>

      <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.05); border-radius: 10px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(99,102,241,0.2); }
      `}</style>
    </div>
  );
};

export default IntelligenceFeed;
