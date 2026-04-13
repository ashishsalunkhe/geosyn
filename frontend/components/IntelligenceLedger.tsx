"use client";

import React, { useState } from "react";
import { 
  Search, 
  ExternalLink, 
  ArrowUpRight, 
  ArrowDownRight, 
  ShieldCheck, 
  Tag, 
  Database,
  SortAsc,
  SortDesc
} from "lucide-react";

interface MeshRecord {
  id: string;
  source: string;
  title: string;
  url: string;
  sector: string;
  tone: number;
  reliability: number;
  timestamp: string;
}

interface IntelligenceLedgerProps {
  records: MeshRecord[];
}

export default function IntelligenceLedger({ records }: IntelligenceLedgerProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [sortField, setSortField] = useState<keyof MeshRecord>("tone");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  const filteredRecords = records
    .filter(r => 
        r.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
        r.source.toLowerCase().includes(searchTerm.toLowerCase()) ||
        r.sector.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
        const valA = a[sortField];
        const valB = b[sortField];
        if (typeof valA === "number" && typeof valB === "number") {
            return sortOrder === "asc" ? valA - valB : valB - valA;
        }
        return sortOrder === "asc" 
            ? String(valA).localeCompare(String(valB)) 
            : String(valB).localeCompare(String(valA));
    });

  const toggleSort = (field: keyof MeshRecord) => {
      if (sortField === field) {
          setSortOrder(sortOrder === "asc" ? "desc" : "asc");
      } else {
          setSortField(field);
          setSortOrder("desc");
      }
  };

  return (
    <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-500">
      
      {/* Table Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 py-4 px-2 border-b border-zinc-900 bg-black/20 rounded-t-2xl">
        <div className="flex items-center gap-3">
           <div className="p-1.5 bg-zinc-900 rounded-lg text-zinc-500">
              <Database size={14} />
           </div>
           <div>
              <h3 className="text-[10px] font-black tracking-widest text-white uppercase">Intelligence Mesh Ledger</h3>
              <p className="text-[8px] font-bold text-zinc-600 uppercase tracking-tighter">Verified Osint Data Points ({records.length})</p>
           </div>
        </div>

        <div className="relative group">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-700 group-focus-within:text-primary transition-colors" size={12} />
            <input 
               type="text" 
               placeholder="Filter Mesh..."
               value={searchTerm}
               onChange={(e) => setSearchTerm(e.target.value)}
               className="h-8 pl-9 pr-4 bg-zinc-900/50 border border-zinc-800 rounded-lg text-[10px] font-bold text-white outline-none focus:border-primary/40 transition-all w-full md:w-64"
            />
        </div>
      </div>

      <div className="overflow-x-auto rounded-b-2xl border border-zinc-900">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-zinc-900/40 text-zinc-500 text-[8px] font-black uppercase tracking-widest italic border-b border-zinc-800">
              <th className="px-6 py-4 cursor-pointer hover:text-white transition-colors" onClick={() => toggleSort("id")}>
                 <div className="flex items-center gap-2 font-mono">ID {sortField === "id" && (sortOrder === "asc" ? <SortAsc size={10}/> : <SortDesc size={10}/>)}</div>
              </th>
              <th className="px-6 py-4">Status</th>
              <th className="px-6 py-4 cursor-pointer hover:text-white transition-colors" onClick={() => toggleSort("title")}>
                 <div className="flex items-center gap-2">Source / Title {sortField === "title" && (sortOrder === "asc" ? <SortAsc size={10}/> : <SortDesc size={10}/>)}</div>
              </th>
              <th className="px-6 py-4 cursor-pointer hover:text-white transition-colors" onClick={() => toggleSort("sector")}>
                 <div className="flex items-center gap-2">Sector {sortField === "sector" && (sortOrder === "asc" ? <SortAsc size={10}/> : <SortDesc size={10}/>)}</div>
              </th>
              <th className="px-6 py-4 cursor-pointer hover:text-white transition-colors" onClick={() => toggleSort("tone")}>
                 <div className="flex items-center gap-2 text-right justify-end">Intensity {sortField === "tone" && (sortOrder === "asc" ? <SortAsc size={10}/> : <SortDesc size={10}/>)}</div>
              </th>
              <th className="px-6 py-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredRecords.map((r, idx) => (
              <tr 
                key={idx} 
                className="group border-b border-zinc-900/50 hover:bg-white/[0.02] transition-colors"
              >
                <td className="px-6 py-4">
                  <span className="text-[9px] font-mono text-zinc-600 group-hover:text-zinc-400 transition-colors uppercase">{r.id}</span>
                </td>
                <td className="px-6 py-4">
                   <div className="flex items-center gap-2 px-2 py-1 bg-emerald-500/5 border border-emerald-500/10 rounded group-hover:border-emerald-500/30 transition-all w-fit">
                      <ShieldCheck size={10} className="text-emerald-500/60" />
                      <span className="text-[8px] font-black text-emerald-500/80 uppercase tracking-tighter italic">Verified</span>
                   </div>
                </td>
                <td className="px-6 py-4 max-w-md">
                   <div className="flex flex-col gap-0.5">
                      <span className="text-[7px] font-black text-primary/60 uppercase tracking-widest">{r.source}</span>
                      <span className="text-[10px] font-bold text-zinc-300 group-hover:text-white transition-colors truncate">{r.title}</span>
                   </div>
                </td>
                <td className="px-6 py-4">
                   <div className="flex items-center gap-2">
                      <Tag size={10} className="text-zinc-700" />
                      <span className="text-[9px] font-black text-zinc-500 uppercase tracking-widest italic">{r.sector}</span>
                   </div>
                </td>
                <td className="px-6 py-4 text-right">
                   <div className={`flex items-center justify-end gap-1.5 font-mono text-[10px] font-black ${r.tone < 0 ? 'text-rose-500' : 'text-emerald-500'}`}>
                      {r.tone < 0 ? <ArrowDownRight size={12}/> : <ArrowUpRight size={12}/>}
                      {r.tone.toFixed(1)}
                   </div>
                </td>
                <td className="px-6 py-4 text-right">
                   <a 
                     href={r.url} 
                     target="_blank" 
                     rel="noreferrer"
                     className="p-1 px-3 bg-zinc-900 border border-zinc-800 rounded-lg text-zinc-500 hover:text-white hover:border-zinc-600 transition-all text-[9px] font-black uppercase flex items-center gap-2 w-fit ml-auto"
                   >
                     Record <ExternalLink size={10} />
                   </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {filteredRecords.length === 0 && (
          <div className="py-20 text-center">
             <Database size={32} className="text-zinc-800 mx-auto mb-4" />
             <p className="text-[10px] font-black text-zinc-600 uppercase tracking-widest">No matching tactical signals found in the mesh.</p>
          </div>
        )}
      </div>
    </div>
  );
}
