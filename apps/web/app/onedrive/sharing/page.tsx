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

const SHARES = [
  { id: "od-1", owner: "frank.finance@dev.local", path: "/Finance/2026/Budget.xlsx", with: "charlie@partner.example", access: "edit", scope: "external", risk: "critical" },
  { id: "od-2", owner: "alice.admin@dev.local", path: "/Personal/IT-passwords.txt", with: "(anyone with link)", access: "view", scope: "anonymous", risk: "critical" },
  { id: "od-3", owner: "bob.analyst@dev.local", path: "/Work/Quarterly-report.pdf", with: "frank.finance@dev.local", access: "view", scope: "internal", risk: "info" },
];

export default async function OneDriveSharingPage() {
  return (
    <FrameworkPage
      module="OneDrive"
      title="Sharing"
      subtitle="Files shared from OneDrive. External + anonymous links surface first."
      currentPath="/onedrive/sharing"
      status="needs-tenant"
      notes="Live data: /drives/{id}/root/permissions and recursive enumeration of /children with hasUniqueRoleAssignments."
    >
      <Card>
        <CardHeader>
          <CardTitle>OneDrive shares (demo)</CardTitle>
          <CardDescription>Sort by risk descending.</CardDescription>
        </CardHeader>
        <CardContent>
          <table className="min-w-full text-left text-sm">
            <thead className="text-xs uppercase tracking-wider text-slate-500">
              <tr>
                <th className="py-2">Owner</th>
                <th className="py-2">Path</th>
                <th className="py-2">With</th>
                <th className="py-2">Access</th>
                <th className="py-2">Scope</th>
                <th className="py-2">Risk</th>
              </tr>
            </thead>
            <tbody>
              {SHARES.map((s) => (
                <tr key={s.id} className="border-t border-slate-800/80 text-slate-300">
                  <td className="py-2 font-mono text-xs">{s.owner}</td>
                  <td className="py-2 font-mono text-xs">{s.path}</td>
                  <td className="py-2 font-mono text-xs">{s.with}</td>
                  <td className="py-2 text-xs">{s.access}</td>
                  <td className="py-2 text-xs">{s.scope}</td>
                  <td className="py-2">
                    <Badge variant={s.risk as "info" | "attention" | "critical"}>{s.risk}</Badge>
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
