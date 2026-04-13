"use client";
import React from 'react';

interface ClaimBadgeProps {
  verdict: "supported" | "contradicted" | "mixed" | "unverified";
}

const ClaimBadge: React.FC<ClaimBadgeProps> = ({ verdict }) => {
  const getBadgeConfig = () => {
    switch (verdict) {
      case "supported":
        return { label: "Supported", color: "#10b981", bg: "rgba(16, 185, 129, 0.15)" };
      case "contradicted":
        return { label: "Contradicted", color: "#ef4444", bg: "rgba(239, 68, 68, 0.15)" };
      case "mixed":
        return { label: "Mixed Evidence", color: "#f59e0b", bg: "rgba(245, 158, 11, 0.15)" };
      default:
        return { label: "Unverified", color: "#94a3b8", bg: "rgba(148, 163, 184, 0.15)" };
    }
  };

  const { label, color, bg } = getBadgeConfig();

  return (
    <span className="claim-badge">
      {label}
      <style jsx>{`
        .claim-badge {
          display: inline-flex;
          align-items: center;
          padding: 0.2rem 0.6rem;
          border-radius: 99px;
          font-size: 0.65rem;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          color: ${color};
          background: ${bg};
          border: 1px solid ${color}33;
        }
      `}</style>
    </span>
  );
};

export default ClaimBadge;
