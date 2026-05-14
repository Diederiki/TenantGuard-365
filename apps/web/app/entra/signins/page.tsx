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

const SIGNINS = [
  { id: "s1", at: "2026-05-13T08:12:00Z", user: "bob.analyst@dev.local", ip: "203.0.113.42", country: "NL", risk: "low", outcome: "success" },
  { id: "s2", at: "2026-05-13T07:58:00Z", user: "alice.admin@dev.local", ip: "203.0.113.11", country: "NL", risk: "low", outcome: "success" },
  { id: "s3", at: "2026-05-13T05:11:00Z", user: "charlie.contractor@partner.example", ip: "5.62.20.99", country: "AE", risk: "medium", outcome: "success" },
  { id: "s4", at: "2026-05-13T04:33:00Z", user: "dana.disabled@dev.local", ip: "198.51.100.5", country: "US", risk: "high", outcome: "blocked (account disabled)" },
];

export default async function EntraSigninsPage() {
  return (
    <FrameworkPage
      module="Entra ID"
      title="Sign-ins"
      subtitle="Recent sign-in events. Risky sign-ins surface at the top with severity."
      currentPath="/entra/signins"
      status="needs-tenant"
      notes="Live data from Graph beta /auditLogs/signIns. Up to 30 days of history retained per Microsoft."
    >
      <Card>
        <CardHeader>
          <CardTitle>Recent (demo)</CardTitle>
          <CardDescription>Risk classification + outcome.</CardDescription>
        </CardHeader>
        <CardContent>
          <table className="min-w-full text-left text-sm">
            <thead className="text-xs uppercase tracking-wider text-slate-500">
              <tr>
                <th className="py-2">When (UTC)</th>
                <th className="py-2">User</th>
                <th className="py-2">IP</th>
                <th className="py-2">Country</th>
                <th className="py-2">Risk</th>
                <th className="py-2">Outcome</th>
              </tr>
            </thead>
            <tbody>
              {SIGNINS.map((s) => (
                <tr key={s.id} className="border-t border-slate-800/80 text-slate-300">
                  <td className="py-2 font-mono text-xs">{s.at}</td>
                  <td className="py-2">{s.user}</td>
                  <td className="py-2 font-mono text-xs">{s.ip}</td>
                  <td className="py-2 font-mono text-xs">{s.country}</td>
                  <td className="py-2">
                    <Badge
                      variant={
                        s.risk === "high" ? "critical" : s.risk === "medium" ? "attention" : "info"
                      }
                    >
                      {s.risk}
                    </Badge>
                  </td>
                  <td className="py-2 text-xs">{s.outcome}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </FrameworkPage>
  );
}
