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
  DEMO_ENTRA_USERS,
  DemoEntraUser,
  isDemoCookie,
} from "../../../lib/demoData";
import { EntraUsersGrid } from "./EntraUsersGrid";

export const dynamic = "force-dynamic";

export default async function EntraUsersPage() {
  const cookie = (await headers()).get("cookie") ?? "";
  const me = await fetchMe(cookie);
  if (!me) redirect("/sign-in");

  // For now, only demo mode has a usable user list because there's no
  // `/api/entra/users` paginated list endpoint yet — it's served via reports.
  // When that endpoint lands, swap this branch.
  const demo = isDemoCookie(cookie);
  const users: DemoEntraUser[] = demo ? DEMO_ENTRA_USERS : [];

  return (
    <AppShell me={me} currentPath="/entra/users">
      <main className="px-6 py-8">
        <header className="mb-6">
          <p className="mb-1 text-xs font-medium uppercase tracking-widest text-brand-400">
            Entra ID
          </p>
          <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
            Directory users
          </h1>
          <p className="mt-1 max-w-2xl text-sm text-slate-400">
            Server-side mirror of the tenant directory. Filterable, sortable.
            Click a row to drill into a user.
          </p>
        </header>

        <Card>
          <CardHeader>
            <CardTitle>Users ({users.length})</CardTitle>
            <CardDescription>
              {demo
                ? "Demo data — 10 fixture users. Real data shows when Graph collector has run."
                : "No data yet. Configure Graph in Settings → Graph and run the entra.users collector."}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {users.length === 0 ? (
              <p className="text-sm text-slate-500">
                No users to display. {demo ? "" : "Append ?demo=1 to preview the UI."}
              </p>
            ) : (
              <EntraUsersGrid rows={users} />
            )}
          </CardContent>
        </Card>
      </main>
    </AppShell>
  );
}
