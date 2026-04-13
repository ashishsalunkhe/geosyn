"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MessageSquare, Users, Share2, TrendingUp, AlertTriangle } from "lucide-react";

interface OSINTChatterProps {
  documents: any[];
}

const OSINTChatter: React.FC<OSINTChatterProps> = ({ documents }) => {
  const osintDocs = documents.filter(d => d.raw_data?.source_type === "osint");

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <MessageSquare size={18} className="text-orange-500 animate-pulse" />
          <h3 className="text-xs font-black tracking-[0.2em] text-zinc-500 uppercase">OSINT Social Chatter</h3>
        </div>
        <div className="flex items-center gap-1.5 px-2 py-1 rounded-md bg-orange-500/10 border border-orange-500/20">
          <TrendingUp size={10} className="text-orange-500" />
          <span className="text-[9px] font-bold text-orange-500 uppercase italic">Volatility High</span>
        </div>
      </div>

      <div className="space-y-4 overflow-y-auto pr-2 custom-scrollbar">
        <AnimatePresence mode="popLayout">
          {osintDocs.length === 0 ? (
            <div className="py-20 text-center flex flex-col items-center opacity-30">
               <Users size={32} className="text-zinc-700 mb-4" />
               <p className="text-[10px] font-black text-zinc-600 uppercase tracking-widest leading-relaxed px-8">
                 No social intelligence intercepted. <br/>Initiate Sync to monitor OSINT wires.
               </p>
            </div>
          ) : (
            osintDocs.map((doc, i) => (
              <motion.div
                key={doc.id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.05 }}
                className="relative p-5 rounded-2xl glass-panel group hover:bg-orange-500/5 transition-all cursor-pointer border-l-2 border-l-orange-500/30 hover:border-l-orange-500"
              >
                <div className="flex items-start justify-between mb-3">
                   <div className="flex flex-col">
                      <span className="text-[10px] font-black text-orange-500 uppercase tracking-tighter">@ENTITY_ALERT</span>
                      <span className="text-[9px] font-bold text-zinc-600">GDELT OSINT Uplink</span>
                   </div>
                   <div className="px-2 py-0.5 rounded bg-zinc-800 text-[10px] font-black text-zinc-400">
                     {new Date(doc.published_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                   </div>
                </div>
                
                <p className="text-[13px] font-bold leading-relaxed text-zinc-200 group-hover:text-white transition-colors mb-4">
                  {doc.title}
                </p>

                <div className="flex items-center justify-between pt-4 border-t border-white/5">
                   <div className="flex items-center gap-4">
                      <div className="flex items-center gap-1 text-zinc-600">
                         <Share2 size={12} />
                         <span className="text-[10px] font-bold">VIRAL</span>
                      </div>
                      <div className="flex items-center gap-1 text-orange-500/60">
                         <AlertTriangle size={12} />
                         <span className="text-[10px] font-bold italic">CRISIS INTEL</span>
                      </div>
                   </div>
                   <div className="h-4 w-px bg-white/5" />
                   <div className="text-[10px] font-black text-zinc-500 uppercase">Impact: High</div>
                </div>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>

      <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.05); border-radius: 10px; }
      `}</style>
    </div>
  );
};

export default OSINTChatter;
