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
import { DEMO_EXCHANGE, isDemoRequest } from "../../lib/demoData";

export const dynamic = "force-dynamic";

export default async function ExchangePage({
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

  const rows = demo
    ? DEMO_EXCHANGE
    : ([] as { upn: string; mailbox_type: string; forwarding_external: boolean; inbox_rules: number }[]);

  return (
    <AppShell me={me} currentPath="/exchange">
      <main className="px-6 py-8">
        <header className="mb-6">
          <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
            Exchange Online
          </h1>
          <p className="mt-1 max-w-2xl text-sm text-slate-400">
            Mailbox inventory, permissions, forwarding, inbox rules. External
            forwarding is flagged red.
          </p>
        </header>

        <Card>
          <CardHeader>
            <CardTitle>Mailboxes</CardTitle>
            <CardDescription>
              External forwarding is a common exfiltration indicator.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {rows.length === 0 ? (
              <p className="text-sm text-slate-500">
                No mailbox data. Connect a tenant + run the Exchange collector.
              </p>
            ) : (
              <div className="overflow-x-auto rounded-lg border border-slate-800/80">
                <table className="min-w-full text-left text-sm">
                  <thead className="bg-slate-900/60 text-xs uppercase tracking-wider text-slate-500">
                    <tr>
                      <th className="px-3 py-2">User principal name</th>
                      <th className="px-3 py-2">Type</th>
                      <th className="px-3 py-2">External forwarding</th>
                      <th className="px-3 py-2">Inbox rules</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((r) => (
                      <tr key={r.upn} className="border-t border-slate-800/80 text-slate-300">
                        <td className="px-3 py-2 font-mono text-xs">{r.upn}</td>
                        <td className="px-3 py-2">{r.mailbox_type}</td>
                        <td className="px-3 py-2">
                          <Badge variant={r.forwarding_external ? "critical" : "info"}>
                            {r.forwarding_external ? "external — review" : "off"}
                          </Badge>
                        </td>
                        <td className="px-3 py-2 text-xs">{r.inbox_rules}</td>
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
