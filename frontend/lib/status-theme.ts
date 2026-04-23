import { AlertTriangle, ShieldAlert, ShieldCheck, TrendingUp, Zap, type LucideIcon } from "lucide-react";

type Tone = {
  text: string;
  soft: string;
  border: string;
  pill: string;
  solid: string;
  icon: LucideIcon;
};

export const STATUS_TONES: Record<string, Tone> = {
  CRITICAL: {
    text: "text-error",
    soft: "bg-error/10",
    border: "border-error/25",
    pill: "bg-error/12 text-error border-error/30",
    solid: "bg-error",
    icon: ShieldAlert,
  },
  ACTIVE: {
    text: "text-primary",
    soft: "bg-primary/10",
    border: "border-primary/25",
    pill: "bg-primary/12 text-primary border-primary/30",
    solid: "bg-primary",
    icon: TrendingUp,
  },
  EMERGING: {
    text: "text-info",
    soft: "bg-info/10",
    border: "border-info/25",
    pill: "bg-info/12 text-info border-info/30",
    solid: "bg-info",
    icon: Zap,
  },
  STABILIZED: {
    text: "text-success",
    soft: "bg-success/10",
    border: "border-success/25",
    pill: "bg-success/12 text-success border-success/30",
    solid: "bg-success",
    icon: ShieldCheck,
  },
  RESOLVING: {
    text: "text-hazard",
    soft: "bg-hazard/10",
    border: "border-hazard/25",
    pill: "bg-hazard/12 text-hazard border-hazard/30",
    solid: "bg-hazard",
    icon: AlertTriangle,
  },
};

export const SEVERITY_TONES: Record<string, Tone> = {
  critical: STATUS_TONES.CRITICAL,
  high: STATUS_TONES.RESOLVING,
  medium: STATUS_TONES.ACTIVE,
  low: STATUS_TONES.STABILIZED,
};

export function getStatusTone(status?: string | null): Tone {
  return STATUS_TONES[(status || "RESOLVING").toUpperCase()] || STATUS_TONES.RESOLVING;
}

export function getSeverityTone(severity?: string | null): Tone {
  return SEVERITY_TONES[(severity || "medium").toLowerCase()] || SEVERITY_TONES.medium;
}
