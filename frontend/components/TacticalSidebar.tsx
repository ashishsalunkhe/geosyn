"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Globe, 
  Inbox, 
  Filter, 
  ChevronRight, 
  ChevronDown,
  Star, 
  Briefcase,
  Layers,
  Search,
  Settings2
} from "lucide-react";

interface TacticalSidebarProps {
  onFilterChange: (region: string, sector: string) => void;
  activeRegion: string;
  activeSector: string;
  scenarios: any[];
  onSelectScenario: (topic: string) => void;
}

const TAXONOMY = [
  {
    id: "industries",
    label: "Advanced Industries",
    icon: Briefcase,
    children: [
        { id: "AERO", label: "Aerospace & Defense" },
        { id: "AUTO", label: "Automotive & Logistics" },
        { id: "ELECT", label: "Advanced Electronics" }
    ]
  },
  {
    id: "energy",
    label: "Energy & Materials",
    icon: Layers,
    children: [
        { id: "POWER", label: "Power & Utilities" },
        { id: "MINING", label: "Rare Earth & Critical" },
        { id: "RENEW", label: "Renewable Systems" }
    ]
  },
  {
    id: "digital",
    label: "Digital Infrastructure",
    icon: Globe,
    children: [
        { id: "TELCO", label: "Telecommunications" },
        { id: "DATA", label: "Data Centers" },
        { id: "CYBER", label: "Cyber Sovereignty" }
    ]
  }
];

const REGIONS = [
  { id: "GLOBAL", label: "Global Presence" },
  { id: "APAC", label: "East Asia & Pacific" },
  { id: "EMEA", label: "Europe & Central Asia" },
  { id: "MENA", label: "Middle East & North Africa" },
  { id: "AMER", label: "Americas" }
];

