import { headers } from "next/headers";
import { redirect } from "next/navigation";

import { AppShell } from "../../../components/layout/AppShell";
import { Badge } from "../../../components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../components/ui/card";
import { apiBaseUrl, fetchMe } from "../../../lib/api";
import { DEMO_RBAC_USERS, isDemoRequest } from "../../../lib/demoData";

export const dynamic = "force-dynamic";

type U = {
  id: string;
  email: string;
  display_name: string;
  is_active: boolean;
  auth_method?: string;
};

export default async function UsersPage({
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

  let users: U[] | { error: string };
  if (demo) {
    users = DEMO_RBAC_USERS;
  } else {
    const base = apiBaseUrl({ serverSide: true });
    try {
      const r = await fetch(`${base}/api/rbac/users`, {
        headers: { cookie },
        cache: "no-store",
      });
      users = r.ok ? ((await r.json()) as U[]) : { error: `${r.status}` };
    } catch (e) {
      users = { error: String(e) };
    }
  }

  const q = demo ? "?demo=1" : "";

  return (
    <AppShell me={me} currentPath="/settings/users">
      <main className="px-6 py-8">
        <header className="mb-6 flex items-end justify-between">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
              Platform users
            </h1>
            <p className="mt-1 max-w-2xl text-sm text-slate-400">
              Admins who can sign into this platform. Sign-in via Microsoft
              Entra SSO, or local password + TOTP for break-glass.
            </p>
          </div>
          <a
            href={`/settings/users/new${q}`}
            className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-500"
          >
            + New user
          </a>
        </header>

        <Card>
          <CardHeader>
            <CardTitle>Users</CardTitle>
            <CardDescription>{Array.isArray(users) ? users.length : 0} accounts</CardDescription>
          </CardHeader>
          <CardContent>
            {"error" in users ? (
              <p className="text-sm text-rose-300">Failed: {users.error}</p>
            ) : (
              <div className="overflow-x-auto rounded-lg border border-slate-800/80">
                <table className="min-w-full text-left text-sm">
                  <thead className="bg-slate-900/60 text-xs uppercase tracking-wider text-slate-500">
                    <tr>
                      <th className="px-3 py-2">User</th>
                      <th className="px-3 py-2">Auth</th>
                      <th className="px-3 py-2">Status</th>
                      <th className="px-3 py-2 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((u) => (
                      <tr key={u.id} className="border-t border-slate-800/80 text-slate-300">
                        <td className="px-3 py-2">
                          <div className="text-slate-100">{u.display_name}</div>
                          <div className="text-xs text-slate-500">{u.email}</div>
                        </td>
                        <td className="px-3 py-2">
                          <Badge
                            variant={u.auth_method === "entra" ? "info" : "attention"}
                          >
                            {u.auth_method ?? "entra"}
                          </Badge>
                        </td>
                        <td className="px-3 py-2">
                          <Badge variant={u.is_active ? "info" : "muted"}>
                            {u.is_active ? "active" : "disabled"}
                          </Badge>
                        </td>
                        <td className="px-3 py-2 text-right">
                          {u.auth_method !== "entra" ? (
                            <a
                              className="text-xs text-brand-400 hover:underline"
                              href={`/settings/users/${u.id}/totp${q}`}
                            >
                              Set up TOTP
                            </a>
                          ) : (
                            <span className="text-xs text-slate-500">
                              MFA via Entra CA policy
                            </span>
                          )}
                        </td>
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
