import * as React from "react";

import { cn } from "../../lib/utils";

type Variant = "glass" | "glass-1" | "glass-2" | "glass-3" | "glass-4" | "glass-5" | "flat";

const VARIANTS: Record<Variant, string> = {
  glass: "bg-slate-900/55 backdrop-blur-xl",
  "glass-1": "bg-glass-1 backdrop-blur-xl",
  "glass-2": "bg-glass-2 backdrop-blur-xl",
  "glass-3": "bg-glass-3 backdrop-blur-xl",
  "glass-4": "bg-glass-4 backdrop-blur-xl",
  "glass-5": "bg-glass-5 backdrop-blur-xl",
  flat: "bg-slate-900/80",
};

export function Card({
  className,
  variant = "glass",
  ...props
}: React.HTMLAttributes<HTMLDivElement> & { variant?: Variant }) {
  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-2xl",
        "ring-1 ring-white/5 border border-slate-800/60",
        "shadow-glass",
        "p-6",
        VARIANTS[variant],
        // subtle inner highlight + bottom-fade
        "before:pointer-events-none before:absolute before:inset-x-0 before:top-0 before:h-px before:bg-gradient-to-r before:from-transparent before:via-white/10 before:to-transparent",
        className,
      )}
      {...props}
    />
  );
}

export function CardHeader({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("mb-4", className)} {...props} />;
}

export function CardTitle({
  className,
  ...props
}: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3
      className={cn("text-lg font-semibold tracking-tight text-slate-100", className)}
      {...props}
    />
  );
}

export function CardDescription({
  className,
  ...props
}: React.HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p
      className={cn("mt-1 text-sm text-slate-400", className)}
      {...props}
    />
  );
}

export function CardContent({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("text-sm text-slate-300", className)} {...props} />;
}
