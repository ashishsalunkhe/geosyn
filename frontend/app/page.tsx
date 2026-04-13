"use client";

import React, { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  fetchEvents, 
  syncMarkets, 
  fetchAlerts, 
  clearAlerts, 
  fetchNexusGraph, 
  syncNexus,
  fetchMarketCorrelation,
  fetchScenarios,
  fetchTrendingScenarios,
  fetchPortfolioSummary,
  followScenario
} from "../lib/api";
import MarketChart from "../components/MarketChart";
import AlertPulse from "../components/AlertPulse";
import CausalNexus from "../components/CausalNexus";
import IntelligenceBrief from "../components/IntelligenceBrief";
import MarketLandscape from "../components/MarketLandscape";
import AnalyticsKPIStrip from "../components/AnalyticsKPIStrip";
import LiveFeed from "../components/LiveFeed";
import InsightVault from "../components/InsightVault";
import ClusterMap from "../components/ClusterMap";
import ScenarioHUD from "../components/ScenarioHUD";
import TacticalSidebar from "../components/TacticalSidebar";
import { Shield, Zap, Target, Search, Bell, GitBranch, LayoutDashboard, Database, Star } from "lucide-react";

const EXCHANGES = [
  { id: "^BSESN", label: "BSE SENSEX" },
  { id: "^NSEI", label: "NIFTY 50" },
  { id: "^GSPC", label: "S&P 500" },
  { id: "CL=F", label: "Crude Oil" },
  { id: "GC=F", label: "Gold Spot" },
];

