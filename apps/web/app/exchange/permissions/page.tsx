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

const PERMS = [
  { mb: "frank.finance@dev.local", grantee: "bob.analyst@dev.local", access: "FullAccess", risk: "attention" },
  { mb: "frank.finance@dev.local", grantee: "alice.admin@dev.local", access: "SendAs", risk: "critical" },
  { mb: "john.jansen@dev.local", grantee: "henry.hr@dev.local", access: "Reviewer (inbox folder)", risk: "info" },
];

export default async function ExchangePermissionsPage() {
  return (
    <FrameworkPage
      module="Exchange Online"
      title="Mailbox permissions"
      subtitle="Who has FullAccess, SendAs, or SendOnBehalfOf on whose mailbox."
      currentPath="/exchange/permissions"
      status="needs-tenant"
      notes="SendAs is highlighted critical — anyone with this can send messages as the mailbox owner."
    >
      <Card>
        <CardHeader>
          <CardTitle>Permissions (demo)</CardTitle>
          <CardDescription>Filter for SendAs to surface impersonation risk.</CardDescription>
        </CardHeader>
        <CardContent>
          <table className="min-w-full text-left text-sm">
            <thead className="text-xs uppercase tracking-wider text-slate-500">
              <tr>
                <th className="py-2">Mailbox</th>
                <th className="py-2">Grantee</th>
                <th className="py-2">Access</th>
                <th className="py-2">Risk</th>
              </tr>
            </thead>
            <tbody>
              {PERMS.map((p, i) => (
                <tr key={i} className="border-t border-slate-800/80 text-slate-300">
                  <td className="py-2">{p.mb}</td>
                  <td className="py-2">{p.grantee}</td>
                  <td className="py-2 font-mono text-xs">{p.access}</td>
                  <td className="py-2">
                    <Badge variant={p.risk as "info" | "attention" | "critical"}>{p.risk}</Badge>
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
