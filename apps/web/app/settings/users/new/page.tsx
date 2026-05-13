import { headers } from "next/headers";
import { redirect } from "next/navigation";

import { AppShell } from "../../../../components/layout/AppShell";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../../components/ui/card";
import { fetchMe } from "../../../../lib/api";
import { isDemoRequest } from "../../../../lib/demoData";
import { NewUserForm } from "../NewUserForm";

export const dynamic = "force-dynamic";

export default async function NewUserPage({
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

  return (
    <AppShell me={me} currentPath="/settings/users/new">
      <main className="px-6 py-8">
        <header className="mb-6">
          <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
            New platform user
          </h1>
          <p className="mt-1 max-w-2xl text-sm text-slate-400">
            Provision an additional admin. They will inherit the chosen roles
            on first sign-in.
          </p>
        </header>

        <Card>
          <CardHeader>
            <CardTitle>Details</CardTitle>
            <CardDescription>
              Entra users authenticate via Microsoft SSO. Local users sign in
              with a password and 6-digit TOTP code.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <NewUserForm demo={demo} />
          </CardContent>
        </Card>
      </main>
    </AppShell>
  );
}
