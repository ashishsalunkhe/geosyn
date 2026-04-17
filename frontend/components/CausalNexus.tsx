"use client";

/**
 * CausalNexus — Custom SVG force-directed graph.
 *
 * Replaces react-force-graph-2d/3d entirely to eliminate a persistent runtime
 * crash caused by those libraries internally passing undefined/null color values
 * to polished's parseToRgb(). This pure-JS/SVG implementation has zero
 * dependency on polished or THREE.js.
 */

import React, { useCallback, useEffect, useRef, useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Network, ZoomIn, ZoomOut, RefreshCw, Minimize2, Target } from "lucide-react";

/* ─────────────────────────── Types ─────────────────────────── */

interface GraphNode {
  id: number;
  name: string;
  type: "event" | "asset" | "entity" | "shock";
  importance: number;
  val: number;
  meta?: {
    shock_type?: string;
    shock_timestamp?: string;
    shock_content?: string;
  };
}

interface GraphLink {
  source: number;
  target: number;
  type: string;
  weight: number;
  color: string;
}

interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

interface CausalNexusProps {
  graphData: GraphData;
  onSync?: () => void;
  isSyncing?: boolean;
  onNodeClick?: (name: string) => void;
  theme?: "dark" | "light";
}

/* ─────────────────────────── Constants ─────────────────────── */

const NODE_COLORS: Record<string, string> = {
  event:  "var(--primary)",   // Signal Teal – Geopolitical Events
  asset:  "var(--hazard)",    // Signal Yellow – Market Assets
  entity: "var(--info)",      // Sky Blue – Actors / Entities
  shock:  "var(--error)",     // Hazard Amber – Systemic Shock
};

const NODE_LABELS: Record<string, string> = {
  event:  "Event",
  asset:  "Asset",
  entity: "Institutional Macro",
  shock:  "Systemic Shock",
};

const NODE_TOOLTIPS: Record<string, string> = {
  event:  "A geopolitical event driving causal change (conflict, election, treaty)",
  asset:  "A market asset impacted by geopolitical signals (equity, commodity, currency)",
  entity: "Global macro indicators from institutional sources like FRED, IMF, and World Bank",
  shock:  "A sudden, high-impact rupture event that reshapes the geopolitical or financial landscape (coup, pandemic trigger, sanctions cascade, market crash)",
};
const FALLBACK_NODE_COLOR = "var(--text-muted)";
const FALLBACK_LINK_COLOR = "var(--border)";

/* ─────────────────────────── Simulation types ───────────────── */

interface SimNode extends GraphNode {
  x: number;
  y: number;
  vx: number;
  vy: number;
}

interface SimLink {
  source: SimNode;
  target: SimNode;
  original: GraphLink;
}

/* ─────────────────────────── Force simulation ───────────────── */

/**
 * Runs a pure-JS spring/repulsion force layout and returns stable node
 * positions. No external physics library needed — and critically, no polished.
 */
