import { headers } from "next/headers";
import { redirect } from "next/navigation";

import { AppShell } from "../../components/layout/AppShell";
import { Badge } from "../../components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../components/ui/card";
import { fetchMe } from "../../lib/api";
import { DEMO_ONEDRIVE, isDemoRequest } from "../../lib/demoData";

export const dynamic = "force-dynamic";

export default async function OneDrivePage({
  searchParams,
}: {
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
}) {
  const cookie = (await headers()).get("cookie") ?? "";
  const params = searchParams ? await searchParams : {};
  const demo = isDemoRequest(cookie, params);
  const me = demo
    ? { display_name: "Local Admin (Demo)", email: "admin@dev.local", role_keys: ["platform_admin"] }
    : await fetchMe(cookie);
  if (!me) redirect("/sign-in");

  const rows = demo
    ? DEMO_ONEDRIVE
    : ([] as { user: string; used_gb: number; quota_gb: number; last_active_at: string }[]);

  return (
    <AppShell me={me} currentPath="/onedrive">
      <main className="px-6 py-8">
        <header className="mb-6">
          <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
            OneDrive
          </h1>
          <p className="mt-1 max-w-2xl text-sm text-slate-400">
            Per-user OneDrive inventory, storage, sharing, activity. Populated
            once a tenant Graph connection is configured.
          </p>
        </header>

        <Card>
          <CardHeader>
            <CardTitle>OneDrive accounts</CardTitle>
            <CardDescription>Storage + last activity.</CardDescription>
          </CardHeader>
          <CardContent>
            {rows.length === 0 ? (
              <p className="text-sm text-slate-500">
                No OneDrive data yet. Connect a tenant and run the OneDrive collector
                (Phase 4+).
              </p>
            ) : (
              <div className="overflow-x-auto rounded-lg border border-slate-800/80">
                <table className="min-w-full text-left text-sm">
                  <thead className="bg-slate-900/60 text-xs uppercase tracking-wider text-slate-500">
                    <tr>
                      <th className="px-3 py-2">User</th>
                      <th className="px-3 py-2">Used</th>
                      <th className="px-3 py-2">Quota</th>
                      <th className="px-3 py-2">Last active</th>
                      <th className="px-3 py-2">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((r) => {
                      const stale = Date.parse(r.last_active_at) <
                        Date.now() - 30 * 24 * 3600 * 1000;
                      return (
                        <tr key={r.user} className="border-t border-slate-800/80 text-slate-300">
                          <td className="px-3 py-2 font-mono text-xs">{r.user}</td>
                          <td className="px-3 py-2">{r.used_gb} GB</td>
                          <td className="px-3 py-2 text-slate-500">{r.quota_gb} GB</td>
                          <td className="px-3 py-2 font-mono text-xs">
                            {new Date(r.last_active_at)
                              .toISOString()
                              .slice(0, 10)}
                          </td>
                          <td className="px-3 py-2">
                            <Badge variant={stale ? "attention" : "info"}>
                              {stale ? "inactive" : "active"}
                            </Badge>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </AppShell>
  );
}
