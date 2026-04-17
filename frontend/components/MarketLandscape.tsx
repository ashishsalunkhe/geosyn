"use client";

import React from "react";
import { motion } from "framer-motion";
import { 
  Globe, 
  TrendingUp, 
  AlertCircle, 
  ShieldCheck, 
  ExternalLink,
  ChevronRight,
  Target,
  Users
} from "lucide-react";

interface Scenario {
  id: string;
  topic: string;
  status: "EMERGING" | "ACTIVE" | "CRITICAL" | "STABILIZED" | "RESOLVING";
  region: string;
  sector: string;
  risk_score: number;
  community_interest?: string;
}

interface MarketLandscapeProps {
  scenarios: Scenario[];
  trending: Scenario[];
  alerts?: any[];
  onSelect: (topic: string) => void;
}

export default function MarketLandscape({ scenarios, trending, alerts = [], onSelect }: MarketLandscapeProps) {
  return (
    <div className="space-y-16 animate-in fade-in duration-1000">
      
      {/* Tracked Scenarios Grid */}
      <section>
        <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary rounded-xl text-white shadow-sm">
                <Target size={18} />
              </div>
              <div>
                <h3 className="text-sm font-black tracking-widest text-foreground uppercase italic">Active Portfolio Landscape</h3>
                <p className="text-[10px] font-bold text-text-muted uppercase tracking-tighter">Your Persistent Tactical Vault</p>
              </div>
            </div>
            <div className="text-[10px] font-black text-text-muted uppercase tracking-widest border border-border px-4 py-1.5 rounded-2xl bg-panel-bg shadow-sm">
                {scenarios.length} Tracked Records
            </div>
        </div>

        {scenarios.length === 0 ? (
          <div className="py-20 text-center glass-panel border-dashed border-border bg-panel-bg/40">
             <Target size={40} className="text-text-muted/20 mx-auto mb-4" />
             <p className="text-[10px] font-black text-text-muted uppercase tracking-widest italic">No tracked scenarios in current filter orbit.</p>
             <p className="text-[8px] font-bold text-text-muted/60 uppercase mt-2">Discover and follow topics from the global mesh.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {scenarios.map((s, idx) => (
              <ScenarioCard key={s.id} scenario={s} idx={idx} onClick={() => onSelect(s.topic)} />
            ))}
          </div>
        )}
      </section>

      {/* Global Community Discovery */}
      <section>
        <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-secondary rounded-xl text-primary border border-border">
                <Globe size={18} />
              </div>
              <div>
                <h3 className="text-sm font-black tracking-widest text-foreground uppercase italic">Community Discovery Feed</h3>
                <p className="text-[10px] font-bold text-text-muted uppercase tracking-tighter">Global Strategic Priorities (Simulated Community)</p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-[9px] font-black text-text-muted uppercase tracking-widest">
                <Users size={12} className="text-primary" /> Live Orbit Analysis
            </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {trending.map((s, idx) => (
            <motion.div 
              key={s.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 + (idx * 0.1) }}
              onClick={() => onSelect(s.topic)}
              className="glass-panel p-5 bg-panel-bg border-border group hover:border-primary transition-all cursor-pointer relative overflow-hidden rounded-2xl shadow-sm"
            >
              <div className="flex items-center justify-between mb-4">
                 <span className="text-[7px] font-black text-primary tracking-[0.3em] uppercase">{s.region} / {s.sector}</span>
                 <div className="px-1.5 py-0.5 bg-secondary border border-border rounded text-[7px] font-black text-text-muted flex items-center gap-1 group-hover:text-primary transition-colors">
                    <TrendingUp size={8} /> {s.community_interest || "HIGH"} INTEREST
                 </div>
              </div>
              <h4 className="text-[11px] font-black text-foreground italic uppercase tracking-tight leading-snug group-hover:text-primary transition-colors mb-2">
                {s.topic}
              </h4>
              <div className="absolute -bottom-2 -right-2 opacity-[0.03] group-hover:opacity-[0.08] transition-opacity pointer-events-none">
                 <Globe size={80} />
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Strategic Market Assets to Watch */}
      <section>
        <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-hazard/20 border border-hazard/30 rounded-xl text-hazard shadow-sm">
                <AlertCircle size={18} />
              </div>
              <div>
                <h3 className="text-sm font-black tracking-widest text-foreground uppercase italic">Assets & Commodities Watchlist</h3>
                <p className="text-[10px] font-bold text-text-muted uppercase tracking-tighter">High-Volatility Tickers with Historical Differences</p>
              </div>
            </div>
            <div className="text-[10px] font-black text-text-muted uppercase tracking-widest border border-border px-4 py-1.5 rounded-2xl bg-panel-bg shadow-sm">
                {alerts.filter(a => a.type === 'volatility').length} Shocks Detected
            </div>
        </div>

        {alerts.filter(a => a.type === 'volatility' || a.ticker).length === 0 ? (
          <div className="py-20 text-center glass-panel border-dashed border-border bg-panel-bg/40">
             <TrendingUp size={40} className="text-text-muted/20 mx-auto mb-4" />
             <p className="text-[10px] font-black text-text-muted uppercase tracking-widest italic">No significant market deviations detected.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {alerts
              .filter(a => a.type === 'volatility' || a.ticker)
              .slice(0, 8)
              .map((alert, idx) => {
                const diff = alert.alert_payload?.change_pct || 0;
                const isPositive = diff > 0;
                return (
                  <motion.div 
                    key={alert.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 * idx }}
                    className="glass-panel p-5 bg-panel-bg border-border group hover:border-border/80 transition-all rounded-2xl shadow-sm relative overflow-hidden"
                  >
                    <div className="flex items-start justify-between mb-4">
                       <div className="flex flex-col">
                           <span className="text-[8px] font-black text-text-muted tracking-[0.2em] uppercase mb-1">
                               {alert.ticker === 'GLOBAL' ? 'Macro' : 'Ticker'}
                           </span>
                           <h4 className="text-[16px] font-black text-foreground italic uppercase tracking-tight leading-none group-hover:text-primary transition-colors">
                               ${alert.ticker}
                           </h4>
                       </div>
                       <div className={`text-[12px] font-black px-2 py-1 rounded-lg border ${isPositive ? 'bg-success/10 text-success border-success/20' : 'bg-error/10 text-error border-error/20'}`}>
                           {isPositive ? '+' : ''}{diff.toFixed(2)}%
                       </div>
                    </div>
                    <p className="text-[9px] font-bold text-text-muted/80 leading-relaxed uppercase overflow-hidden line-clamp-3">
                       {alert.content}
                    </p>
                  </motion.div>
                );
            })}
          </div>
        )}
      </section>

    </div>
  );
}

