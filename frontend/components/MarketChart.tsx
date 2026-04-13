"use client";

import React, { useMemo } from "react";
import { motion } from "framer-motion";
import { Activity, TrendingUp, TrendingDown } from "lucide-react";

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
      <div className="flex flex-col items-center justify-center h-[300px] glass-panel bg-white/5 border-dashed">
         <Activity size={32} className="text-zinc-700 mb-4 animate-pulse" />
         <p className="text-xs font-black tracking-widest text-zinc-600 uppercase">Awaiting Tactical Stream...</p>
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

  const shockPoints = data.shocks.map(s => {
    const shockTime = new Date(s.timestamp).getTime();
    let closestIdx = 0;
    let minDiff = Infinity;
    points.forEach((p, i) => {
      const diff = Math.abs(new Date(p.t).getTime() - shockTime);
      if (diff < minDiff) {
        minDiff = diff;
        closestIdx = i;
      }
    });
    return { ...s, ...chartPoints[closestIdx] };
  });

  const lastPrice = points[points.length - 1].v;
  const prevPrice = points[0].v;
  const isUp = lastPrice >= prevPrice;

  return (
    <div className="w-full">
      <div className="flex justify-between items-end mb-8">
        <div className="flex items-center gap-4">
          <div className={`p-3 rounded-2xl ${isUp ? 'bg-emerald-500/10 text-emerald-500' : 'bg-rose-500/10 text-rose-500'}`}>
            {isUp ? <TrendingUp size={24} /> : <TrendingDown size={24} />}
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-1.5 py-0.5 rounded bg-rose-500 text-[9px] font-black text-white">LIVE</span>
              <span className="text-[10px] font-black tracking-widest text-zinc-500 uppercase">{data.ticker} / GLOBAL</span>
            </div>
            <h2 className="text-3xl font-black tracking-tight text-white leading-none">
              {lastPrice.toLocaleString('en-IN', { 
                minimumFractionDigits: 2, 
                maximumFractionDigits: 2 
              })}
            </h2>
          </div>
        </div>
        
        <div className="flex flex-col items-end gap-1">
          <span className="text-[10px] font-black tracking-widest text-zinc-500 uppercase">30D PERFORMANCE</span>
          <span className={`text-sm font-black ${isUp ? 'text-emerald-500' : 'text-rose-500'}`}>
            {isUp ? '+' : ''}{((lastPrice - prevPrice) / prevPrice * 100).toFixed(2)}%
          </span>
        </div>
      </div>

      <div className="relative glass-panel bg-black/20 p-6">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto overflow-visible">
          <defs>
            <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--primary)" stopOpacity="0.2" />
              <stop offset="100%" stopColor="var(--primary)" stopOpacity="0" />
            </linearGradient>
            <filter id="glow">
              <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>

          {/* Grid lines */}
          <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} className="stroke-white/5" />
          
          {/* Area */}
          <motion.path 
            d={areaD} 
            fill="url(#chartGradient)"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1 }}
          />

          {/* Line */}
          <motion.path 
            d={pathD} 
            fill="none" 
            className="stroke-primary" 
            strokeWidth="3"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 1.5, ease: "easeInOut" }}
          />

          {/* Shock Markers */}
          {shockPoints.map((s, i) => (
            <g key={i} className="group/shock cursor-help">
              <motion.circle 
                cx={s.x} cy={s.y} r="6" 
                fill={s.intensity > 0.7 ? "#f43f5e" : "#f59e0b"}
                className="drop-shadow-[0_0_8px_rgba(244,63,94,0.5)]"
                initial={{ scale: 0 }}
                animate={{ scale: [0, 1.5, 1] }}
                transition={{ delay: 1 + (i * 0.2), duration: 0.5 }}
              />
              <line x1={s.x} y1={s.y} x2={s.x} y2={height - padding} className="stroke-primary opacity-20" strokeDasharray="4 2" />
            </g>
          ))}
        </svg>

        <div className="flex gap-6 mt-6">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-primary" />
            <span className="text-[10px] font-black text-zinc-500 tracking-widest uppercase italic">Price Velocity</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.8)]" />
            <span className="text-[10px] font-black text-zinc-500 tracking-widest uppercase italic">Intelligence Shock</span>
          </div>
        </div>
      </div>
    </div>
  );
}
