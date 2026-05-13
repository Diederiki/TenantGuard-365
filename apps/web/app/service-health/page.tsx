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

export const dynamic = "force-dynamic";

export default async function ServiceHealthPage() {
  const cookie = (await headers()).get("cookie") ?? "";
  const me = await fetchMe(cookie);
  if (!me) redirect("/sign-in");

  return (
    <AppShell me={me} currentPath="/service-health">
      <main className="px-6 py-8">
        <header className="mb-6">
          <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
            Service health
          </h1>
          <p className="mt-1 max-w-2xl text-sm text-slate-400">
            Snapshot of Microsoft 365 service status from the
            <code className="mx-1 font-mono">
              /admin/serviceAnnouncement/healthOverviews
            </code>
            endpoint. The <span className="font-mono">serviceHealth.snapshot</span>{" "}
            collector refreshes this on its schedule.
          </p>
        </header>

        <Card>
          <CardHeader>
            <CardTitle>Reports</CardTitle>
            <CardDescription>
              Use the report engine to extract a snapshot.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-1">
              <li className="flex items-center justify-between">
                <span className="font-mono text-xs text-slate-400">
                  serviceHealth.overviews
                </span>
                <Badge variant="info">CSV / XLSX / HTML / PDF</Badge>
              </li>
            </ul>
          </CardContent>
        </Card>
      </main>
    </AppShell>
  );
}
