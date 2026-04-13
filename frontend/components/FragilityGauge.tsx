"use client";

import React from "react";
import { motion } from "framer-motion";

interface FragilityGaugeProps {
  label: string;
  value: number; // 0-100
  color: string;
  subtext: string;
}

export default function FragilityGauge({ label, value, color, subtext }: FragilityGaugeProps) {
  return (
    <div className="flex flex-col gap-2 flex-1">
      <div className="flex items-center justify-between px-1">
        <span className="text-[9px] font-black text-zinc-500 uppercase tracking-widest italic">{label}</span>
        <span className={`text-[10px] font-mono font-black ${color}`}>{value.toFixed(1)}</span>
      </div>
      
      <div className="h-1.5 bg-white/5 rounded-full overflow-hidden relative">
        <motion.div 
           initial={{ width: 0 }}
           animate={{ width: `${value}%` }}
           transition={{ duration: 1, ease: "easeOut" }}
           className={`h-full ${color.replace('text-', 'bg-')} shadow-[0_0_10px_rgba(var(--tw-shadow-color),0.5)]`}
        />
      </div>

      <p className="text-[7px] font-bold text-zinc-600 uppercase tracking-tighter italic">
        {subtext}
      </p>
    </div>
  );
}
