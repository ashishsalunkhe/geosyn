"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AlertCircle, TrendingUp, Activity, MessageSquare, ArrowUpRight, ArrowDownRight, Clock, Info, Loader2 } from "lucide-react";
import { fetchAlertExplanation } from "@/lib/api";

interface Alert {
  id: number;
  type: string;
  severity: string;
  ticker: string;
  title: string;
  content: string;
  context_snippet: string;
  created_at: string;
  alert_payload?: any;
}

interface AlertPulseProps {
  alerts: Alert[];
  onClear?: () => void;
}

const AlertPulse: React.FC<AlertPulseProps> = ({ alerts, onClear }) => {
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [fetchedExplanations, setFetchedExplanations] = useState<Record<number, any>>({});
  const [loadingIds, setLoadingIds] = useState<Set<number>>(new Set());
  const [isMounted, setIsMounted] = useState(false);

  React.useEffect(() => {
    setIsMounted(true);
  }, []);

  const handleToggleExpand = async (alertId: number, hasExplanation: boolean) => {
    if (expandedId === alertId) {
      setExpandedId(null);
      return;
    }

    setExpandedId(alertId);

    // If no explanation exists in the payload AND not already fetched, fetch it
    if (!hasExplanation && !fetchedExplanations[alertId] && !loadingIds.has(alertId)) {
      setLoadingIds(prev => new Set(prev).add(alertId));
      try {
        const explanation = await fetchAlertExplanation(alertId);
        setFetchedExplanations(prev => ({ ...prev, [alertId]: explanation }));
      } catch (err) {
        console.error("Failed to fetch explanation:", err);
      } finally {
        setLoadingIds(prev => {
          const next = new Set(prev);
          next.delete(alertId);
          return next;
        });
      }
    }
  };

  if (!isMounted) return <div className="h-64 animate-pulse bg-panel-bg rounded-2xl" />;

  if (alerts.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full opacity-20 grayscale py-12">
        <Activity size={32} className="mb-4 text-text-muted opacity-40" />
        <p className="text-[10px] font-black uppercase tracking-widest text-center text-text-muted opacity-60">Monitoring Tactical Pulse...</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full max-h-[800px]">
      <div className="flex items-center justify-between mb-10 px-2">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-lg bg-hazard/10 border border-hazard/20 flex items-center justify-center text-hazard">
            <AlertCircle size={18} />
          </div>
          <h3 className="text-sm font-black uppercase tracking-[0.2em] text-foreground">Proactive Alerts</h3>
        </div>
        {onClear && (
          <button 
            onClick={onClear}
            className="text-[9px] font-black text-text-muted hover:text-foreground uppercase tracking-widest transition-all"
          >
            Clear All
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto pr-2 space-y-4 custom-scrollbar px-2 pb-12">
        {alerts.map((alert, i) => {
          const explanation = alert.alert_payload?.explanation || fetchedExplanations[alert.id];
          const isExpanded = expandedId === alert.id;
          const isLoading = loadingIds.has(alert.id);

          return (
            <motion.div
              key={alert.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
              className={`p-5 rounded-2xl border transition-all group relative overflow-hidden cursor-pointer ${
                alert.severity === 'high' ? 'bg-error/5 border-error/30 shadow-[0_4px_20px_rgba(229,62,62,0.05)]' : 
                alert.severity === 'medium' ? 'bg-hazard/5 border-hazard/30 shadow-sm' : 'bg-panel-bg border-border'
              }`}
              onClick={() => handleToggleExpand(alert.id, !!alert.alert_payload?.explanation)}
            >
              {/* Background Glow */}
              <div className={`absolute top-0 right-0 w-32 h-32 blur-[60px] opacity-10 pointer-events-none ${
                alert.severity === 'high' ? 'bg-error' : 
                alert.severity === 'medium' ? 'bg-hazard' : 'bg-primary'
              }`} />

              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <span className={`px-2 py-0.5 rounded text-[8px] font-black uppercase tracking-widest ${
                    alert.type === 'volatility' ? 'bg-error/20 text-error' : 'bg-hazard/20 text-hazard'
                  }`}>
                    {alert.type}
                  </span>
                  <span className="text-[10px] font-black text-foreground italic tracking-wider">${alert.ticker}</span>
                </div>
                <div className="flex items-center gap-1.5 text-text-muted opacity-60">
                  <Clock size={10} />
                  <span className="text-[9px] font-bold">
                    {new Date(alert.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </div>

              <h4 className="text-xs font-black text-foreground mb-2 leading-tight uppercase tracking-tight group-hover:text-primary transition-colors">
                {alert.title}
              </h4>

              <p className="text-[10px] text-text-muted font-bold leading-relaxed mb-4">
                {alert.content}
              </p>

              <AnimatePresence>
                {isExpanded && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="overflow-hidden"
                  >
                    {isLoading ? (
                      <div className="mb-4 p-4 rounded-xl bg-primary/5 border border-primary/20 flex flex-col items-center gap-2">
                        <Loader2 size={16} className="text-primary animate-spin" />
                        <span className="text-[8px] font-black text-primary uppercase tracking-[0.2em] animate-pulse">Synthesizing Evidence...</span>
                      </div>
                    ) : explanation ? (
                      <div className="space-y-4 mb-4">
                         {explanation.strategic_narrative && (
                           <div className="p-3 rounded-xl bg-hazard/10 border border-hazard/20">
                             <span className="text-[8px] font-black text-hazard uppercase tracking-widest block mb-1">Strategic Narrative</span>
                             <p className="text-[9px] font-bold text-foreground italic leading-snug">
                               {explanation.strategic_narrative}
                             </p>
                           </div>
                         )}

                         <div className="space-y-2">
                           <div className="flex items-center gap-2">
                             <div className="h-[1px] flex-1 bg-border" />
                             <span className="text-[8px] font-black text-primary uppercase tracking-widest italic">Evidence Chain</span>
                             <div className="h-[1px] flex-1 bg-border" />
                           </div>
                           <p className="text-[9px] font-black italic text-foreground leading-tight">
                             "{explanation.historical_pattern || "No direct causal pattern matched in historical data."}"
                           </p>
                           {explanation.evidence?.length > 0 && (
                             <ul className="space-y-1 pt-2 border-l border-primary/20 ml-1">
                               {explanation.evidence.map((ev: string, idx: number) => (
                                 <li key={idx} className="text-[9px] text-text-muted font-bold pl-3 leading-tight">
                                   {ev}
                                 </li>
                               ))}
                             </ul>
                           )}
                         </div>
                      </div>
                    ) : (
                      <div className="mb-4 p-4 rounded-xl bg-panel-bg border border-border text-center">
                        <p className="text-[9px] font-black text-text-muted uppercase tracking-widest italic opacity-40">No matching narrative found.</p>
                      </div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>

              <div className="p-3 rounded-xl bg-foreground/5 border border-border flex items-center justify-between gap-2">
                <div className="flex items-center gap-3 min-w-0 flex-1">
                  <div className={`h-6 w-6 rounded-lg bg-panel-bg flex-shrink-0 flex items-center justify-center border border-border ${explanation ? 'text-primary' : 'text-text-muted/40'}`}>
                    <MessageSquare size={12} />
                  </div>
                  <p className="text-[9px] font-black text-text-muted uppercase tracking-tighter leading-snug italic truncate">
                    {explanation ? 'AI REASONING ACTIVE' : alert.context_snippet}
                  </p>
                </div>
                <div className={`text-[8px] font-black uppercase tracking-widest px-2 py-1 rounded transition-colors ${
                  isExpanded ? 'text-foreground' : 'text-text-muted hover:text-primary'
                }`}>
                  {isLoading ? 'Wait...' : isExpanded ? 'Collapse' : 'Explain'}
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

export default AlertPulse;
