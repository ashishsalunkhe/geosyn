"use client";

import React from "react";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip
} from "recharts";

interface ThematicRadarProps {
  data: Record<string, number>;
}

const ThematicRadar: React.FC<ThematicRadarProps> = ({ data }) => {
  // Normalize and transform data for recharts
  const chartData = Object.entries(data).map(([key, value]) => ({
    subject: key.toUpperCase(),
    A: value,
    fullMark: Math.max(...Object.values(data), 10)
  }));

  if (chartData.length === 0) return null;

  return (
    <div className="w-full h-[250px] flex items-center justify-center p-2">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={chartData}>
          <PolarGrid stroke="#3f3f46" />
          <PolarAngleAxis 
            dataKey="subject" 
            tick={{ fill: "#71717a", fontSize: 8, fontWeight: "900" }} 
          />
          <Radar
            name="Crisis Dimension"
            dataKey="A"
            stroke="#f97316"
            fill="#f97316"
            fillOpacity={0.3}
          />
          <Tooltip 
            contentStyle={{ backgroundColor: "#09090b", border: "1px solid #27272a", fontSize: "10px" }}
            itemStyle={{ color: "#f97316", fontWeight: "900" }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ThematicRadar;
