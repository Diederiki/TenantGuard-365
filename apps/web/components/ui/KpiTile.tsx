import * as React from "react";
import { cn } from "../../lib/utils";

type Tone = "info" | "ok" | "warn" | "danger" | "muted";

const TONE: Record<Tone, { icon: string; ring: string; chip: string }> = {
  info: {
    icon: "text-sky-300 bg-sky-500/10 ring-sky-500/30",
    ring: "ring-sky-500/15",
    chip: "bg-sky-500/15 text-sky-200 ring-sky-500/30",
  },
  ok: {
    icon: "text-emerald-300 bg-emerald-500/10 ring-emerald-500/30",
    ring: "ring-emerald-500/15",
    chip: "bg-emerald-500/15 text-emerald-200 ring-emerald-500/30",
  },
  warn: {
    icon: "text-amber-300 bg-amber-500/10 ring-amber-500/30",
    ring: "ring-amber-500/15",
    chip: "bg-amber-500/15 text-amber-200 ring-amber-500/30",
  },
  danger: {
    icon: "text-rose-300 bg-rose-500/10 ring-rose-500/30",
    ring: "ring-rose-500/15",
    chip: "bg-rose-500/15 text-rose-200 ring-rose-500/30",
  },
  muted: {
    icon: "text-slate-300 bg-slate-500/10 ring-slate-500/20",
    ring: "ring-slate-500/10",
    chip: "bg-slate-500/15 text-slate-300 ring-slate-500/30",
  },
};

export function KpiTile({
  label,
  value,
  delta,
  icon: Icon,
  tone = "info",
  href,
  className,
}: {
  label: string;
  value: React.ReactNode;
  delta?: string;
  icon?: React.ComponentType<{ className?: string }>;
  tone?: Tone;
  href?: string;
  className?: string;
}) {
  const t = TONE[tone];
  const Wrap = href ? "a" : "div";
  return (
    <Wrap
      {...(href ? { href } : {})}
      className={cn(
        "group relative block overflow-hidden rounded-2xl p-4",
        "border border-slate-800/60 ring-1",
        "bg-slate-900/55 backdrop-blur-xl",
        "shadow-glass transition-all",
        "hover:-translate-y-0.5 hover:shadow-glow-brand",
        t.ring,
        className,
      )}
    >
      <div
        className="pointer-events-none absolute inset-x-0 top-0 h-px
          bg-gradient-to-r from-transparent via-white/10 to-transparent"
      />
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs uppercase tracking-widest text-slate-400">{label}</p>
          <p className="mt-1 text-2xl font-semibold tracking-tight text-slate-50">
            {value}
          </p>
          {delta ? (
            <span
              className={cn(
                "mt-2 inline-flex items-center rounded-full px-2 py-0.5 text-xs ring-1",
                t.chip,
              )}
            >
              {delta}
            </span>
          ) : null}
        </div>
        {Icon ? (
          <div
            className={cn(
              "flex h-9 w-9 shrink-0 items-center justify-center rounded-xl ring-1",
              t.icon,
            )}
          >
            <Icon className="h-4 w-4" />
          </div>
        ) : null}
      </div>
    </Wrap>
  );
}
