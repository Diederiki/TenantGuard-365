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

const reports = [
  "sharepoint.sites.inventory",
  "sharepoint.sharing.anonymous_links",
];
const rules = [
  "sharepoint.anonymous_link_present",
  "sharepoint.org_wide_link_present",
];

export default async function SharePointPage() {
  const cookie = (await headers()).get("cookie") ?? "";
  const me = await fetchMe(cookie);
  if (!me) redirect("/sign-in");

  return (
    <AppShell me={me} currentPath="/sharepoint">
      <main className="px-6 py-8">
        <header className="mb-6">
          <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
            SharePoint Online
          </h1>
          <p className="mt-1 max-w-2xl text-sm text-slate-400">
            Site inventory, permissions, sharing links. Deep inheritance scan
            ships when the SharePoint permissions collector first runs against
            a connected tenant.
          </p>
        </header>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>What you can do</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-1.5 text-sm text-slate-300">
                <li>• Site inventory (display name, URL, storage, last modified)</li>
                <li>• Sharing-link audit (anonymous / company-wide / users)</li>
                <li>• Permission grants by item / list / site</li>
                <li>• External / guest user grants per site</li>
                <li>• Broken-inheritance detection (Phase 6+ scan)</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Reports + rules</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="mb-3">
                <div className="text-xs uppercase tracking-wider text-slate-500">
                  Reports
                </div>
                <ul className="mt-1 space-y-1">
                  {reports.map((r) => (
                    <li key={r} className="font-mono text-xs text-slate-400">
                      {r}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <div className="text-xs uppercase tracking-wider text-slate-500">
                  Security rules
                </div>
                <ul className="mt-1 space-y-1">
                  {rules.map((r) => (
                    <li key={r} className="flex items-center justify-between">
                      <span className="font-mono text-xs text-slate-400">{r}</span>
                      <Badge variant="info">enabled</Badge>
                    </li>
                  ))}
                </ul>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </AppShell>
  );
}