function ScenarioCard({ scenario, idx, onClick }: { scenario: Scenario, idx: number, onClick: () => void }) {
  const statusColors = {
      CRITICAL: "text-error bg-error/10 border-error/20",
      ACTIVE: "text-success bg-success/10 border-success/20",
      EMERGING: "text-primary bg-primary/10 border-primary/20",
      STABILIZED: "text-success bg-success/10 border-success/20",
      RESOLVING: "text-text-muted bg-text-muted/10 border-border"
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: idx * 0.1 }}
      onClick={onClick}
      className="glass-panel p-6 bg-panel-bg border-border group hover:border-primary transition-all cursor-pointer relative overflow-hidden min-h-[180px] flex flex-col rounded-2xl shadow-sm"
    >
      <div className="flex items-start justify-between mb-6">
        <div className="flex flex-col">
            <span className="text-[8px] font-black text-text-muted tracking-widest uppercase mb-1">{scenario.region} // {scenario.sector}</span>
            <h4 className="text-[15px] font-black text-foreground italic group-hover:text-primary transition-colors leading-tight uppercase tracking-tight">
                {scenario.topic}
            </h4>
        </div>
        <div className={`px-2 py-1 rounded-lg text-[8px] font-black tracking-widest transition-all border ${statusColors[scenario.status]}`}>
            {scenario.status}
        </div>
      </div>

      <div className="mt-auto space-y-4 pt-4 border-t border-border/60">
        <div className="flex justify-between items-end">
            <div className="flex flex-col gap-1">
               <span className="text-[7px] font-black text-text-muted uppercase tracking-widest">TACTICAL RISK SCORE</span>
               <div className="flex items-center gap-2">
                  <div className={`text-xl font-black italic ${scenario.risk_score > 0.7 ? 'text-error' : 'text-primary'}`}>
                    {(scenario.risk_score * 100).toFixed(0)}%
                  </div>
                  <div className="h-1 w-16 bg-secondary rounded-full overflow-hidden">
                     <div className={`h-full ${scenario.risk_score > 0.7 ? 'bg-error' : 'bg-primary'}`} style={{ width: `${scenario.risk_score * 100}%` }} />
                  </div>
               </div>
            </div>
            <div className="p-2 border border-border rounded-xl text-text-muted group-hover:text-primary group-hover:border-primary transition-all bg-secondary/30">
               <ChevronRight size={16} />
            </div>
        </div>
      </div>

      {/* Aesthetic Background Pattern */}
      <div className="absolute -bottom-4 -right-4 opacity-[0.03] group-hover:opacity-[0.08] transition-opacity pointer-events-none">
         {scenario.status === 'CRITICAL' ? <AlertCircle size={100} /> : <ShieldCheck size={100} />}
      </div>
    </motion.div>
  );
}
