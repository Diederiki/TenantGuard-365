import { FrameworkPage } from "../../../components/layout/FrameworkPage";
import { Badge } from "../../../components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../components/ui/card";

export const dynamic = "force-dynamic";

const RULES = [
  { mb: "frank.finance@dev.local", to: "frank.personal@gmail.com", scope: "external", action: "forward + delete", risk: "critical" },
  { mb: "henry.hr@dev.local", to: "leaks@vendor.example", scope: "external", action: "forward", risk: "critical" },
  { mb: "ivy.intern@dev.local", to: "ivy.intern@dev.local-archive", scope: "internal", action: "move to folder", risk: "info" },
];

export default async function ExchangeForwardingRiskPage() {
  return (
    <FrameworkPage
      module="Exchange Online"
      title="Forwarding risk"
      subtitle="Inbox rules that forward mail outside the tenant. Top risk for data exfiltration."
      currentPath="/exchange/forwarding-risk"
      status="needs-tenant"
      notes="Detect via /users/{id}/messageRules + transport rule scan."
    >
      <Card>
        <CardHeader>
          <CardTitle>External forwarding (demo)</CardTitle>
          <CardDescription>
            Anything outbound to a non-tenant domain triggers critical.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <table className="min-w-full text-left text-sm">
            <thead className="text-xs uppercase tracking-wider text-slate-500">
              <tr>
                <th className="py-2">Mailbox</th>
                <th className="py-2">Forwards to</th>
                <th className="py-2">Scope</th>
                <th className="py-2">Action</th>
                <th className="py-2">Risk</th>
              </tr>
            </thead>
            <tbody>
              {RULES.map((r, i) => (
                <tr key={i} className="border-t border-slate-800/80 text-slate-300">
                  <td className="py-2">{r.mb}</td>
                  <td className="py-2 font-mono text-xs">{r.to}</td>
                  <td className="py-2 text-xs">{r.scope}</td>
                  <td className="py-2 text-xs">{r.action}</td>
                  <td className="py-2">
                    <Badge variant={r.risk as "info" | "critical"}>{r.risk}</Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </FrameworkPage>
  );
}
