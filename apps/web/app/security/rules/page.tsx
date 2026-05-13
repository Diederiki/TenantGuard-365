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
import { DEMO_RULES, isDemoCookie } from "../../../lib/demoData";

export const dynamic = "force-dynamic";

type Rule = {
  key: string;
  display_name: string;
  description: string;
  severity: "info" | "attention" | "trouble" | "critical";
  enabled_by_default: boolean;
};

function sevVariant(s: Rule["severity"]) {
  if (s === "info") return "info" as const;
  if (s === "attention") return "attention" as const;
  if (s === "trouble") return "trouble" as const;
  return "critical" as const;
}

export default async function SecurityRulesPage() {
  const cookie = (await headers()).get("cookie") ?? "";
  const me = await fetchMe(cookie);
  if (!me) redirect("/sign-in");

  const base = apiBaseUrl({ serverSide: true });
  let rules: Rule[] | { error: string };
  if (isDemoCookie(cookie)) {
    rules = DEMO_RULES as Rule[];
  } else {
    try {
      const r = await fetch(`${base}/api/security/rules`, {
        headers: { cookie },
        cache: "no-store",
      });
      rules = r.ok ? ((await r.json()) as Rule[]) : { error: `${r.status}` };
    } catch (e) {
      rules = { error: String(e) };
    }
  }

  return (
    <AppShell me={me} currentPath="/security/rules">
      <main className="px-6 py-8">
        <header className="mb-6">
          <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
            Security rules
          </h1>
          <p className="mt-1 max-w-2xl text-sm text-slate-400">
            Detection rules evaluated against ingested data. Matches deduplicate
            into ``security_alerts``.
          </p>
        </header>

        <Card>
          <CardHeader>
            <CardTitle>Built-in rules</CardTitle>
            <CardDescription>
              Severity palette: info / attention / trouble / critical.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {"error" in rules ? (
              <p className="text-sm text-rose-300">Failed to load: {rules.error}</p>
            ) : (
              <ul className="divide-y divide-slate-800/80">
                {rules.map((rule) => (
                  <li key={rule.key} className="py-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium text-slate-100">
                          {rule.display_name}
                        </div>
                        <div className="font-mono text-xs text-slate-500">
                          {rule.key}
                        </div>
                      </div>
                      <Badge variant={sevVariant(rule.severity)}>{rule.severity}</Badge>
                    </div>
                    <p className="mt-1 max-w-3xl text-sm text-slate-400">
                      {rule.description}
                    </p>
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
