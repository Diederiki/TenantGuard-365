import { cn } from "../../lib/utils";

type Tone = "ok" | "warn" | "danger" | "info" | "muted";

const COLOR: Record<Tone, string> = {
  ok: "bg-emerald-400",
  warn: "bg-amber-400",
  danger: "bg-rose-400",
  info: "bg-sky-400",
  muted: "bg-slate-500",
};

export function StatusDot({
  tone = "ok",
  pulse = true,
  className,
}: {
  tone?: Tone;
  pulse?: boolean;
  className?: string;
}) {
  return (
    <span className={cn("relative inline-flex h-2.5 w-2.5", className)}>
      <span
        className={cn(
          "absolute inset-0 rounded-full",
          COLOR[tone],
          pulse ? "animate-pulseDot" : "",
        )}
      />
      <span
        className={cn(
          "relative inline-flex h-2.5 w-2.5 rounded-full",
          COLOR[tone],
        )}
      />
    </span>
  );
}
