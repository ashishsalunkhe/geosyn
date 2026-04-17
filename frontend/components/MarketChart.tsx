"use client";

import React, { useMemo } from "react";
import { motion } from "framer-motion";
import { Activity, TrendingUp, TrendingDown, Zap } from "lucide-react";

interface MarketChartProps {
  data: {
    ticker: string;
    points: { t: string; v: number }[];
    shocks: { event_id: number; event_title: string; timestamp: string; intensity: number }[];
  } | null;
}

export default function MarketChart({ data }: MarketChartProps) {
  if (!data || !data.points || data.points.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-[300px] glass-panel border-dashed">
         <Activity size={32} className="text-text-muted mb-4 animate-pulse opacity-20" />
         <p className="text-xs font-black tracking-widest text-text-muted uppercase">Loading market data...</p>
      </div>
    );
  }

  const points = data.points;
  const minPrice = Math.min(...points.map(p => p.v));
  const maxPrice = Math.max(...points.map(p => p.v));
  const priceRange = maxPrice - minPrice || 1;

  const width = 800;
  const height = 350;
  const padding = 30;

  // The chart X-axis spans from the first to the last price point timestamp
  const firstTime = new Date(points[0].t).getTime();
  const lastTime  = new Date(points[points.length - 1].t).getTime();
  const timeRange = lastTime - firstTime || 1;

  const chartPoints = useMemo(() => {
    return points.map((p, i) => ({
      x: (i / (points.length - 1)) * (width - padding * 2) + padding,
      y: (height - padding) - ((p.v - minPrice) / priceRange) * (height - padding * 2),
      val: p.v,
      time: p.t
    }));
  }, [points, minPrice, priceRange]);

  const pathD = `M ${chartPoints[0].x} ${chartPoints[0].y} ` +
                chartPoints.slice(1).map(p => `L ${p.x} ${p.y}`).join(" ");

  const areaD = `${pathD} L ${chartPoints[chartPoints.length-1].x} ${height} L ${chartPoints[0].x} ${height} Z`;

  // Map each shock to the closest price point, but only include shocks
  // that actually fall within the chart's time window.
  const shockPoints = (data.shocks || [])
    .filter(s => {
      const st = new Date(s.timestamp).getTime();
      // Allow ±3 days leeway outside window edges
      return st >= firstTime - 3 * 86400_000 && st <= lastTime + 3 * 86400_000;
    })
    .map(s => {
      const shockTime = new Date(s.timestamp).getTime();
      let closestIdx = 0;
      let minDiff = Infinity;
      points.forEach((p, i) => {
        const diff = Math.abs(new Date(p.t).getTime() - shockTime);
        if (diff < minDiff) { minDiff = diff; closestIdx = i; }
      });
      return { ...s, ...chartPoints[closestIdx] };
    });

  const lastPrice = points[points.length - 1].v;
  const prevPrice = points[0].v;
  const isUp = lastPrice >= prevPrice;

  return (
    <div className="w-full">
      <div className="flex justify-between items-end mb-6">
        <div className="flex items-center gap-3">
          <div className={`p-3 rounded-2xl ${isUp ? 'bg-success/10 text-success' : 'bg-error/10 text-error'}`}>
            {isUp ? <TrendingUp size={22} /> : <TrendingDown size={22} />}
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-1.5 py-0.5 rounded bg-error text-[9px] font-black text-white animate-pulse">LIVE</span>
              <span className="text-[10px] font-black tracking-widest text-text-muted uppercase">{data.ticker} / GLOBAL</span>
            </div>
            <h2 className="text-3xl font-black tracking-tight text-foreground leading-none">
              {lastPrice.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </h2>
          </div>
        </div>

        <div className="flex flex-col items-end gap-1">
          <span className="text-[10px] font-black tracking-widest text-text-muted uppercase">30-Day Change</span>
          <span className={`text-sm font-black ${isUp ? 'text-success' : 'text-error'}`}>
            {isUp ? '+' : ''}{((lastPrice - prevPrice) / prevPrice * 100).toFixed(2)}%
          </span>
        </div>
      </div>

      <div className="relative glass-panel p-4 md:p-6">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto overflow-visible">
          <defs>
            <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--primary)" stopOpacity="0.2" />
              <stop offset="100%" stopColor="var(--primary)" stopOpacity="0" />
            </linearGradient>
            <filter id="glow">
              <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
              <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
            <filter id="shockGlow">
              <feGaussianBlur stdDeviation="5" result="blur"/>
              <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
          </defs>

          {/* Baseline grid line */}
          <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} className="stroke-foreground/5" />

          {/* Area fill */}
          <motion.path
            d={areaD}
            fill="url(#chartGradient)"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1 }}
          />

          {/* Price line */}
          <motion.path
            d={pathD}
            fill="none"
            className="stroke-primary"
            strokeWidth="2.5"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 1.5, ease: "easeInOut" }}
          />

          {/* Crisis Spike markers — pinned to the actual price line */}
          {shockPoints.map((s, i) => (
            <g key={i} className="cursor-help">
              {/* Dashed vertical drop line */}
              <line
                x1={s.x} y1={s.y}
                x2={s.x} y2={height - padding}
                stroke={s.intensity > 0.7 ? "var(--error)" : "var(--hazard)"}
                strokeOpacity={0.25}
                strokeDasharray="4 3"
                strokeWidth={1}
              />
              {/* Outer pulse ring */}
              <motion.circle
                cx={s.x} cy={s.y} r={12}
                fill={s.intensity > 0.7 ? "var(--error)" : "var(--hazard)"}
                fillOpacity={0.12}
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: [1, 1.4, 1], opacity: [0.2, 0.05, 0.15] }}
                transition={{ delay: 0.8 + i * 0.15, duration: 1.5, repeat: Infinity, repeatType: "loop" }}
              />
              {/* Core marker dot */}
              <motion.circle
                cx={s.x} cy={s.y} r={6}
                fill={s.intensity > 0.7 ? "var(--error)" : "var(--hazard)"}
                filter="url(#shockGlow)"
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.6 + i * 0.15, duration: 0.4, ease: "backOut" }}
              />
              {/* Tooltip title above the marker */}
              <motion.text
                x={s.x}
                y={s.y - 16}
                textAnchor="middle"
                fontSize={7}
                fontWeight={700}
                fill={s.intensity > 0.7 ? "var(--error)" : "var(--hazard)"}
                fillOpacity={0.8}
                style={{ fontFamily: "Inter, monospace", pointerEvents: "none", userSelect: "none", letterSpacing: "0.06em" }}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1 + i * 0.15 }}
              >
                {s.event_title && s.event_title.length > 22
                  ? s.event_title.slice(0, 21) + "…"
                  : s.event_title || "CRISIS EVENT"}
              </motion.text>
            </g>
          ))}

          {/* "No crisis events in window" ghost message when shocks exist but none are in range */}
          {(data.shocks?.length ?? 0) > 0 && shockPoints.length === 0 && (
            <text
              x={width / 2} y={height - padding - 10}
              textAnchor="middle" fontSize={9} fill="var(--text-muted)"
              style={{ fontFamily: "Inter, monospace", userSelect: "none", letterSpacing: "0.05em" }}
            >
              No crisis events fall within this 30-day window
            </text>
          )}
        </svg>

        {/* Legend */}
        <div className="flex flex-wrap gap-x-5 gap-y-2 mt-4">
          <div className="flex items-center gap-2">
            <span className="w-6 h-0.5 rounded-full bg-primary inline-block" />
            <span className="text-[9px] font-black text-text-muted tracking-widest uppercase">Price</span>
          </div>
          <div className="flex items-center gap-2" title="A dot marks a major world event that may have moved this market. Red = high impact, amber = moderate impact.">
            <span className="relative flex h-2.5 w-2.5 shrink-0">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-error opacity-30" />
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-error" />
            </span>
            <span className="text-[9px] font-black text-text-muted tracking-widest uppercase">
              Crisis Event
              <span className="text-text-muted opacity-40 font-normal normal-case ml-1">(hover for details)</span>
            </span>
          </div>
          {(data.shocks?.length ?? 0) === 0 && (
            <span className="text-[8px] text-text-muted opacity-30 font-bold uppercase tracking-wider self-center">
              — No crisis events detected for this asset yet
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
