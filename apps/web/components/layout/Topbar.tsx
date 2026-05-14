import { Bell, ChevronRight, Search } from "lucide-react";
import { Badge } from "../ui/badge";
import { StatusDot } from "../ui/StatusDot";

function Crumbs({ path }: { path: string }) {
  if (path === "/") return <span className="text-slate-300">Dashboard</span>;
  const parts = path.split("/").filter(Boolean);
  return (
    <span className="flex items-center gap-1 text-slate-400">
      {parts.map((p, i) => (
        <span key={i} className="flex items-center gap-1">
          {i > 0 ? <ChevronRight className="h-3.5 w-3.5 text-slate-700" /> : null}
          <span className={i === parts.length - 1 ? "text-slate-200" : ""}>{p}</span>
        </span>
      ))}
    </span>
  );
}

export function Topbar({
  me,
  currentPath,
}: {
  me: { display_name: string; email: string; role_keys: string[] };
  currentPath: string;
}) {
  return (
    <header className="sticky top-0 z-20 border-b border-slate-800/60 bg-ink-950/70 backdrop-blur-xl">
      <div className="flex items-center gap-3 px-6 py-3">
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <StatusDot tone="ok" />
          <span className="font-mono">tg365</span>
          <ChevronRight className="h-3.5 w-3.5 text-slate-700" />
          <Crumbs path={currentPath} />
        </div>

        <div className="ml-4 flex flex-1 items-center">
          <label className="relative w-full max-w-md">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-500" />
            <input
              type="search"
              placeholder="Search reports, users, sites, alerts…"
              className="w-full rounded-xl border border-slate-800/60 bg-slate-900/60 py-2 pl-9 pr-3 text-sm text-slate-100 ring-1 ring-white/5 placeholder:text-slate-500 focus:border-brand-500 focus:outline-none"
            />
            <span className="absolute right-3 top-1/2 -translate-y-1/2 rounded border border-slate-800 px-1.5 text-[10px] font-mono text-slate-500">
              ⌘K
            </span>
          </label>
        </div>

        <button
          type="button"
          className="relative grid h-9 w-9 place-items-center rounded-xl border border-slate-800/60 bg-slate-900/60 text-slate-400 ring-1 ring-white/5 hover:text-slate-100"
        >
          <Bell className="h-4 w-4" />
          <span className="absolute -right-0.5 -top-0.5 grid h-4 w-4 place-items-center rounded-full bg-rose-500 text-[10px] font-semibold text-white">
            2
          </span>
        </button>

        <div className="ml-1 flex items-center gap-3 rounded-xl border border-slate-800/60 bg-slate-900/60 px-3 py-1.5 ring-1 ring-white/5">
          <div className="hidden text-right text-xs leading-tight md:block">
            <div className="text-slate-100">{me.display_name}</div>
            <div className="text-slate-500">{me.email}</div>
          </div>
          <div className="flex gap-1">
            {me.role_keys.slice(0, 2).map((r) => (
              <Badge key={r} variant="info">
                {r}
              </Badge>
            ))}
          </div>
        </div>
      </div>
    </header>
  );
}
