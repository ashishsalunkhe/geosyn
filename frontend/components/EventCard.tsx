"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, ChevronUp, AlertCircle, Bookmark, Share2, Activity, Globe, Shield } from "lucide-react";

interface EventCardProps {
  event: any;
}

const EventCard: React.FC<EventCardProps> = ({ event }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="glass-panel group hover:border-primary/30 transition-all duration-300 overflow-hidden">
      {/* Tactical Status Ribbon */}
      <div className="h-1 w-full bg-gradient-to-r from-primary/50 via-primary to-primary/50 opacity-60" />
      
      <div className="p-5">
        <div className="flex justify-between items-start mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-lg">
              <Shield size={18} className="text-primary" />
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-[10px] font-black tracking-widest text-primary uppercase">INTEL CLUSTER</span>
                <span className="w-1 h-1 rounded-full bg-primary/40" />
                <span className="text-[10px] font-bold text-zinc-500 uppercase">
                  {new Date(event.created_at).toLocaleDateString()}
                </span>
              </div>
              <h3 className="text-lg font-bold tracking-tight text-white group-hover:text-primary transition-colors">
                {event.title}
              </h3>
            </div>
          </div>
          <div className="flex items-center gap-2">
             <div className="flex flex-col items-end">
                <span className="text-[9px] font-black text-zinc-500 uppercase leading-none mb-1">Intensity</span>
                <div className="flex gap-0.5">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <div 
                      key={i} 
                      className={`h-3 w-1.5 rounded-sm ${i <= 3 ? 'bg-primary' : 'bg-white/10'}`} 
                    />
                  ))}
                </div>
             </div>
          </div>
        </div>

        <p className="text-sm text-zinc-400 leading-relaxed mb-6 line-clamp-2">
          {event.summary}
        </p>

        {/* Tactical Badges */}
        <div className="flex flex-wrap gap-2 mb-6">
          {event.metadata?.themes?.slice(0, 3).map((theme: string) => (
            <span key={theme} className="px-2 py-0.5 rounded-md bg-zinc-800/50 border border-white/5 text-[10px] font-bold text-zinc-300 uppercase tracking-wider">
              {theme}
            </span>
          ))}
          {event.metadata?.actors?.slice(0, 2).map((actor: string) => (
            <span key={actor} className="px-2 py-0.5 rounded-md bg-primary/5 border border-primary/20 text-[10px] font-black text-primary uppercase tracking-wider">
              @{actor}
            </span>
          ))}
        </div>

        <button 
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full flex items-center justify-center gap-2 py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/5 transition-colors text-xs font-bold text-zinc-300 hover:text-white"
        >
          {isExpanded ? (
            <>COLLAPSE ANALYSIS <ChevronUp size={14} /></>
          ) : (
            <>EXPAND FULL INTELLIGENCE <ChevronDown size={14} /></>
          )}
        </button>

        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden"
            >
              <div className="pt-6 mt-6 border-t border-white/5 flex flex-col gap-6">
                <div>
                  <h4 className="text-[10px] font-black text-primary mb-3 uppercase tracking-[0.2em]">Causal Analysis</h4>
                  <p className="text-sm text-zinc-400 leading-relaxed">
                    This cluster demonstrates significant correlation with regional volatility. 
                    Sentiment weights suggest high-probability impact on safe-haven assets.
                  </p>
                </div>
                
                <div>
                  <h4 className="text-[10px] font-black text-primary mb-3 uppercase tracking-[0.2em]">Source Intelligence</h4>
                  <div className="space-y-2">
                    {event.documents?.map((doc: any) => (
                      <a 
                        key={doc.id} 
                        href={doc.url} 
                        target="_blank" 
                        rel="noreferrer"
                        className="flex items-center justify-between p-3 rounded-xl bg-black/20 border border-white/5 hover:border-primary/30 transition-all group/link"
                      >
                        <span className="max-w-[80%] wrap-anywhere text-xs font-semibold text-zinc-300 group-hover/link:text-white">
                          {doc.title}
                        </span>
                        <Activity size={12} className="text-zinc-500 group-hover/link:text-primary" />
                      </a>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default EventCard;