export default function Home() {
  const [events, setEvents] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [marketData, setMarketData] = useState<any>(null);
  const [selectedTicker, setSelectedTicker] = useState("CL=F");
  const [scenarioQuery, setScenarioQuery] = useState("");
  const [activeTopic, setActiveTopic] = useState("");
  const [loading, setLoading] = useState(true);
  const [actionBusy, setActionBusy] = useState(false);
  const [activeView, setActiveView] = useState<"brief" | "nexus" | "clusters" | "vault">("brief");
  const [nexusData, setNexusData] = useState<{ nodes: any[]; links: any[] }>({ nodes: [], links: [] });
  
  // Tactical Scenario State (Taiyo-style)
  const [trackedScenarios, setTrackedScenarios] = useState<any[]>([]);
  const [trendingScenarios, setTrendingScenarios] = useState<any[]>([]);
  const [summaryData, setSummaryData] = useState<any>(null);
  const [activeRegion, setActiveRegion] = useState("GLOBAL");
  const [activeSector, setActiveSector] = useState("GENERAL");

  const loadData = useCallback(async () => {
    try {
      const [evs, alrts, market, scens, trends, summary] = await Promise.all([
        fetchEvents(),
        fetchAlerts(),
        fetchMarketCorrelation(selectedTicker),
        fetchScenarios(activeRegion, activeSector),
        fetchTrendingScenarios(),
        fetchPortfolioSummary()
      ]);
      setEvents(evs);
      setAlerts(alrts);
      setMarketData(market);
      setTrackedScenarios(scens);
      setTrendingScenarios(trends);
      setSummaryData(summary);
      
      const graph = await fetchNexusGraph();
      setNexusData(graph);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [selectedTicker, activeRegion, activeSector]);

  useEffect(() => {
    loadData();
    const interval = setInterval(() => {
      fetchAlerts().then(setAlerts).catch(console.error);
    }, 60000);
    return () => clearInterval(interval);
  }, [loadData]);

  const handleAnalyzeTopic = (topic: string) => {
    setScenarioQuery(topic);
    setActiveTopic(topic);
    setActiveView("brief");
    
    // Intelligent ticker selection
    const lowerTopic = topic.toLowerCase();
    if (lowerTopic.includes("oil") || lowerTopic.includes("energy") || lowerTopic.includes("crude")) {
      setSelectedTicker("CL=F");
    } else if (lowerTopic.includes("gold") || lowerTopic.includes("precious")) {
      setSelectedTicker("GC=F");
    } else if (lowerTopic.includes("india") || lowerTopic.includes("nifty") || lowerTopic.includes("bse")) {
      setSelectedTicker("^NSEI");
    }
  };

  const handleFollowTopic = async () => {
    if (!activeTopic) return;
    try {
      setActionBusy(true);
      await followScenario(activeTopic, activeRegion, activeSector);
      const scens = await fetchScenarios(activeRegion, activeSector);
      setTrackedScenarios(scens);
    } catch (err) {
      console.error(err);
    } finally {
      setActionBusy(false);
    }
  };

  const handleFilterChange = (region: string, sector: string) => {
    setActiveRegion(region);
    setActiveSector(sector);
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!scenarioQuery) return;
    handleAnalyzeTopic(scenarioQuery);
  };

  const handleFullSync = async () => {
    try {
      setActionBusy(true);
      await syncMarkets();
      await loadData();
    } catch (err) { console.error(err); } finally { setActionBusy(false); }
  };

  return (
    <div className="min-h-screen bg-black text-zinc-100 font-sans antialiased flex">
      
      {/* Tactical Sidebar (Taiyo Discovery Pattern) */}
      <aside className="hidden lg:flex w-[320px] h-screen flex-col sticky top-0 border-r border-zinc-900 bg-zinc-950/40 backdrop-blur-xl">
        <TacticalSidebar 
          onFilterChange={handleFilterChange} 
          activeRegion={activeRegion}
          activeSector={activeSector}
          scenarios={trackedScenarios}
          onSelectScenario={handleAnalyzeTopic}
        />
      </aside>

      <main className="flex-1 flex flex-col min-h-screen">
        
        {/* Persistent Tactical Header */}
        <header className="p-6 border-b border-zinc-900 bg-black/40 backdrop-blur-md sticky top-0 z-50">
          <div className="max-w-[1400px] px-8 mx-auto flex items-center justify-between w-full">
            <div className="flex items-center gap-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-black shadow-[0_0_20px_rgba(99,102,241,0.4)]">
                <Shield size={22} />
              </div>
              <h1 className="text-xl font-black tracking-tighter uppercase italic flex items-center gap-2 group cursor-pointer" onClick={() => handleAnalyzeTopic("")}>
                GeoSyn <span className="text-primary opacity-60">Intelligence</span>
              </h1>
            </div>

            <nav className="flex items-center p-1 bg-zinc-900/80 rounded-xl border border-white/5">
              {[
                { id: "brief", label: "Intelligence", icon: LayoutDashboard },
                { id: "nexus", label: "Causal Nexus", icon: GitBranch },
                { id: "clusters", label: "Clusters", icon: Target },
                { id: "vault", label: "Insight Vault", icon: Database }
              ].map((btn) => (
                <button
                  key={btn.id}
                  onClick={() => setActiveView(btn.id as any)}
                  className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-[9px] font-black uppercase tracking-widest transition-all ${
                    activeView === btn.id ? "bg-primary text-black shadow-lg" : "text-zinc-500 hover:text-white"
                  }`}
                >
                  <btn.icon size={12} />
                  {btn.label}
                </button>
              ))}
              
              <button 
                onClick={() => setActiveTopic("")}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-[9px] font-black uppercase tracking-widest transition-all ${
                  !activeTopic ? "bg-primary text-black" : "text-zinc-500 hover:text-white"
                }`}
              >
                <LayoutDashboard size={12} />
                Landscape
              </button>
            </nav>

            <div className="flex items-center gap-4">
               <button 
                  onClick={handleFullSync}
                  disabled={actionBusy}
                  className="px-4 py-2.5 bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 rounded-xl text-[9px] font-black uppercase tracking-widest hover:bg-emerald-500/20 transition-all flex items-center gap-2"
                >
                  <Zap size={12} className={actionBusy ? 'animate-spin' : ''} />
                  {actionBusy ? 'Syncing...' : 'Sync Pipeline'}
              </button>
            </div>
          </div>
        </header>

        <div className="p-8 max-w-[1400px] w-full mx-auto">
          
          {/* High-Density Portfolio Analytics Strip */}
          <AnalyticsKPIStrip data={summaryData} loading={loading} />

          {/* Scenario KPI Distribution (Taiyo Pattern) */}
          <ScenarioHUD scenarios={trackedScenarios} />
          
          <form className="relative group mb-12" onSubmit={handleSearch}>
            <Search className="absolute left-6 top-1/2 -translate-y-1/2 text-zinc-600 group-focus-within:text-primary transition-colors" size={24} />
            <input 
              type="text" 
              placeholder="Search Tactical Topic or Strategic Project Scope..."
              className="w-full h-16 md:h-20 pl-16 pr-32 bg-zinc-900 border-2 border-zinc-800 rounded-3xl text-base font-bold outline-none focus:border-primary/40 focus:bg-zinc-900/80 transition-all text-white placeholder:text-zinc-700 shadow-2xl"
              value={scenarioQuery}
              onChange={(e) => setScenarioQuery(e.target.value)}
            />
            <button 
              type="submit"
              className="absolute right-4 top-1/2 -translate-y-1/2 h-12 px-8 bg-primary text-black text-[10px] font-black uppercase tracking-widest rounded-2xl shadow-xl hover:scale-105 active:scale-95 transition-all"
            >
              Search
            </button>
          </form>

          <div className="grid grid-cols-1 xl:grid-cols-12 gap-10">
            
            <div className="xl:col-span-8 space-y-10">
              <AnimatePresence mode="wait">
                {activeView === "brief" && (
                  <motion.div 
                    key="brief"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                  >
                    {activeTopic ? (
                      <>
                        <div className="flex justify-end mb-4">
                          <button 
                            onClick={handleFollowTopic}
                            disabled={actionBusy}
                            className="flex items-center gap-2 px-4 py-2 bg-amber-500/10 border border-amber-500/20 text-amber-500 rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-amber-500/20 transition-all"
                          >
                            <Star size={12} fill={trackedScenarios.find(s => s.topic === activeTopic) ? "currentColor" : "none"} />
                            {trackedScenarios.find(s => s.topic === activeTopic) ? "Tracking Scenario" : "Follow Scenario"}
                          </button>
                        </div>
                        <IntelligenceBrief topic={activeTopic} ticker={selectedTicker} />
                      </>
                    ) : (
                      <MarketLandscape 
                        scenarios={trackedScenarios} 
                        trending={trendingScenarios} 
                        onSelect={handleAnalyzeTopic} 
                      />
                    )}
                  </motion.div>
                )}
                {activeView === "vault" && (
                  <motion.div key="vault" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
                    <InsightVault />
                  </motion.div>
                )}
                {activeView === "nexus" && (
                  <motion.div key="nexus" initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} className="glass-panel p-8 min-h-[600px]">
                    <CausalNexus graphData={nexusData} onSync={syncNexus} isSyncing={actionBusy} onNodeClick={handleAnalyzeTopic} />
                  </motion.div>
                )}
                {activeView === "clusters" && (
                  <motion.div key="clusters" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
                    <ClusterMap clusters={events} onAnalyze={handleAnalyzeTopic} />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Right Column: Tactical HUD */}
            <div className="xl:col-span-4 flex flex-col gap-10 min-w-0">
               <section className="glass-panel p-6 bg-black/40 border-zinc-800 sticky top-32">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-[10px] font-black tracking-widest text-zinc-500 uppercase">Market Correlation</h3>
                    <div className="flex gap-1">
                      {EXCHANGES.map(ex => (
                        <button 
                          key={ex.id}
                          onClick={() => setSelectedTicker(ex.id)}
                          className={`w-2 h-2 rounded-full transition-all ${selectedTicker === ex.id ? 'bg-primary scale-125' : 'bg-zinc-800'}`}
                        />
                      ))}
                    </div>
                  </div>
                  <div className="h-[250px] mb-8">
                    <MarketChart data={marketData} />
                  </div>
                  <div className="pt-8 border-t border-zinc-800/50">
                    <AlertPulse alerts={alerts} onClear={clearAlerts} />
                  </div>
               </section>
               
               <LiveFeed onAnalyze={handleAnalyzeTopic} />
            </div>

          </div>
        </div>


        <footer className="mt-auto py-12 px-8 border-t border-zinc-900 bg-zinc-950/20 text-center">
            <div className="flex items-center justify-center gap-6 opacity-30">
               <span className="text-[9px] font-black uppercase tracking-[0.4em]">GeoSyn Intelligence Framework v4.2.0</span>
               <div className="w-1 h-1 rounded-full bg-zinc-600" />
               <span className="text-[9px] font-black uppercase tracking-[0.4em]">Secure Terminal</span>
            </div>
        </footer>
      </main>
    </div>
  );
}
