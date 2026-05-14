import * as React from "react";

import { cn } from "../../lib/utils";

export type BadgeVariant =
  | "default"
  | "info"
  | "attention"
  | "trouble"
  | "critical"
  | "muted";

type Variant = BadgeVariant;

const styles: Record<Variant, string> = {
  default: "bg-slate-800 text-slate-200 border-slate-700",
  info: "bg-sky-900/40 text-sky-200 border-sky-700",
  attention: "bg-amber-900/40 text-amber-200 border-amber-700",
  trouble: "bg-orange-900/40 text-orange-200 border-orange-700",
  critical: "bg-rose-900/40 text-rose-200 border-rose-700",
  muted: "bg-slate-900 text-slate-500 border-slate-800",
};

export function Badge({
  className,
  variant = "default",
  ...props
}: React.HTMLAttributes<HTMLSpanElement> & { variant?: Variant }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5",
        "text-xs font-medium",
        styles[variant],
        className,
      )}
      {...props}
    />
  );
}
