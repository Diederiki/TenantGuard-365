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
import { isDemoRequest } from "../../lib/demoData";

export const dynamic = "force-dynamic";

export default async function SettingsIndex({
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
  const q = demo ? "?demo=1" : "";

  return (
    <AppShell me={me} currentPath="/settings">
      <main className="px-6 py-8">
        <header className="mb-6">
          <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
            Settings
          </h1>
          <p className="mt-1 max-w-2xl text-sm text-slate-400">
            Configure Microsoft Graph connection, platform users, and security
            policy.
          </p>
        </header>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <a href={`/settings/graph${q}`} className="block">
            <Card className="h-full hover:border-brand-700">
              <CardHeader>
                <CardTitle>Microsoft Graph connection</CardTitle>
                <CardDescription>
                  Tenant ID, app registration client IDs, secret rotation, 2FA
                  enforcement.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Badge variant="info">configure</Badge>
              </CardContent>
            </Card>
          </a>

          <a href={`/settings/users${q}`} className="block">
            <Card className="h-full hover:border-brand-700">
              <CardHeader>
                <CardTitle>Platform users</CardTitle>
                <CardDescription>
                  Invite additional admins. Pick auth method: Entra SSO, mock
                  (dev only), or local + TOTP.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Badge variant="info">manage</Badge>
              </CardContent>
            </Card>
          </a>

          <a href={`/delegation${q}`} className="block">
            <Card className="h-full hover:border-brand-700">
              <CardHeader>
                <CardTitle>Delegation / RBAC</CardTitle>
                <CardDescription>
                  Built-in role templates + scope assignments.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Badge variant="info">browse</Badge>
              </CardContent>
            </Card>
          </a>

          <a href={`/audit${q}`} className="block">
            <Card className="h-full hover:border-brand-700">
              <CardHeader>
                <CardTitle>Audit trail</CardTitle>
                <CardDescription>
                  Append-only record of every privileged action on this platform.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Badge variant="info">browse</Badge>
              </CardContent>
            </Card>
          </a>
        </div>
      </main>
    </AppShell>
  );
}
