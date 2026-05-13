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
import { apiBaseUrl, fetchMe } from "../../lib/api";

export const dynamic = "force-dynamic";

type Role = {
  id: string;
  key: string;
  display_name: string;
  description: string;
  is_builtin: boolean;
};

type User = {
  id: string;
  email: string;
  display_name: string;
  is_active: boolean;
};

export default async function DelegationPage() {
  const cookie = (await headers()).get("cookie") ?? "";
  const me = await fetchMe(cookie);
  if (!me) redirect("/sign-in");

  const base = apiBaseUrl({ serverSide: true });
  async function safe<T>(path: string): Promise<T | { error: string }> {
    try {
      const r = await fetch(`${base}${path}`, {
        headers: { cookie },
        cache: "no-store",
      });
      return r.ok ? ((await r.json()) as T) : { error: `${r.status}` };
    } catch (e) {
      return { error: String(e) };
    }
  }

  const [roles, users] = await Promise.all([
    safe<Role[]>("/api/rbac/roles"),
    safe<User[]>("/api/rbac/users"),
  ]);

  return (
    <AppShell me={me} currentPath="/delegation">
      <main className="px-6 py-8">
        <header className="mb-6">
          <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
            Delegation / RBAC
          </h1>
          <p className="mt-1 max-w-2xl text-sm text-slate-400">
            Roles bundle atomic permissions. Assignments can be scoped to
            tenant / domain / site / department.
          </p>
        </header>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Roles</CardTitle>
              <CardDescription>
                Built-in templates are read-only. Custom roles inherit from a
                template.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {"error" in roles ? (
                <p className="text-sm text-rose-300">Failed: {roles.error}</p>
              ) : (
                <ul className="divide-y divide-slate-800/80">
                  {roles.map((r) => (
                    <li
                      key={r.key}
                      className="flex items-center justify-between py-2"
                    >
                      <div>
                        <div className="text-slate-100">{r.display_name}</div>
                        <div className="font-mono text-xs text-slate-500">
                          {r.key}
                        </div>
                      </div>
                      {r.is_builtin ? (
                        <Badge variant="info">built-in</Badge>
                      ) : (
                        <Badge variant="muted">custom</Badge>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Users</CardTitle>
              <CardDescription>Platform users that can sign in.</CardDescription>
            </CardHeader>
            <CardContent>
              {"error" in users ? (
                <p className="text-sm text-rose-300">Failed: {users.error}</p>
              ) : (
                <ul className="divide-y divide-slate-800/80">
                  {users.map((u) => (
                    <li
                      key={u.id}
                      className="flex items-center justify-between py-2"
                    >
                      <div>
                        <div className="text-slate-100">{u.display_name}</div>
                        <div className="text-xs text-slate-500">{u.email}</div>
                      </div>
                      <Badge variant={u.is_active ? "info" : "muted"}>
                        {u.is_active ? "active" : "disabled"}
                      </Badge>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </AppShell>
  );
}
