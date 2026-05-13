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
import { DEMO_TEAMS, isDemoRequest } from "../../lib/demoData";

export const dynamic = "force-dynamic";

export default async function TeamsPage({
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

  const rows = demo ? DEMO_TEAMS : ([] as typeof DEMO_TEAMS);

  return (
    <AppShell me={me} currentPath="/teams">
      <main className="px-6 py-8">
        <header className="mb-6">
          <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
            Microsoft Teams
          </h1>
          <p className="mt-1 max-w-2xl text-sm text-slate-400">
            Teams inventory, members, guests, channel breakdown.
          </p>
        </header>

        <Card>
          <CardHeader>
            <CardTitle>Teams</CardTitle>
            <CardDescription>Guests are highlighted.</CardDescription>
          </CardHeader>
          <CardContent>
            {rows.length === 0 ? (
              <p className="text-sm text-slate-500">No Teams data yet.</p>
            ) : (
              <div className="overflow-x-auto rounded-lg border border-slate-800/80">
                <table className="min-w-full text-left text-sm">
                  <thead className="bg-slate-900/60 text-xs uppercase tracking-wider text-slate-500">
                    <tr>
                      <th className="px-3 py-2">Team</th>
                      <th className="px-3 py-2">Visibility</th>
                      <th className="px-3 py-2">Members</th>
                      <th className="px-3 py-2">Guests</th>
                      <th className="px-3 py-2">Channels</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((t) => (
                      <tr key={t.name} className="border-t border-slate-800/80 text-slate-300">
                        <td className="px-3 py-2 text-slate-100">{t.name}</td>
                        <td className="px-3 py-2">
                          <Badge variant={t.visibility === "Public" ? "info" : "muted"}>
                            {t.visibility}
                          </Badge>
                        </td>
                        <td className="px-3 py-2 text-xs">{t.members}</td>
                        <td className="px-3 py-2">
                          {t.guests > 0 ? (
                            <Badge variant="attention">{t.guests}</Badge>
                          ) : (
                            <span className="text-xs text-slate-500">0</span>
                          )}
                        </td>
                        <td className="px-3 py-2 text-xs">{t.channels}</td>
                      </tr>
                    ))}
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
