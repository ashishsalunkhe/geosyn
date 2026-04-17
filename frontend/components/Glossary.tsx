"use client";

import React from "react";
import { motion } from "framer-motion";
import { 
  Activity,
  Book,
  Cpu,
  Eye,
  ActivitySquare
} from "lucide-react";

export default function Glossary() {
  const categories = [
    {
      title: "Quantitative Vectors",
      icon: <Activity className="text-primary" size={18} />,
      terms: [
        {
          name: "Nexus Depth (D)",
          definition: "A leading indicator representing the causal connectivity of a topic within the Knowledge Graph. Higher depth indicates complex systemic linkages.",
          formula: "Σ(Edges connected to specific Node) / Norm_Factor"
        },
        {
          name: "Attention Quotient (A)",
          definition: "A real-time measure of global visibility across news cycles and social volume. High attention often follows Market Pricing.",
          formula: "Volume(Archive_Search) / Sliding_Window_Avg"
        },
        {
          name: "Alpha Gap (Δ)",
          definition: "The divergence between Nexus Depth and Attention. A high positive gap indicates a 'Blind Spot' or market inefficiency.",
          formula: "Nexus Depth - Attention Quotient"
        },
        {
          name: "Trigger Probability (T)",
          definition: "The statistical likelihood of a geopolitical event catalyzing into a significant market movement within a T+5 window.",
          formula: "Historical_Bayesian_Success_Rate * Sentiment_Delta"
        }
      ]
    },
    {
      title: "Engine Architecture",
      icon: <Cpu className="text-primary" size={18} />,
      terms: [
        {
          name: "Causal Nexus",
          definition: "The core 2D/3D force-directed knowledge graph that maps relationships between geopolitical entities and financial assets.",
          formula: null
        },
        {
          name: "GeoSyn Index (GSI)",
          definition: "A composite tactical score (0.0 - 10.0) that aggregates risk across all active vectors.",
          formula: "0.45D + 0.25A + 0.20P + 0.10T"
        },
        {
          name: "Intelligence Gap",
          definition: "A state where system-identified risk (Nexus) vastly exceeds market awareness (Attention).",
          formula: null
        }
      ]
    },
    {
      title: "Monitoring HUDs",
      icon: <Eye className="text-primary" size={18} />,
      terms: [
        {
          name: "Fragility Gauge (GFI)",
          definition: "Geopolitical Fragility Index. Measures the structural instability of a specific geographic cluster.",
          formula: null
        },
        {
          name: "Scenario HUD",
          definition: "User-defined monitoring environment for tracking specific geopolitical 'narratives' over time.",
          formula: null
        }
      ]
    }
  ];

  return (
    <div className="space-y-12 pb-20 max-w-7xl mx-auto px-4">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div>
          <h2 className="text-2xl font-black text-foreground uppercase tracking-tighter flex items-center gap-3">
            <Book className="text-primary" size={28} />
            Strategic Glossary
          </h2>
          <p className="text-xs text-text-muted mt-2 font-medium tracking-wide uppercase opacity-70">
            Internal technical definitions for the GeoSyn Tactical Engine
          </p>
        </div>
        <div className="flex gap-4">
          <div className="px-4 py-2 rounded-xl bg-primary/10 border border-primary/20">
             <span className="text-[10px] font-black text-primary uppercase">Version 1.0.4-TACTICAL</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-12">
        {categories.map((category, idx) => (
          <div key={idx} className="space-y-6">
            <div className="flex items-center gap-3 border-b border-border pb-4">
              {category.icon}
              <h3 className="text-xs font-black text-foreground uppercase tracking-[0.2em]">{category.title}</h3>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {category.terms.map((term, tIdx) => (
                <motion.div 
                  key={tIdx}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: tIdx * 0.05 + idx * 0.1 }}
                  className="glass-panel p-6 hover:border-primary/30 transition-all cursor-default"
                >
                  <h4 className="text-sm font-black text-foreground uppercase tracking-tight mb-3">
                    {term.name}
                  </h4>
                  <p className="text-[11px] text-text-muted leading-relaxed mb-4 font-medium">
                    {term.definition}
                  </p>
                  {term.formula && (
                    <div className="mt-4 p-3 rounded-lg bg-foreground/5 border border-border">
                      <span className="text-[8px] font-black text-primary uppercase block mb-1">Calculation Logic</span>
                      <code className="text-[9px] font-mono text-foreground/80 break-all">{term.formula}</code>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="p-8 rounded-3xl bg-primary/5 border border-primary/10 text-center">
         <ActivitySquare className="mx-auto mb-4 text-primary opacity-40" size={32} />
         <h4 className="text-xs font-black text-foreground uppercase tracking-widest mb-2">Dynamic Engine Update</h4>
         <p className="text-[10px] text-text-muted max-w-md mx-auto leading-relaxed">
            Definitions are dynamically indexed against the latest backend heuristic model. Manual adjustments require root-level tactical clearance.
         </p>
      </div>
    </div>
  );
}
