"use client";

import React, { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  fetchEvents, 
  syncMarkets, 
  fetchAlerts, 
  clearAlerts, 
  fetchPortfolioSummary,
  followScenario,
  fetchIntelligenceComposite,
  fetchMarketCorrelation,
  fetchScenarios,
  fetchTrendingScenarios,
  fetchNexusGraph,
  syncNexus
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
import TopicSidebar from "../components/TopicSidebar";
import GeoSynIndex from "../components/GeoSynIndex";
import Glossary from "../components/Glossary";
import { 
  Shield, Zap, Target, Search, Bell, GitBranch, LayoutDashboard, 
  Database, Star, Sun, Moon, Book, Network
} from "lucide-react";

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
  const [activeView, setActiveView] = useState<"brief" | "nexus" | "clusters" | "vault" | "glossary">("brief");
  const [nexusData, setNexusData] = useState<{ nodes: any[]; links: any[] }>({ nodes: [], links: [] });
  
  // Tactical Scenario State (Taiyo-style)
  const [trackedScenarios, setTrackedScenarios] = useState<any[]>([]);
  const [trendingScenarios, setTrendingScenarios] = useState<any[]>([]);
  const [summaryData, setSummaryData] = useState<any>({
    avg_fragility: 0,
    total_signals: 0,
    critical_count: 0,
    avg_confidence: 0,
    market_exposure: 0
  });
  const [activeRegion, setActiveRegion] = useState("GLOBAL");
  const [activeSector, setActiveSector] = useState("GENERAL");
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [compositeData, setCompositeData] = useState<any>(null);

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

      const composite = await fetchIntelligenceComposite();
      setCompositeData(composite);
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

    // Initialise Theme
    const savedTheme = localStorage.getItem("geosyn-theme") as "dark" | "light";
    if (savedTheme) {
      setTheme(savedTheme);
      document.documentElement.classList.toggle("light", savedTheme === "light");
    }

    return () => clearInterval(interval);
  }, [loadData]);

  const toggleTheme = () => {
    const newTheme = theme === "dark" ? "light" : "dark";
    setTheme(newTheme);
    localStorage.setItem("geosyn-theme", newTheme);
    document.documentElement.classList.toggle("light", newTheme === "light");
  };

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
    <div className={`min-h-screen bg-background text-foreground font-sans antialiased flex transition-colors duration-500 ${theme}`}>
      
      {/* Topic Search & Filters */}
      <aside className="hidden xl:flex w-[280px] 2xl:w-[320px] h-screen flex-col sticky top-0 border-r border-border bg-panel-bg/40 backdrop-blur-3xl z-40 transition-all">
        <TopicSidebar 
          onFilterChange={handleFilterChange} 
          activeRegion={activeRegion}
          activeSector={activeSector}
          scenarios={trackedScenarios}
          onSelectScenario={handleAnalyzeTopic}
        />
      </aside>

      <main className="flex-1 flex flex-col min-h-screen min-w-0 overflow-x-hidden">
        
        {/* Main Dashboard Header */}
        <header className="px-4 py-3 md:px-6 md:py-4 lg:px-8 lg:py-5 border-b border-border bg-background/40 backdrop-blur-md sticky top-0 z-50">
          <div className="max-w-[1400px] mx-auto flex items-center justify-between w-full gap-3">
            <div className="flex items-center gap-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-black">
                <Shield size={22} />
              </div>
              <h1 className="text-xl font-black tracking-tighter uppercase italic flex items-center gap-2 group cursor-pointer" onClick={() => handleAnalyzeTopic("")}>
                GeoSyn <span className="text-primary">Intelligence</span>
              </h1>
            </div>

            <nav className="flex items-center p-1 bg-panel-bg rounded-xl border border-border overflow-x-auto scrollbar-none">
              {[
                { id: "brief", label: "Intel", icon: LayoutDashboard },
                { id: "nexus", label: "Nexus", icon: GitBranch },
                { id: "clusters", label: "Groups", icon: Network },
                { id: "vault", label: "Vault", icon: Database },
                { id: "glossary", label: "Glossary", icon: Book },
              ].map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveView(item.id as any)}
                  className={`flex items-center gap-2.5 px-6 py-2.5 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all ${
                    activeView === item.id 
                      ? "bg-panel-bg text-primary border border-primary/20" 
                      : "text-text-muted hover:text-foreground hover:bg-foreground/5"
                  }`}
                >
                  <item.icon size={13} className={activeView === item.id ? "text-primary" : "text-text-muted"} />
                  {item.label}
                </button>
              ))}
              <div className="w-[1px] h-4 bg-border mx-1" />
              <button 
                 onClick={() => {
                   setActiveView("brief");
                   setActiveTopic("");
                 }}
                 className={`flex items-center gap-2 px-6 py-2.5 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all ${
                   activeView === "brief" && !activeTopic ? "bg-panel-bg text-primary border border-primary/20" : "text-text-muted hover:text-foreground"
                 }`}
               >
                 <LayoutDashboard size={11} className={activeView === "brief" && !activeTopic ? "text-primary" : "text-text-muted"} />
                 <span className="hidden sm:inline">Landscape</span>
               </button>
            </nav>

            <div className="flex items-center gap-2 shrink-0">
               <button 
                  onClick={handleFullSync}
                  disabled={actionBusy}
                  className="px-3 md:px-4 py-2 bg-success/10 border border-success/20 text-success rounded-xl text-[8px] md:text-[9px] font-black uppercase tracking-widest hover:bg-success/20 transition-all flex items-center gap-1.5"
                >
                  <Zap size={11} className={actionBusy ? 'animate-spin' : ''} />
                  <span className="hidden md:inline">{actionBusy ? 'Syncing...' : 'Sync'}</span>
              </button>

              <button 
                onClick={toggleTheme}
                className="p-2.5 rounded-xl bg-panel-bg border border-border text-text-muted hover:text-primary transition-all ml-1"
                title={theme === "dark" ? "Switch to Light Mode" : "Switch to Dark Mode"}
              >
                {theme === "dark" ? <Sun size={15} /> : <Moon size={15} />}
              </button>
            </div>
          </div>
        </header>

        <div className="p-4 md:p-6 xl:p-8 max-w-[1400px] w-full mx-auto">
          
          {/* High-Density Portfolio Analytics Strip */}
          <AnalyticsKPIStrip data={summaryData} loading={loading} />

          {/* Scenario KPI Distribution (Taiyo Pattern) */}
          <ScenarioHUD scenarios={trackedScenarios} />
          
          <form className="relative group mb-12" onSubmit={handleSearch}>
            <input 
                 type="text" 
                 placeholder="Search tactical Nexus..."
                 value={scenarioQuery}
                 onChange={(e) => setScenarioQuery(e.target.value)}
                 className="w-full h-16 bg-panel-bg border border-border rounded-2xl text-xs md:text-sm font-bold outline-none focus:border-primary/40 transition-all text-foreground placeholder:text-text-muted italic px-16"
               />
               <Search className="absolute left-6 top-1/2 -translate-y-1/2 text-primary" size={18} />
            <button 
              type="submit"
              className="absolute right-3 top-1/2 -translate-y-1/2 h-10 px-6 bg-primary text-black text-[10px] font-black uppercase tracking-widest rounded-xl hover:bg-primary-dark transition-all"
            >
              Search
            </button>
          </form>

          {/* GeoSyn Intelligence Index (The Divergence Engine) */}
          <GeoSynIndex data={compositeData} onSelectTopic={handleAnalyzeTopic} />

          <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 xl:gap-10">
            
            <div className="xl:col-span-8 space-y-6 xl:space-y-10 min-w-0">
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
                            className="flex items-center gap-2 px-4 py-2 bg-hazard/10 border border-hazard/20 text-hazard rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-hazard/20 transition-all"
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
                        alerts={alerts}
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
                  <motion.div key="nexus" initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} className="glass-panel p-8 min-h-[600px] border-primary/10">
                    <CausalNexus graphData={nexusData} onSync={syncNexus} isSyncing={actionBusy} onNodeClick={handleAnalyzeTopic} theme={theme} />
                  </motion.div>
                )}
                { activeView === "clusters" && (
                  <motion.div key="clusters" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
                    <ClusterMap clusters={events} onAnalyze={handleAnalyzeTopic} />
                  </motion.div>
                )}
                {activeView === "glossary" && (
                  <motion.div key="glossary" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
                    <Glossary />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Right Column: Tactical HUD */}
            <div className="xl:col-span-4 flex flex-col gap-6 xl:gap-10 min-w-0">
               <section className="glass-panel p-4 md:p-6 xl:sticky xl:top-24">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-[10px] font-black tracking-widest text-foreground uppercase">Market Correlation</h3>
                    <div className="flex gap-1">
                      {EXCHANGES.map(ex => (
                        <button 
                          key={ex.id}
                          onClick={() => setSelectedTicker(ex.id)}
                          className={`w-2 h-2 rounded-full transition-all ${selectedTicker === ex.id ? 'bg-primary scale-125' : 'bg-border'}`}
                        />
                      ))}
                    </div>
                  </div>
                  <div className="h-[250px] mb-12">
                    <MarketChart data={marketData} />
                  </div>
                  <div className="pt-12 border-t border-border">
                    <AlertPulse alerts={alerts} onClear={clearAlerts} />
                  </div>
               </section>
               
               <LiveFeed onAnalyze={handleAnalyzeTopic} />
            </div>

          </div>
        </div>


        <footer className="mt-auto py-12 px-8 border-t border-border bg-panel-bg text-center">
            <div className="flex items-center justify-center gap-6 opacity-30">
               <span className="text-[9px] font-black uppercase tracking-[0.4em]">GeoSyn Intelligence Framework v4.2.0</span>
               <div className="w-1 h-1 rounded-full bg-text-muted" />
               <span className="text-[9px] font-black uppercase tracking-[0.4em]">Secure Terminal</span>
            </div>
        </footer>
      </main>
    </div>
  );
}
