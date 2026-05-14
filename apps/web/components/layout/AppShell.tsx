import { headers } from "next/headers";

import { Badge } from "../ui/badge";
import { Sidebar } from "./Sidebar";

export async function AppShell({
  me,
  currentPath,
  children,
}: {
  me: { display_name: string; email: string; role_keys: string[]; permissions?: string[] };
  currentPath: string;
  children: React.ReactNode;
}) {
  void headers;
  return (
    <div className="flex min-h-screen">
      <Sidebar currentPath={currentPath} permissions={me.permissions ?? []} />
      <div className="flex-1">
        <header className="border-b border-slate-800/80 bg-slate-950/60 px-6 py-3">
          <div className="flex items-center justify-between">
            <div className="text-xs text-slate-500">
              <span className="font-mono">tg365</span>{" "}
              <span className="text-slate-700">/</span>{" "}
              <span>{currentPath}</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="hidden flex-col text-right md:flex">
                <span className="text-sm text-slate-100">{me.display_name}</span>
                <span className="text-xs text-slate-500">{me.email}</span>
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
        {children}
      </div>
    </div>
  );
}
