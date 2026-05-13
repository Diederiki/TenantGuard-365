import { headers } from "next/headers";
import { redirect } from "next/navigation";

import { AppShell } from "../../../../../components/layout/AppShell";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../../../components/ui/card";
import { fetchMe } from "../../../../../lib/api";
import { isDemoRequest } from "../../../../../lib/demoData";
import { TotpEnroll } from "./TotpEnroll";

export const dynamic = "force-dynamic";

export default async function TotpPage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
}) {
  const cookie = (await headers()).get("cookie") ?? "";
  const sp = searchParams ? await searchParams : {};
  const demo = isDemoRequest(cookie, sp);
  const me = demo
    ? { display_name: "Local Admin (Demo)", email: "admin@dev.local", role_keys: ["platform_admin"] }
    : await fetchMe(cookie);
  if (!me) redirect("/sign-in");
  const { id } = await params;

  return (
    <AppShell me={me} currentPath={`/settings/users/${id}/totp`}>
      <main className="px-6 py-8">
        <header className="mb-6">
          <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
            Two-factor authentication
          </h1>
          <p className="mt-1 max-w-2xl text-sm text-slate-400">
            Bind a TOTP authenticator for this user. After confirming once with
            a current code, sign-in will require email + password + TOTP.
          </p>
        </header>

        <Card>
          <CardHeader>
            <CardTitle>Enroll TOTP</CardTitle>
            <CardDescription>
              The secret is generated server-side, encrypted at rest (AES-GCM),
              and never logged.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <TotpEnroll userId={id} demo={demo} />
          </CardContent>
        </Card>
      </main>
    </AppShell>
  );
}
