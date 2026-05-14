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
import { fetchMe } from "../../../lib/api";

export const dynamic = "force-dynamic";

const FIELDS: { label: string; default: string; note?: string }[] = [
  { label: "Platform name", default: "TenantGuard 365" },
  { label: "Organisation", default: "—", note: "Set via env or tenant settings" },
  { label: "Default timezone", default: "UTC" },
  { label: "Default date format", default: "ISO 8601 (YYYY-MM-DD HH:mm:ss)" },
  { label: "Default theme", default: "Dark" },
  { label: "Default language", default: "en-US (placeholder)" },
  { label: "Session timeout", default: "60 min idle / 12 h absolute" },
  { label: "Maintenance mode", default: "off", note: "Placeholder — not yet wired" },
  { label: "Support contact", default: "support@example.local", note: "Placeholder" },
  { label: "Legal / compliance message", default: "Authorised use only.", note: "Placeholder" },
];

export default async function GeneralSettingsPage() {
  const cookie = (await headers()).get("cookie") ?? "";
  const me = await fetchMe(cookie);
  if (!me) redirect("/sign-in");

  return (
    <AppShell me={me} currentPath="/settings/general">
      <main className="px-6 py-8">
        <header className="mb-6 flex items-end justify-between">
          <div>
            <p className="mb-1 text-xs font-medium uppercase tracking-widest text-brand-400">
              Settings
            </p>
            <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
              General site settings
            </h1>
            <p className="mt-1 max-w-2xl text-sm text-slate-400">
              Visual identity + global defaults. UI scaffolding only — backing
              storage is the `tg365_settings` table planned for Phase 27.
            </p>
          </div>
          <Badge variant="muted">framework</Badge>
        </header>

        <Card>
          <CardHeader>
            <CardTitle>Current values</CardTitle>
            <CardDescription>Read-only until backing table lands.</CardDescription>
          </CardHeader>
          <CardContent>
            <dl className="grid grid-cols-1 gap-3 md:grid-cols-2">
              {FIELDS.map((f) => (
                <div
                  key={f.label}
                  className="rounded-md border border-slate-800/80 bg-slate-900/40 px-3 py-2"
                >
                  <dt className="text-xs uppercase tracking-wider text-slate-500">
                    {f.label}
                  </dt>
                  <dd className="mt-1 text-sm text-slate-100">{f.default}</dd>
                  {f.note ? (
                    <p className="mt-1 text-xs text-slate-500">{f.note}</p>
                  ) : null}
                </div>
              ))}
            </dl>
          </CardContent>
        </Card>
      </main>
    </AppShell>
  );
}
