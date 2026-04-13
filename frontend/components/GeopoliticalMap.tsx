"use client";

import React from "react";
import { ComposableMap, Geographies, Geography, Marker } from "react-simple-maps";

const geoUrl = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json";

interface GeoPoint {
  type: string;
  geometry: {
    type: string;
    coordinates: [number, number];
  };
  properties: {
    name: string;
    intensity: number;
    magnitude: number;
  };
}

interface GeopoliticalMapProps {
  points: GeoPoint[];
}

const GeopoliticalMap: React.FC<GeopoliticalMapProps> = ({ points }) => {
  return (
    <div className="w-full aspect-video bg-zinc-950/50 rounded-2xl border border-zinc-800/50 overflow-hidden relative group">
      <div className="absolute top-4 left-4 z-10">
        <h4 className="text-[10px] font-black text-white uppercase tracking-widest shadow-xl px-2 py-1 bg-black/60 rounded border border-white/10">Tactical Heatmap</h4>
      </div>
      
      <ComposableMap projectionConfig={{ scale: 140 }}>
        <Geographies geography={geoUrl}>
          {({ geographies }) =>
            geographies.map((geo) => (
              <Geography
                key={geo.rsmKey}
                geography={geo}
                fill="#09090b"
                stroke="#18181b"
                strokeWidth={0.5}
                style={{
                  default: { outline: "none" },
                  hover: { fill: "#18181b", outline: "none" },
                  pressed: { outline: "none" },
                }}
              />
            ))
          }
        </Geographies>
        
        {points.map((point, i) => (
          <Marker key={i} coordinates={point.geometry.coordinates}>
            <circle 
              r={2 + (point.properties.magnitude || 2) * 2} 
              fill="#f97316" 
              className="animate-pulse" 
              fillOpacity={0.4} 
            />
            <circle r={2} fill="#ea580c" />
            
            {/* Tooltip Overlay */}
            <title>{point.properties.name}: Intensity {point.properties.intensity}</title>
          </Marker>
        ))}
      </ComposableMap>

      {/* Map Legend */}
      <div className="absolute bottom-4 right-4 flex items-center gap-4 bg-black/80 px-4 py-2 rounded-full border border-zinc-800">
        <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-rose-500 animate-pulse" />
            <span className="text-[8px] font-black text-zinc-400 uppercase tracking-widest">Active Signal</span>
        </div>
      </div>
    </div>
  );
};

export default GeopoliticalMap;
