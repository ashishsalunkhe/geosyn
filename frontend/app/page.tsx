"use client";

import React, { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  fetchEventsV2, 
  syncMarkets, 
  fetchAlertsV2, 
  generateAlertsV2,
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
        fetchEventsV2(),
        fetchAlertsV2(),
        fetchMarketCorrelation(selectedTicker),
        fetchScenarios(activeRegion, activeSector),
        fetchTrendingScenarios(),
        fetchPortfolioSummary()
      ]);
      setEvents(evs as any[]);
      setAlerts(alrts as any[]);
      setMarketData(market as any);
      setTrackedScenarios(scens as any[]);
      setTrendingScenarios(trends as any[]);
      setSummaryData(summary as any);
      
      const graph = await fetchNexusGraph();
      setNexusData(graph as { nodes: any[]; links: any[] });

      const composite = await fetchIntelligenceComposite();
      setCompositeData(composite as any);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [selectedTicker, activeRegion, activeSector]);

  useEffect(() => {
    loadData();
    const interval = setInterval(() => {
      fetchAlertsV2().then(setAlerts).catch(console.error);
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
      setTrackedScenarios(scens as any[]);
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
      await generateAlertsV2();
      await loadData();
    } catch (err) { console.error(err); } finally { setActionBusy(false); }
  };

  return (
    <div className={`min-h-screen bg-background text-foreground font-sans antialiased xl:flex transition-colors duration-500 ${theme}`}>
      
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

      <main className="flex min-h-screen min-w-0 flex-1 flex-col overflow-x-hidden">
        
        {/* Main Dashboard Header */}
        <header className="sticky top-0 z-50 border-b border-border bg-background/70 px-4 py-3 backdrop-blur-md md:px-6 md:py-4 lg:px-8 lg:py-5">
          <div className="mx-auto flex max-w-[1400px] flex-wrap items-center justify-between gap-3 md:gap-4">
            <div className="flex min-w-0 items-center gap-3 md:gap-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-black">
                <Shield size={22} />
              </div>
              <h1 className="flex min-w-0 items-center gap-2 text-base font-black uppercase italic tracking-tighter sm:text-xl group cursor-pointer" onClick={() => handleAnalyzeTopic("")}>
                <span className="truncate">GeoSyn</span>
                <span className="truncate text-primary">Intelligence</span>
              </h1>
            </div>

            <nav className="order-3 -mx-1 flex w-full items-center gap-1 overflow-x-auto rounded-xl border border-border bg-panel-bg p-1 scrollbar-none xl:order-none xl:mx-0 xl:w-auto">
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
                  className={`flex shrink-0 items-center gap-2 rounded-2xl px-3 py-2 text-[10px] font-black uppercase tracking-widest transition-all sm:px-4 xl:px-6 ${
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
                 className={`flex shrink-0 items-center gap-2 rounded-2xl px-3 py-2 text-[10px] font-black uppercase tracking-widest transition-all sm:px-4 xl:px-6 ${
                   activeView === "brief" && !activeTopic ? "bg-panel-bg text-primary border border-primary/20" : "text-text-muted hover:text-foreground"
                 }`}
               >
                 <LayoutDashboard size={11} className={activeView === "brief" && !activeTopic ? "text-primary" : "text-text-muted"} />
                 <span className="hidden sm:inline">Landscape</span>
               </button>
            </nav>

            <div className="flex shrink-0 items-center gap-2 self-start sm:self-auto">
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

        <div className="mx-auto w-full max-w-[1400px] p-4 md:p-6 xl:p-8">
          
          {/* High-Density Portfolio Analytics Strip */}
          <AnalyticsKPIStrip data={summaryData} loading={loading} />

          {/* Scenario KPI Distribution (Taiyo Pattern) */}
          <ScenarioHUD scenarios={trackedScenarios} />
          
          <form className="group relative mb-8 md:mb-12" onSubmit={handleSearch}>
            <input 
                 type="text" 
                 placeholder="Search tactical Nexus..."
                 value={scenarioQuery}
                 onChange={(e) => setScenarioQuery(e.target.value)}
                 className="h-14 w-full rounded-2xl border border-border bg-panel-bg px-12 pr-24 text-xs font-bold italic text-foreground outline-none transition-all placeholder:text-text-muted focus:border-primary/40 md:h-16 md:px-16 md:pr-32 md:text-sm"
               />
               <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-primary md:left-6" size={18} />
            <button 
              type="submit"
              className="absolute right-2 top-1/2 h-9 -translate-y-1/2 rounded-xl bg-primary px-4 text-[10px] font-black uppercase tracking-widest text-black transition-all hover:bg-primary-dark md:right-3 md:h-10 md:px-6"
            >
              Search
            </button>
          </form>

          {/* GeoSyn Intelligence Index (The Divergence Engine) */}
          <GeoSynIndex data={compositeData} onSelectTopic={handleAnalyzeTopic} />

          <div className="grid grid-cols-1 gap-6 xl:grid-cols-12 xl:gap-10">
            
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
                        <div className="mb-4 flex justify-start sm:justify-end">
                          <button 
                            onClick={handleFollowTopic}
                            disabled={actionBusy}
                            className="flex w-full items-center justify-center gap-2 rounded-xl border border-hazard/20 bg-hazard/10 px-4 py-2 text-[10px] font-black uppercase tracking-widest text-hazard transition-all hover:bg-hazard/20 sm:w-auto"
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
                  <motion.div key="nexus" initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} className="glass-panel min-h-[420px] border-primary/10 p-4 md:min-h-[600px] md:p-8">
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
                  <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
                    <h3 className="text-[10px] font-black tracking-widest text-foreground uppercase">Market Correlation</h3>
                    <div className="flex flex-wrap gap-1">
                      {EXCHANGES.map(ex => (
                        <button 
                          key={ex.id}
                          onClick={() => setSelectedTicker(ex.id)}
                          className={`w-2 h-2 rounded-full transition-all ${selectedTicker === ex.id ? 'bg-primary scale-125' : 'bg-border'}`}
                        />
                      ))}
                    </div>
                  </div>
                  <div className="mb-8 h-[220px] md:mb-12 md:h-[250px]">
                    <MarketChart data={marketData} />
                  </div>
                  <div className="border-t border-border pt-8 md:pt-12">
                    <AlertPulse alerts={alerts} onRefresh={async () => {
      await generateAlertsV2();
      const freshAlerts = await fetchAlertsV2();
      setAlerts(freshAlerts as any[]);
                    }} />
                  </div>
               </section>
               
               <LiveFeed onAnalyze={handleAnalyzeTopic} />
            </div>

          </div>
        </div>


        <footer className="mt-auto border-t border-border bg-panel-bg px-4 py-8 text-center md:px-8 md:py-12">
            <div className="flex flex-col items-center justify-center gap-3 opacity-30 sm:flex-row sm:gap-6">
               <span className="text-[9px] font-black uppercase tracking-[0.35em]">GeoSyn Intelligence Framework v4.2.0</span>
               <div className="w-1 h-1 rounded-full bg-text-muted" />
               <span className="text-[9px] font-black uppercase tracking-[0.35em]">Secure Terminal</span>
            </div>
        </footer>
      </main>
    </div>
  );
}
