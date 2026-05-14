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

const FIELDS: { label: string; value: string; status: "info" | "attention" | "critical" | "muted" }[] = [
  { label: "Session idle timeout", value: "60 minutes", status: "info" },
  { label: "Session absolute timeout", value: "12 hours", status: "info" },
  { label: "Require Entra SSO", value: "on (production default)", status: "info" },
  { label: "Break-glass local password", value: "disabled by default", status: "info" },
  { label: "Local-login rate limit", value: "10 / 5 min", status: "info" },
  { label: "TOTP verify rate limit", value: "5 / min", status: "info" },
  { label: "IP allowlist", value: "not configured", status: "muted" },
  { label: "Sensitive-export reason required", value: "on", status: "info" },
  { label: "Content-search reason required", value: "on", status: "info" },
  { label: "Remediation approval required", value: "on", status: "info" },
  { label: "Remediation dry-run default", value: "on", status: "info" },
  { label: "Token-cache master key", value: "set via TOKEN_CACHE_MASTER_KEY env", status: "info" },
];

export default async function SecuritySettingsPage() {
  const cookie = (await headers()).get("cookie") ?? "";
  const me = await fetchMe(cookie);
  if (!me) redirect("/sign-in");

  return (
    <AppShell me={me} currentPath="/settings/security">
      <main className="px-6 py-8">
        <header className="mb-6 flex items-end justify-between">
          <div>
            <p className="mb-1 text-xs font-medium uppercase tracking-widest text-brand-400">
              Settings
            </p>
            <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
              Security policy
            </h1>
            <p className="mt-1 max-w-2xl text-sm text-slate-400">
              Defaults are enterprise-safe. Toggles for IP allowlist, custom
              session timeouts, and per-tenant policy land in Phase 27.
            </p>
          </div>
          <Badge variant="muted">framework</Badge>
        </header>

        <Card>
          <CardHeader>
            <CardTitle>Effective policy</CardTitle>
            <CardDescription>
              Read-only view of the currently-enforced security defaults.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="divide-y divide-slate-800/80">
              {FIELDS.map((f) => (
                <li
                  key={f.label}
                  className="flex items-center justify-between py-2"
                >
                  <span className="text-sm text-slate-200">{f.label}</span>
                  <span className="flex items-center gap-2">
                    <span className="font-mono text-xs text-slate-400">
                      {f.value}
                    </span>
                    <Badge variant={f.status}>{f.status}</Badge>
                  </span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </main>
    </AppShell>
  );
}