export default function TacticalSidebar({ 
  onFilterChange, 
  activeRegion, 
  activeSector, 
  scenarios,
  onSelectScenario 
}: TacticalSidebarProps) {
  const [expanded, setExpanded] = useState<string[]>(["industries"]);

  const toggleExpand = (id: string) => {
    setExpanded(prev => prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]);
  };

  return (
    <div className="flex flex-col h-full bg-zinc-950/20 p-6 gap-8 select-none border-r border-zinc-900 overflow-y-auto custom-scrollbar">
      
      {/* Platform Navigation (Taiyo Pattern) */}
      <section className="space-y-1">
         <h3 className="text-[10px] font-black text-zinc-600 tracking-[0.2em] uppercase mb-4 px-1">Tactical Orbit</h3>
         {[
           { label: "Search Templates", icon: Search },
           { label: "Advanced Analysis", icon: Settings2 },
         ].map((item, i) => (
           <button key={i} className="w-full flex items-center justify-between px-3 py-2 rounded-xl text-[10px] font-black text-zinc-500 hover:bg-white/5 hover:text-white transition-all group">
             <div className="flex items-center gap-3">
               <item.icon size={13} className="text-zinc-700 group-hover:text-primary transition-colors" />
               <span className="uppercase tracking-widest">{item.label}</span>
             </div>
             <ChevronRight size={10} className="text-zinc-800" />
           </button>
         ))}
      </section>

      {/* Hierarchical Filter Taxonomy */}
      <section>
        <div className="flex items-center justify-between mb-4 px-1">
           <h3 className="text-[10px] font-black text-zinc-400 tracking-[0.2em] uppercase flex items-center gap-2">
              <Filter size={12} className="text-primary" /> Sector Taxonomy
           </h3>
           <button className="text-[9px] font-bold text-primary hover:underline uppercase tracking-tighter">Reset</button>
        </div>
        
        <div className="space-y-1">
          {TAXONOMY.map(category => (
            <div key={category.id} className="mb-2">
              <button
                onClick={() => toggleExpand(category.id)}
                className="w-full flex items-center justify-between px-3 py-2 text-[10px] font-black text-zinc-500 hover:text-zinc-300 transition-colors"
              >
                <div className="flex items-center gap-2 uppercase tracking-widest">
                  <category.icon size={13} className={expanded.includes(category.id) ? 'text-primary' : 'text-zinc-800'} />
                  {category.label}
                </div>
                {expanded.includes(category.id) ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
              </button>
              
              <AnimatePresence>
                {expanded.includes(category.id) && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="overflow-hidden ml-4 mt-1 border-l border-zinc-900"
                  >
                    {category.children.map(child => (
                      <button
                        key={child.id}
                        onClick={() => onFilterChange(activeRegion, child.id)}
                        className={`w-full text-left px-5 py-2 text-[9px] font-bold uppercase tracking-widest transition-all flex items-center gap-3 group ${
                          activeSector === child.id ? 'text-primary' : 'text-zinc-600 hover:text-zinc-400'
                        }`}
                      >
                         <div className={`w-1 h-1 rounded-full ${activeSector === child.id ? 'bg-primary shadow-[0_0_8px_#34D399]' : 'bg-zinc-800 group-hover:bg-zinc-700'}`} />
                         {child.label}
                      </button>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ))}
        </div>
      </section>

      {/* Geography Filters */}
      <section>
         <h3 className="text-[10px] font-black text-zinc-600 tracking-[0.2em] uppercase mb-4 px-1">Global Theater</h3>
         <div className="space-y-1">
            {REGIONS.map(reg => (
               <button
                  key={reg.id}
                  onClick={() => onFilterChange(reg.id, activeSector)}
                  className={`w-full text-left px-3 py-2 rounded-xl text-[10px] font-black tracking-widest transition-all flex items-center justify-between group ${
                     activeRegion === reg.id ? 'bg-primary/10 text-primary border border-primary/20' : 'text-zinc-500 hover:bg-white/5 hover:text-white'
                  }`}
               >
                  <div className="flex items-center gap-3">
                     <Globe size={13} className={activeRegion === reg.id ? 'text-primary' : 'text-zinc-700 group-hover:text-primary'} />
                     <span className="uppercase">{reg.label}</span>
                  </div>
                  {activeRegion === reg.id && <div className="w-1 h-1 rounded-full bg-primary" />}
               </button>
            ))}
         </div>
      </section>

      {/* Tracked Projects (Taiyo-style List) */}
      <section className="flex-1 min-h-0 flex flex-col pt-8 border-t border-zinc-900">
        <div className="flex items-center justify-between mb-4 px-1">
           <h3 className="text-[10px] font-black text-zinc-500 tracking-[0.2em] uppercase flex items-center gap-2">
              <Star size={12} className="text-amber-500" /> Tracked Scenarios
           </h3>
           <span className="text-[9px] font-black text-zinc-800 bg-white/5 px-2 py-0.5 rounded-full">{scenarios.length}</span>
        </div>
        
        <div className="space-y-2 overflow-y-auto custom-scrollbar flex-1 pr-1">
           {scenarios.map((s, idx) => (
             <motion.button
               key={s.id}
               initial={{ opacity: 0, x: -10 }}
               animate={{ opacity: 1, x: 0 }}
               transition={{ delay: idx * 0.05 }}
               onClick={() => onSelectScenario(s.topic)}
               className="w-full text-left p-3 rounded-xl border border-zinc-900 bg-white/[0.01] hover:bg-white/[0.04] hover:border-primary/20 transition-all group relative overflow-hidden"
             >
                <div className="flex items-center justify-between mb-1">
                    <span className={`text-[7px] font-black px-1.5 py-0.5 rounded tracking-widest uppercase ${
                      s.status === 'CRITICAL' ? 'bg-rose-500/10 text-rose-500 border border-rose-500/20' : 
                      s.status === 'ACTIVE' ? 'bg-amber-500/10 text-amber-500 border border-amber-500/20' : 'bg-zinc-800 text-zinc-500'
                    }`}>
                      {s.status}
                    </span>
                    <span className="text-[8px] font-mono text-zinc-700">ORD-0{s.id}</span>
                </div>
                <div className="text-[11px] font-black text-zinc-400 group-hover:text-white transition-colors truncate uppercase italic">
                  {s.topic}
                </div>
             </motion.button>
           ))}

           {scenarios.length === 0 && (
              <div className="text-center py-8 px-4 border border-dashed border-zinc-800 rounded-2xl opacity-40">
                 <Inbox size={24} className="text-zinc-800 mx-auto mb-2" />
                 <p className="text-[9px] font-bold text-zinc-600 uppercase tracking-widest leading-relaxed text-center">No active monitoring in this orbit.</p>
              </div>
           )}
        </div>
      </section>

    </div>
  );
}
