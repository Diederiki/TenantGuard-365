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
import { DEMO_CONTENT_SEARCH_PATTERNS, isDemoRequest } from "../../lib/demoData";

export const dynamic = "force-dynamic";

function sev(s: string) {
  if (s === "info") return "info" as const;
  if (s === "attention") return "attention" as const;
  if (s === "trouble") return "trouble" as const;
  return "critical" as const;
}

export default async function ContentSearchPage({
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
    <AppShell me={me} currentPath="/content-search">
      <main className="px-6 py-8">
        <header className="mb-6">
          <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
            Content search
          </h1>
          <p className="mt-1 max-w-3xl text-sm text-slate-400">
            Regex / sensitive-info pattern scans across SharePoint + OneDrive
            metadata. Off by default — set <code className="font-mono">FEATURE_CONTENT_SEARCH_ENABLED=true</code>{" "}
            and grant <code className="font-mono">content_search.run</code> to use it.
          </p>
        </header>

        <Card className="border-amber-900/40 bg-amber-950/20">
          <CardHeader>
            <CardTitle className="text-amber-200">
              Legal / compliance warning
            </CardTitle>
            <CardDescription className="text-amber-300/80">
              Content searches are subject to your jurisdiction&apos;s
              workplace-surveillance rules. The platform records who searched
              what, when, and why. Raw content is never ingested by default —
              only metadata + truncated match snippets.
            </CardDescription>
          </CardHeader>
        </Card>

        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Sensitive-information patterns</CardTitle>
            <CardDescription>
              Built-in templates. Combine into a saved profile + schedule.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="divide-y divide-slate-800/80">
              {DEMO_CONTENT_SEARCH_PATTERNS.map((p) => (
                <li
                  key={p.key}
                  className="flex items-center justify-between py-2"
                >
                  <div>
                    <div className="text-slate-100">{p.display_name}</div>
                    <div className="font-mono text-xs text-slate-500">{p.key}</div>
                  </div>
                  <Badge variant={sev(p.severity)}>{p.severity}</Badge>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </main>
    </AppShell>
  );
}
