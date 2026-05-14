import { headers } from "next/headers";
import { redirect } from "next/navigation";

import { AppShell } from "../../../components/layout/AppShell";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../components/ui/card";
import { fetchMe } from "../../../lib/api";
import {
  DEMO_SP_PERMISSIONS,
  DemoSpPermission,
  isDemoCookie,
} from "../../../lib/demoData";
import { SpPermsGrid } from "./SpPermsGrid";

export const dynamic = "force-dynamic";

export default async function SharePointPermissionsPage() {
  const cookie = (await headers()).get("cookie") ?? "";
  const me = await fetchMe(cookie);
  if (!me) redirect("/sign-in");

  const demo = isDemoCookie(cookie);
  const rows: DemoSpPermission[] = demo ? DEMO_SP_PERMISSIONS : [];

  return (
    <AppShell me={me} currentPath="/sharepoint/permissions">
      <main className="px-6 py-8">
        <header className="mb-6">
          <p className="mb-1 text-xs font-medium uppercase tracking-widest text-brand-400">
            SharePoint Online
          </p>
          <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
            Permissions audit
          </h1>
          <p className="mt-1 max-w-2xl text-sm text-slate-400">
            Effective principals on each SharePoint resource. Highlight
            anonymous + external sharing first — those are the risky ones.
          </p>
        </header>

        <Card>
          <CardHeader>
            <CardTitle>Permissions ({rows.length})</CardTitle>
            <CardDescription>
              {demo
                ? "Demo data — 8 fixture entries across 8 sites."
                : "No data yet. Configure Graph in Settings → Graph and run the sharepoint.permissions collector."}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {rows.length === 0 ? (
              <p className="text-sm text-slate-500">
                No permissions to display.{" "}
                {demo ? "" : "Append ?demo=1 to preview the UI."}
              </p>
            ) : (
              <SpPermsGrid rows={rows} />
            )}
          </CardContent>
        </Card>
      </main>
    </AppShell>
  );
}
