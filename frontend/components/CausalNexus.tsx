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
  type: "event" | "asset" | "entity";
  importance: number;
  val: number;
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
}

/* ─────────────────────────── Constants ─────────────────────── */

const NODE_COLORS: Record<string, string> = {
  event:  "#a78bfa",   // Violet  – Geopolitical Events
  asset:  "#34d399",   // Emerald – Market Assets
  entity: "#60a5fa",   // Blue    – Actors / Entities
};
const FALLBACK_NODE_COLOR = "#a1a1aa";
const FALLBACK_LINK_COLOR = "#3f3f46";

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

  const nodes: SimNode[] = rawNodes.map((n, i) => ({
    ...n,
    x:  cx + r0 * Math.cos((i / rawNodes.length) * TWO_PI) + (Math.random() - 0.5) * 20,
    y:  cy + r0 * Math.sin((i / rawNodes.length) * TWO_PI) + (Math.random() - 0.5) * 20,
    vx: 0,
    vy: 0,
  }));

  const byId = new Map<number, SimNode>(nodes.map(n => [n.id, n]));

  const links: SimLink[] = rawLinks
    .filter(l => byId.has(l.source) && byId.has(l.target))
    .map(l => ({
      source:   byId.get(l.source)!,
      target:   byId.get(l.target)!,
      original: l,
    }));

  // Iterative integration (Euler method with cooling schedule)
  const ITERATIONS   = 400;
  const REPULSION    = 6000;
  const SPRING_LEN   = 90;
  const SPRING_K     = 0.18;
  const GRAVITY      = 0.012;
  const DAMPING      = 0.85;

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

    // Velocity integration + damping
    for (const n of nodes) {
      n.vx *= DAMPING;
      n.vy *= DAMPING;
      n.x  += n.vx;
      n.y  += n.vy;
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
const arrowTip = (src: SimNode, tgt: SimNode) => {
  const dx = tgt.x - src.x;
  const dy = tgt.y - src.y;
  const d  = Math.sqrt(dx * dx + dy * dy) || 1;
  const r  = nodeRadius(tgt) + 5; // 5px gap before arrowhead
  return { x: tgt.x - (dx / d) * r, y: tgt.y - (dy / d) * r };
};

/* ─────────────────────────── Component ─────────────────────── */

const CausalNexus: React.FC<CausalNexusProps> = ({ graphData, onSync, isSyncing, onNodeClick }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [size, setSize]           = useState({ w: 800, h: 520 });
  const [selectedNode, setSelectedNode] = useState<SimNode | null>(null);
  const [zoom, setZoom]           = useState(1);
  const [pan, setPan]             = useState({ x: 0, y: 0 });
  const isPanning                 = useRef(false);
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
    isPanning.current = true;
    lastMouse.current = { x: e.clientX, y: e.clientY };
  }, []);

  const onMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isPanning.current) return;
    setPan(p => ({
      x: p.x + (e.clientX - lastMouse.current.x),
      y: p.y + (e.clientY - lastMouse.current.y),
    }));
    lastMouse.current = { x: e.clientX, y: e.clientY };
  }, []);

  const onMouseUp   = useCallback(() => { isPanning.current = false; }, []);
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
          <div className="h-8 w-8 rounded-lg bg-violet-500/10 border border-violet-500/20 flex items-center justify-center text-violet-400">
            <Network size={16} />
          </div>
          <div>
            <h3 className="text-xs font-black text-white uppercase tracking-[0.2em]">Causal Nexus</h3>
            <p className="text-[9px] text-zinc-600 font-bold uppercase tracking-wider">
              {graphData?.nodes?.length || 0} nodes · {graphData?.links?.length || 0} edges
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Zoom controls */}
          <button onClick={onZoomOut} className="p-2 rounded-lg bg-white/5 border border-white/10 text-zinc-500 hover:text-white transition-all">
            <ZoomOut size={13} />
          </button>
          <button onClick={onZoomIn} className="p-2 rounded-lg bg-white/5 border border-white/10 text-zinc-500 hover:text-white transition-all">
            <ZoomIn size={13} />
          </button>
          <button onClick={onZoomFit} title="Reset view" className="p-2 rounded-lg bg-white/5 border border-white/10 text-zinc-500 hover:text-white transition-all">
            <Minimize2 size={13} />
          </button>
          {onSync && (
            <button
              onClick={onSync}
              className={`p-2 rounded-lg bg-white/5 border border-white/10 text-zinc-500 hover:text-violet-400 transition-all ${isSyncing ? "animate-spin" : ""}`}
            >
              <RefreshCw size={13} />
            </button>
          )}
        </div>
      </div>

      {/* ── Legend ── */}
      <div className="flex items-center gap-4 mb-4 px-1">
        {Object.entries(NODE_COLORS).map(([type, color]) => (
          <div key={type} className="flex items-center gap-1.5">
            <div className="h-2 w-2 rounded-full" style={{ backgroundColor: color }} />
            <span className="text-[9px] font-black text-zinc-600 uppercase tracking-widest">{type}</span>
          </div>
        ))}
        <div className="flex items-center gap-1.5 ml-auto">
          <div className="h-2 w-6 rounded-full bg-emerald-500/60" />
          <span className="text-[9px] font-black text-zinc-600 uppercase">+Impact</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="h-2 w-6 rounded-full bg-rose-500/60" />
          <span className="text-[9px] font-black text-zinc-600 uppercase">−Impact</span>
        </div>
      </div>

      {/* ── Graph Canvas ── */}
      <div
        ref={containerRef}
        className="flex-1 relative rounded-2xl overflow-hidden border border-white/5 bg-black/60"
        style={{ minHeight: 380 }}
      >
        {isEmpty ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center opacity-20 grayscale">
            <Network size={48} className="mb-4" />
            <p className="text-[9px] font-black text-white uppercase tracking-[0.3em] text-center">
              No causal signals yet.<br />Trigger a Full Sync to build the graph.
            </p>
          </div>
        ) : (
          <svg
            width={size.w}
            height={size.h}
            style={{ display: "block", cursor: isPanning.current ? "grabbing" : "grab" }}
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
            </defs>

            {/* Pan / zoom transform group */}
            <g transform={`translate(${pan.x},${pan.y}) scale(${zoom})`}>

              {/* Links */}
              {links.map((link, i) => {
                const color = safeLinkColor(link);
                const tip   = arrowTip(link.source, link.target);
                const isActive = activeNeighbors.size === 0 || (activeNeighbors.has(link.source.id) && activeNeighbors.has(link.target.id));
                
                return (
                  <line
                    key={i}
                    x1={link.source.x}
                    y1={link.source.y}
                    x2={tip.x}
                    y2={tip.y}
                    stroke={color}
                    strokeWidth={safeLinkWidth(link)}
                    strokeOpacity={isActive ? (0.35 + Math.abs(link.original.weight ?? 0) * 0.45) : 0.05}
                    markerEnd={isActive ? `url(#${markerId(color)})` : undefined}
                    className="transition-all duration-300"
                  />
                );
              })}

              {/* Nodes */}
              {nodes.map(node => {
                const r         = nodeRadius(node);
                const color     = safeNodeColor(node.type);
                const isSelected = selectedNode?.id === node.id;
                const isActive   = activeNeighbors.size === 0 || activeNeighbors.has(node.id);

                return (
                  <g
                    key={node.id}
                    transform={`translate(${node.x},${node.y})`}
                    style={{ cursor: "pointer" }}
                    onClick={e => handleNodeClick(e, node)}
                    className="transition-all duration-300"
                    opacity={isActive ? 1 : 0.1}
                  >
                    {/* Ambient glow halo */}
                    <circle r={r + 10} fill={color} fillOpacity={isSelected ? 0.15 : 0.06} />

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
                        fill="#ffffff"
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
                  </g>
                );
              })}
            </g>
          </svg>
        )}

        {/* ── Selected Node Info Panel ── */}
        <AnimatePresence>
          {selectedNode && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              className="absolute bottom-4 left-4 right-4 p-4 bg-zinc-950/95 backdrop-blur-xl border border-white/10 rounded-2xl"
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
                  className="text-zinc-600 hover:text-white text-xs transition-colors"
                >
                  ✕
                </button>
              </div>
              <p className="text-sm font-black text-white mb-2 leading-tight">{selectedNode.name}</p>
              <p className="text-[10px] text-zinc-500 font-bold uppercase tracking-wide mb-4">
                Impact Weight: {((selectedNode.importance || 0) * 100).toFixed(0)}%
                {" · "}
                Connected to{" "}
                {(graphData?.links ?? []).filter(
                  l => l.source === selectedNode.id || l.target === selectedNode.id
                ).length}{" "}
                nodes
              </p>
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
