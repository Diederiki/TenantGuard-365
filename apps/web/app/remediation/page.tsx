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
import { DEMO_REMEDIATION_POLICIES, isDemoCookie } from "../../lib/demoData";

export const dynamic = "force-dynamic";

type Policy = {
  key: string;
  display_name: string;
  description: string;
  required_permission: string;
  required_scopes: string[];
  supports_rollback: boolean;
  destructive: boolean;
  dry_run_default: boolean;
  approval_required: boolean;
  enabled_by_default: boolean;
};

export default async function RemediationPage() {
  const cookie = (await headers()).get("cookie") ?? "";
  const me = await fetchMe(cookie);
  if (!me) redirect("/sign-in");

  const base = apiBaseUrl({ serverSide: true });
  let policies: Policy[] | { error: string };
  if (isDemoCookie(cookie)) {
    policies = DEMO_REMEDIATION_POLICIES;
  } else {
    try {
      const r = await fetch(`${base}/api/remediation/policies`, {
        headers: { cookie },
        cache: "no-store",
      });
      policies = r.ok ? ((await r.json()) as Policy[]) : { error: `${r.status}` };
    } catch (e) {
      policies = { error: String(e) };
    }
  }

  return (
    <AppShell me={me} currentPath="/remediation">
      <main className="px-6 py-8">
        <header className="mb-6">
          <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
            Remediation
          </h1>
          <p className="mt-1 max-w-3xl text-sm text-slate-400">
            All remediation policies ship <strong>disabled</strong> and require
            second-technician approval. Dry-run by default. Apply handlers are
            intentionally not wired — operator review required per policy before
            enabling.
          </p>
        </header>

        <Card className="border-amber-900/40 bg-amber-950/20">
          <CardHeader>
            <CardTitle className="text-amber-200">Safety posture</CardTitle>
            <CardDescription className="text-amber-300/80">
              No policy here can change tenant state until you explicitly enable
              it AND grant the listed Graph scopes AND configure an approval
              chain. The platform refuses to call Graph for an unapproved or
              dry-run-only action.
            </CardDescription>
          </CardHeader>
        </Card>

        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Built-in policies</CardTitle>
            <CardDescription>
              Each policy is paired with a documented dry-run handler.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {"error" in policies ? (
              <p className="text-sm text-rose-300">Failed to load: {policies.error}</p>
            ) : (
              <ul className="divide-y divide-slate-800/80">
                {policies.map((p) => (
                  <li key={p.key} className="py-3">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div>
                        <div className="font-medium text-slate-100">
                          {p.display_name}
                        </div>
                        <div className="font-mono text-xs text-slate-500">{p.key}</div>
                      </div>
                      <div className="flex items-center gap-2">
                        {p.destructive ? (
                          <Badge variant="critical">destructive</Badge>
                        ) : null}
                        {p.supports_rollback ? (
                          <Badge variant="info">rollback</Badge>
                        ) : (
                          <Badge variant="muted">no rollback</Badge>
                        )}
                        {p.approval_required ? (
                          <Badge variant="attention">approval required</Badge>
                        ) : null}
                        <Badge
                          variant={p.enabled_by_default ? "trouble" : "muted"}
                        >
                          {p.enabled_by_default ? "enabled" : "disabled"}
                        </Badge>
                      </div>
                    </div>
                    <p className="mt-1 max-w-3xl text-sm text-slate-400">
                      {p.description}
                    </p>
                    <div className="mt-2 flex flex-wrap items-center gap-2">
                      <span className="text-xs text-slate-500">Required scopes:</span>
                      {p.required_scopes.map((s) => (
                        <span
                          key={s}
                          className="rounded border border-slate-800 px-1.5 py-0.5 font-mono text-xs text-slate-400"
                        >
                          {s}
                        </span>
                      ))}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </main>
    </AppShell>
  );
}