function computeLayout(
  rawNodes: GraphNode[],
  rawLinks: GraphLink[],
  w: number,
  h: number,
): { nodes: SimNode[]; links: SimLink[] } {
  if (rawNodes.length === 0) return { nodes: [], links: [] };

  // Spread initial positions around a circle to avoid degenerate starts
  const TWO_PI = 2 * Math.PI;
  const r0     = Math.min(w, h) * 0.3;
  const cx     = w / 2;
  const cy     = h / 2;

  const nodes: SimNode[] = rawNodes.map((n, i) => {
    // Better initial distribution to avoid overlaps at [0,0]
    const angle = (i / rawNodes.length) * TWO_PI;
    const jitter = (Math.random() - 0.5) * 50;
    return {
      ...n,
      x:  cx + (r0 + jitter) * Math.cos(angle) + (Math.random() - 0.5) * 30,
      y:  cy + (r0 + jitter) * Math.sin(angle) + (Math.random() - 0.5) * 30,
      vx: (Math.random() - 0.5) * 2,
      vy: (Math.random() - 0.5) * 2,
    };
  });

  const byId = new Map<number, SimNode>(nodes.map(n => [n.id, n]));

  const links: SimLink[] = rawLinks
    .filter(l => byId.has(l.source) && byId.has(l.target))
    .map(l => ({
      source:   byId.get(l.source)!,
      target:   byId.get(l.target)!,
      original: l,
    }));

  // Iterative integration (Euler method with cooling schedule)
  const ITERATIONS   = 600; // Increased for better stability
  const REPULSION    = 8000;
  const SPRING_LEN   = 100;
  const SPRING_K     = 0.15;
  const GRAVITY      = 0.015;
  const DAMPING      = 0.8;
  const EPSILON      = 0.001; // Safety for divide by zero

  for (let it = 0; it < ITERATIONS; it++) {
    const alpha = Math.exp(-it * 0.014); // exponential cooling

    // Node–node repulsion
    for (let i = 0; i < nodes.length; i++) {
        const ni = nodes[i];
      for (let j = i + 1; j < nodes.length; j++) {
        const nj = nodes[j];
        const dx = (nj.x - ni.x) || 0.01;
        const dy = (nj.y - ni.y) || 0.01;
        const d  = Math.sqrt(dx * dx + dy * dy);
        if (d < 1) continue;
        const f  = (REPULSION / (d * d)) * alpha;
        ni.vx -= (dx / d) * f;
        ni.vy -= (dy / d) * f;
        nj.vx += (dx / d) * f;
        nj.vy += (dy / d) * f;
      }
    }

    // Spring attraction along edges — Stronger attraction for heavier weights
    for (const lk of links) {
      const dx = lk.target.x - lk.source.x;
      const dy = lk.target.y - lk.source.y;
      const d  = Math.sqrt(dx * dx + dy * dy) || 1;
      
      // Dynamic spring strength based on causal weight
      const weightBonus = 1.0 + Math.abs(lk.original.weight || 0) * 2;
      const f  = (d - SPRING_LEN) * (SPRING_K * weightBonus) * alpha;
      
      lk.source.vx += (dx / d) * f;
      lk.source.vy += (dy / d) * f;
      lk.target.vx -= (dx / d) * f;
      lk.target.vy -= (dy / d) * f;
    }

    // Soft Directed Gravity: Subtle nudge to keep types organized but allowing clusters to form
    for (const n of nodes) {
      const targetX = n.type === "event" ? cx - (w * 0.15) : (n.type === "asset" ? cx + (w * 0.15) : cx);
      n.vx += (targetX - n.x) * (GRAVITY * 0.5) * alpha;
      n.vy += (cy - n.y) * (GRAVITY * 0.5) * alpha;
    }

    // Velocity integration + damping + clamping
    for (const n of nodes) {
      // Guard against NaN
      if (isNaN(n.vx)) n.vx = 0;
      if (isNaN(n.vy)) n.vy = 0;

      n.vx *= DAMPING;
      n.vy *= DAMPING;
      n.x  += n.vx;
      n.y  += n.vy;

      // Coordinate clamping to visible viewbox
      n.x = Math.max(0, Math.min(w, n.x));
      n.y = Math.max(0, Math.min(h, n.y));
    }
  }

  return { nodes, links };
}

/* ─────────────────────────── Helpers ───────────────────────── */

const nodeRadius = (n: SimNode) => Math.max(6, (n.importance || 1) * 7);

const safeNodeColor = (type: string) =>
  NODE_COLORS[type] ?? FALLBACK_NODE_COLOR;

const safeLinkColor = (l: SimLink) => {
  const c = l.original?.color;
  return typeof c === "string" && (c.startsWith("#") || c.startsWith("rgb"))
    ? c
    : FALLBACK_LINK_COLOR;
};

const safeLinkWidth = (l: SimLink) =>
  Math.max(1, Math.abs(l.original?.weight ?? 0) * 3);

/** Compute the endpoint on the target's circle perimeter for cleaner arrows */
const arrowTip = (sx: number, sy: number, tx: number, ty: number, tRadius: number) => {
  const dx = tx - sx;
  const dy = ty - sy;
  const d  = Math.sqrt(dx * dx + dy * dy) || 1;
  const r  = tRadius + 5; // 5px gap before arrowhead
  return { x: tx - (dx / d) * r, y: ty - (dy / d) * r };
};

/* ─────────────────────────── Component ─────────────────────── */

const CausalNexus: React.FC<CausalNexusProps> = ({ graphData, onSync, isSyncing, onNodeClick, theme = "dark" }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [size, setSize]           = useState({ w: 800, h: 520 });
  const [selectedNode, setSelectedNode] = useState<SimNode | null>(null);
  const [zoom, setZoom]           = useState(1);
  const [pan, setPan]             = useState({ x: 0, y: 0 });
  const [isGuideOpen, setIsGuideOpen] = useState(false);
  const [isPanning, setIsPanning] = useState(false);
  const lastMouse                 = useRef({ x: 0, y: 0 });

  const isEmpty = !graphData || graphData.nodes.length === 0;

  /* Measure container so the simulation fills the actual canvas */
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const ro = new ResizeObserver(entries => {
      const { width, height } = entries[0].contentRect;
      setSize({ w: width || 800, h: Math.max(380, height) });
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  /* Re-compute layout whenever data or size changes */
  const { nodes, links } = useMemo(
    () => computeLayout(
      graphData?.nodes ?? [],
      graphData?.links ?? [],
      size.w, size.h
    ),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [graphData?.nodes, graphData?.links, size.w, size.h]
  );

  /* Reset selection when data changes */
  useEffect(() => { setSelectedNode(null); }, [graphData]);

  /* ── Pan / zoom handlers ── */
  const onWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    setZoom(z => Math.max(0.25, Math.min(5, z - e.deltaY * 0.001)));
  }, []);

  const onMouseDown = useCallback((e: React.MouseEvent) => {
    if (e.button !== 0) return;
    setIsPanning(true);
    lastMouse.current = { x: e.clientX, y: e.clientY };
  }, []);

  const onMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isPanning) return;
    setPan(p => ({
      x: p.x + (e.clientX - lastMouse.current.x),
      y: p.y + (e.clientY - lastMouse.current.y),
    }));
    lastMouse.current = { x: e.clientX, y: e.clientY };
  }, [isPanning]);

  const onMouseUp   = useCallback(() => { setIsPanning(false); }, []);
  const onZoomFit   = () => { setZoom(1); setPan({ x: 0, y: 0 }); };
  const onZoomIn    = () => setZoom(z => Math.min(5, z + 0.2));
  const onZoomOut   = () => setZoom(z => Math.max(0.25, z - 0.2));

  /* ── Node click ── */
  const [activeNeighbors, setActiveNeighbors] = useState<Set<number>>(new Set());

  const handleNodeClick = useCallback((e: React.MouseEvent, node: SimNode) => {
    e.stopPropagation();
    if (selectedNode?.id === node.id) {
        setSelectedNode(null);
        setActiveNeighbors(new Set());
    } else {
        setSelectedNode(node);
        // Find 1st degree neighbors
        const neighbors = new Set<number>([node.id]);
        links.forEach(l => {
            if (l.source.id === node.id) neighbors.add(l.target.id);
            if (l.target.id === node.id) neighbors.add(l.source.id);
        });
        setActiveNeighbors(neighbors);
    }
  }, [selectedNode, links]);

  /* ── Interactive Render Coordinates ── */
  const renderedNodes = useMemo(() => {
     return nodes.map(node => {
        let x = node.x;
        let y = node.y;
        if (selectedNode && selectedNode.id !== node.id && activeNeighbors.has(node.id)) {
            const edge = links.find(l => 
                (l.source.id === selectedNode.id && l.target.id === node.id) ||
                (l.target.id === selectedNode.id && l.source.id === node.id)
            );
            if (edge) {
                const weight = Math.abs(edge.original.weight ?? 0) || 0.1;
                const targetDist = 80 + ((1.0 - weight) * 150); // Strongly correlated nodes cluster tighter
                const dx = node.x - selectedNode.x;
                const dy = node.y - selectedNode.y;
                const dist = Math.sqrt(dx*dx + dy*dy) || 1;
                x = selectedNode.x + (dx / dist) * targetDist;
                y = selectedNode.y + (dy / dist) * targetDist;
            }
        } else if (selectedNode && !activeNeighbors.has(node.id)) {
            // Push non-neighbors away slightly for focus
            const dx = node.x - selectedNode.x;
            const dy = node.y - selectedNode.y;
            const dist = Math.sqrt(dx*dx + dy*dy) || 1;
            if (dist < 300) {
                x = selectedNode.x + (dx / dist) * 250;
                y = selectedNode.y + (dy / dist) * 250;
            }
        }
        return { ...node, renderX: x, renderY: y };
     });
  }, [nodes, selectedNode, activeNeighbors, links]);
  
  const renderedNodesById = useMemo(() => new Map(renderedNodes.map(n => [n.id, n])), [renderedNodes]);

  /* ── Unique markers per link color ── */
  const markerColors = useMemo(() => {
    const seen = new Set<string>();
    links.forEach(l => seen.add(safeLinkColor(l)));
    seen.add(FALLBACK_LINK_COLOR);
    return Array.from(seen);
  }, [links]);

  const markerId = (color: string) =>
    "arrow-" + color.replace(/[^a-zA-Z0-9]/g, "");

  return (
    <div className="flex flex-col h-full">
      {/* ── Header ── */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
            <Network size={16} />
          </div>
          <div>
            <h3 className="text-xs font-black text-foreground uppercase tracking-[0.2em]">Causal Nexus</h3>
            <p className="text-[9px] text-text-muted font-bold uppercase tracking-wider">
              {graphData?.nodes?.length || 0} nodes · {graphData?.links?.length || 0} edges
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1.5">
          <button 
            onClick={() => setIsGuideOpen(!isGuideOpen)} 
            className={`p-2 rounded-lg border transition-all text-[10px] uppercase font-black tracking-widest flex items-center gap-2 ${isGuideOpen ? "bg-primary/20 border-primary/40 text-primary" : "bg-panel-bg border-border text-text-muted hover:text-foreground hover:bg-white/5"}`}
          >
            Guide
          </button>
          <div className="w-px h-4 bg-border mx-1" />
          {/* Zoom controls */}
          <button onClick={onZoomOut} className="p-2 rounded-lg bg-panel-bg border border-border text-text-muted hover:text-foreground transition-all">
            <ZoomOut size={13} />
          </button>
          <button onClick={onZoomIn} className="p-2 rounded-lg bg-panel-bg border border-border text-text-muted hover:text-foreground transition-all">
            <ZoomIn size={13} />
          </button>
          <button onClick={onZoomFit} title="Reset view" className="p-2 rounded-lg bg-panel-bg border border-border text-text-muted hover:text-foreground transition-all">
            <Minimize2 size={13} />
          </button>
          {onSync && (
            <button
              onClick={onSync}
              className={`p-2 rounded-lg bg-panel-bg border border-border text-text-muted hover:text-primary transition-all ${isSyncing ? "animate-spin" : ""}`}
            >
              <RefreshCw size={13} />
            </button>
          )}
        </div>
      </div>

      {/* ── Legend ── */}
      <div className="flex flex-wrap items-center gap-x-4 gap-y-2 mb-4 px-1">
        {Object.entries(NODE_COLORS).map(([type, color]) => (
          <div
            key={type}
            className="flex items-center gap-1.5 group relative cursor-help"
            title={NODE_TOOLTIPS[type]}
          >
            {type === "shock" ? (
              <div className="relative">
                <div className="h-2 w-2 rounded-full animate-pulse" style={{ backgroundColor: color }} />
                <div className="absolute -inset-1 rounded-full opacity-30" style={{ backgroundColor: color, filter: "blur(3px)" }} />
              </div>
            ) : (
              <div className="h-2 w-2 rounded-full" style={{ backgroundColor: color }} />
            )}
            <span className="text-[9px] font-black text-text-muted uppercase tracking-widest">
              {NODE_LABELS[type] || type}
            </span>
          </div>
        ))}
        <div className="flex items-center gap-x-3 ml-auto">
          <div className="flex items-center gap-1.5">
            <div className="h-2 w-5 rounded-full bg-success/60" />
            <span className="text-[9px] font-black text-text-muted uppercase">+Impact</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="h-2 w-5 rounded-full bg-error/60" />
            <span className="text-[9px] font-black text-text-muted uppercase">−Impact</span>
          </div>
        </div>
      </div>

      {/* ── Graph Canvas ── */}
      <div
        ref={containerRef}
        className="flex-1 relative rounded-2xl overflow-hidden border border-border bg-panel-bg"
        style={{ minHeight: 380 }}
      >
        {isEmpty ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center opacity-20 grayscale">
            <Network size={48} className="mb-4 text-text-muted" />
            <p className="text-[9px] font-black text-foreground uppercase tracking-[0.3em] text-center">
              No causal signals yet.<br />Trigger a Full Sync to build the graph.
            </p>
          </div>
        ) : (
          <svg
            width={size.w}
            height={size.h}
            style={{ display: "block", cursor: isPanning ? "grabbing" : "grab" }}
            onWheel={onWheel}
            onMouseDown={onMouseDown}
            onMouseMove={onMouseMove}
            onMouseUp={onMouseUp}
            onMouseLeave={onMouseUp}
            onClick={() => setSelectedNode(null)}
          >
            <defs>
              {/* One glow filter per node type */}
              {Object.entries(NODE_COLORS).map(([type, color]) => (
                <filter key={type} id={`glow-${type}`} x="-80%" y="-80%" width="260%" height="260%">
                  <feGaussianBlur stdDeviation="5" result="blur" in="SourceGraphic" />
                  <feMerge>
                    <feMergeNode in="blur" />
                    <feMergeNode in="SourceGraphic" />
                  </feMerge>
                </filter>
              ))}

              {/* One arrowhead marker per distinct link color */}
              {markerColors.map(color => (
                <marker
                  key={color}
                  id={markerId(color)}
                  markerWidth="7"
                  markerHeight="7"
                  refX="5"
                  refY="3.5"
                  orient="auto"
                >
                  <path d="M 0 0 L 7 3.5 L 0 7 z" fill={color} fillOpacity={0.7} />
                </marker>
              ))}

              {/* Shock pulse animation */}
              <style>{`
                @keyframes shock-pulse {
                  0% { stroke-opacity: 0.8; stroke-width: 2; r: 10; }
                  50% { stroke-opacity: 0.4; stroke-width: 15; r: 30; }
                  100% { stroke-opacity: 0; stroke-width: 25; r: 50; }
                }
              `}</style>
            </defs>

              <g transform={`translate(${pan.x},${pan.y}) scale(${zoom})`}>

              {/* Links */}
              {links.map((link, i) => {
                const sNode = renderedNodesById.get(link.source.id)!;
                const tNode = renderedNodesById.get(link.target.id)!;
                if (!sNode || !tNode) return null;

                const color = safeLinkColor(link);
                const tip   = arrowTip(sNode.renderX, sNode.renderY, tNode.renderX, tNode.renderY, nodeRadius(tNode));
                const isActive = activeNeighbors.size === 0 || (activeNeighbors.has(link.source.id) && activeNeighbors.has(link.target.id));
                const isSelectedFocus = selectedNode && activeNeighbors.has(link.source.id) && activeNeighbors.has(link.target.id);
                // Reduce visual clutter: only show highly relevant text or when clicking
                const showText = isSelectedFocus || (activeNeighbors.size === 0 && Math.abs(link.original.weight ?? 0) > 0.4);

                return (
                  <g key={`edge-${i}`}>
                    <motion.line
                      animate={{ 
                        x1: sNode.renderX, y1: sNode.renderY, 
                        x2: tip.x, y2: tip.y,
                        strokeOpacity: isActive ? (0.35 + Math.abs(link.original.weight ?? 0) * 0.45) : 0.05
                      }}
                      transition={{ type: "spring", damping: 15, stiffness: 100 }}
                      stroke={color}
                      strokeWidth={safeLinkWidth(link)}
                      markerEnd={isActive ? `url(#${markerId(color)})` : undefined}
                    />
                    {showText && (
                      <motion.text
                        animate={{ 
                           x: (sNode.renderX + tNode.renderX) / 2, 
                           y: (sNode.renderY + tNode.renderY) / 2,
                           opacity: isActive ? 1 : 0
                        }}
                        transition={{ type: "spring", damping: 15, stiffness: 100 }}
                        fill={color}
                        fontSize={8}
                        fontWeight={900}
                        textAnchor="middle"
                        dy={-4}
                        className="pointer-events-none select-none drop-shadow-sm filter"
                      >
                         {Math.abs(link.original.weight ?? 0).toFixed(2)}
                      </motion.text>
                    )}
                  </g>
                );
              })}

              {/* Nodes */}
              {renderedNodes.map(node => {
                const r         = nodeRadius(node);
                const color     = safeNodeColor(node.type);
                const isSelected = selectedNode?.id === node.id;
                const isActive   = activeNeighbors.size === 0 || activeNeighbors.has(node.id);

                return (
                  <motion.g
                    key={node.id}
                    animate={{ x: node.renderX, y: node.renderY, opacity: isActive ? 1 : 0.1 }}
                    transition={{ type: "spring", damping: 15, stiffness: 100 }}
                    style={{ cursor: "pointer" }}
                    onClick={(e: any) => handleNodeClick(e, node)}
                  >
                    {/* Ambient glow halo */}
                    <circle r={r + 10} fill={color} fillOpacity={isSelected ? 0.15 : 0.06} />

                    {/* Tactical Shock Pulse */}
                    {node.meta?.shock_type && (
                      <circle
                        r={r}
                        fill="none"
                        stroke="var(--hazard)"
                        strokeWidth={3}
                        className="animate-[shock-pulse_2s_infinite]"
                      />
                    )}

                    {/* Selection ring */}
                    {isSelected && (
                      <circle
                        r={r + 7}
                        fill="none"
                        stroke={color}
                        strokeWidth={1.5}
                        strokeOpacity={0.8}
                        strokeDasharray="4 3"
                        className="animate-[spin_4s_linear_infinite]"
                      />
                    )}

                    {/* Core node */}
                    <circle
                      r={r}
                      fill={color}
                      fillOpacity={isSelected ? 1 : 0.75}
                      filter={`url(#glow-${node.type})`}
                    />

                    {/* Type ring for "event" nodes */}
                    {node.type === "event" && (
                      <circle r={r + 3} fill="none" stroke={color} strokeWidth={1} strokeOpacity={isActive ? 0.35 : 0.1} />
                    )}

                    {/* Node label - only show if active or no selection */}
                    {(isActive || activeNeighbors.size === 0) && (
                      <text
                        textAnchor="middle"
                        dy={r + 14}
                        fontSize={9}
                        fontWeight={isSelected ? 900 : 700}
                        fill="currentColor"
                        className="text-foreground"
                        fillOpacity={isSelected ? 1 : 0.65}
                        style={{
                          fontFamily: "Inter, monospace, sans-serif",
                          pointerEvents: "none",
                          userSelect: "none",
                          letterSpacing: "0.05em",
                        }}
                      >
                        {node.name.length > 20 ? node.name.slice(0, 19) + "…" : node.name}
                      </text>
                    )}
                  </motion.g>
                );
              })}
            </g>
          </svg>
        )}

        {/* ── Nexus Guide Overlay ── */}
        <AnimatePresence>
          {isGuideOpen && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="absolute top-4 right-4 bottom-4 w-72 bg-background/95 backdrop-blur-xl border border-border rounded-2xl p-6 overflow-y-auto z-50 shadow-2xl"
            >
              <div className="flex items-center justify-between mb-6">
                <h4 className="text-xs font-black text-foreground uppercase tracking-widest">The Nexus Guide</h4>
                <button onClick={() => setIsGuideOpen(false)} className="text-text-muted hover:text-foreground transition-colors">✕</button>
              </div>

              <div className="space-y-6">
                <section>
                  <h5 className="text-[10px] font-black text-primary uppercase tracking-widest mb-2 italic">Mathematical Rigor</h5>
                  <p className="text-[10px] text-text-muted leading-relaxed">
                    This graph uses <strong className="text-foreground">Granger Causality</strong> to verify if news signals have predictive power over market prices. 
                    Unlike simple correlation, this requires statistical proof that news events precede market moves.
                  </p>
                </section>

                <section>
                  <h5 className="text-[10px] font-black text-success uppercase tracking-widest mb-2 italic">Node Importance</h5>
                  <p className="text-[10px] text-text-muted leading-relaxed">
                    Node size is determined by <strong className="text-foreground">Degree Centrality</strong>. 
                    A larger node means that entity or event has more causal connections in the current intelligence mesh.
                  </p>
                </section>

                <section>
                  <h5 className="text-[10px] font-black text-info uppercase tracking-widest mb-2 italic">Institutional Macro</h5>
                  <p className="text-[10px] text-text-muted leading-relaxed">
                    Blue nodes represent official data from <strong className="text-foreground">FRED, IMF, and World Bank</strong>.
                    These provide the economic baseline (Inflation, Interest Rates) that anchors our tactical news signals.
                  </p>
                </section>

                <div className="pt-4 border-t border-border">
                   <div className="p-3 bg-violet-500/10 border border-violet-500/20 rounded-xl">
                      <p className="text-[9px] font-bold text-primary uppercase leading-snug">
                        "The goal of the Nexus is to quantify the unquantifiable: turning global chaos into actionable market vectors."
                      </p>
                   </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── Selected Node Info Panel ── */}
        <AnimatePresence>
          {selectedNode && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              className="absolute bottom-4 left-4 right-4 p-4 bg-background/95 backdrop-blur-xl border border-border rounded-2xl"
            >
              <div className="flex items-center justify-between mb-3">
                <span
                  className="text-[9px] font-black uppercase tracking-[0.3em]"
                  style={{ color: safeNodeColor(selectedNode.type) }}
                >
                  {selectedNode.type}
                </span>
                <button
                  onClick={() => setSelectedNode(null)}
                  className="text-text-muted hover:text-foreground text-xs transition-colors"
                >
                  ✕
                </button>
              </div>
              <p className="text-sm font-black text-foreground mb-2 leading-tight">{selectedNode.name}</p>
              <p className="text-[10px] text-text-muted font-bold uppercase tracking-wide mb-4">
                Connected to{" "}
                {(graphData?.links ?? []).filter(
                  l => l.source === selectedNode.id || l.target === selectedNode.id
                ).length}{" "}
                nodes
              </p>

              {selectedNode.meta?.shock_type && (
                <div className="mb-4 p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl">
                  <p className="text-[10px] font-black text-amber-400 uppercase tracking-widest mb-1 flex items-center gap-2">
                    <RefreshCw size={10} className="animate-spin-slow" />
                    Tactical Divergence Detected
                  </p>
                  <p className="text-[10px] text-foreground leading-relaxed italic">
                    {selectedNode.meta.shock_content}
                  </p>
                </div>
              )}
              {onNodeClick && (
                <button 
                  onClick={(e) => { e.stopPropagation(); onNodeClick(selectedNode.name); }}
                  className="w-full flex items-center justify-center gap-2 py-2.5 bg-primary text-black rounded-xl text-[10px] font-black uppercase tracking-widest hover:scale-[1.02] active:scale-[0.98] transition-all shadow-lg shadow-primary/20"
                >
                  <Target size={12} />
                  Analyze Tactical Brief
                </button>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default CausalNexus;
