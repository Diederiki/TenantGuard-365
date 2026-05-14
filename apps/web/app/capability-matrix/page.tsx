import { FrameworkPage } from "../../components/layout/FrameworkPage";
import { Badge } from "../../components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../components/ui/card";

export const dynamic = "force-dynamic";

type Row = {
  feature: string;
  source: string;
  scope: string;
  status:
    | "real"
    | "mock"
    | "framework"
    | "needs-tenant"
    | "needs-purview"
    | "needs-defender"
    | "future";
};

const VARIANT: Record<Row["status"], "info" | "muted" | "attention" | "critical"> = {
  real: "info",
  mock: "info",
  framework: "muted",
  "needs-tenant": "attention",
  "needs-purview": "attention",
  "needs-defender": "critical",
  future: "muted",
};

const ROWS: Row[] = [
  { feature: "Entra ID — users", source: "Graph v1.0 /users", scope: "User.Read.All", status: "real" },
  { feature: "Entra ID — groups", source: "Graph v1.0 /groups", scope: "Group.Read.All", status: "real" },
  { feature: "Entra ID — licenses", source: "Graph v1.0 /subscribedSkus", scope: "Organization.Read.All", status: "real" },
  { feature: "Entra ID — sign-ins", source: "Graph beta /auditLogs/signIns", scope: "AuditLog.Read.All", status: "needs-tenant" },
  { feature: "Entra ID — directory audit", source: "Graph beta /auditLogs/directoryAudits", scope: "AuditLog.Read.All", status: "needs-tenant" },
  { feature: "SharePoint — sites", source: "Graph v1.0 /sites", scope: "Sites.Read.All", status: "real" },
  { feature: "SharePoint — permissions", source: "Graph v1.0 /sites/{id}/permissions", scope: "Sites.FullControl.All", status: "needs-tenant" },
  { feature: "SharePoint — sharing links", source: "Graph beta /sharingLinks", scope: "Sites.FullControl.All", status: "needs-tenant" },
  { feature: "OneDrive — accounts", source: "Graph v1.0 /users/{id}/drive", scope: "Files.Read.All", status: "needs-tenant" },
  { feature: "OneDrive — sharing", source: "Graph v1.0 /drives/{id}/items/{id}/permissions", scope: "Files.Read.All", status: "needs-tenant" },
  { feature: "Exchange — mailboxes", source: "Graph v1.0 /users/{id}/mailboxSettings", scope: "MailboxSettings.Read", status: "needs-tenant" },
  { feature: "Exchange — forwarding risk", source: "Graph v1.0 mailbox rules", scope: "MailboxSettings.Read", status: "needs-tenant" },
  { feature: "Teams — inventory", source: "Graph v1.0 /teams", scope: "Team.ReadBasic.All", status: "needs-tenant" },
  { feature: "Teams — members", source: "Graph v1.0 /teams/{id}/members", scope: "TeamMember.Read.All", status: "needs-tenant" },
  { feature: "Service health", source: "Graph v1.0 /admin/serviceAnnouncement/healthOverviews", scope: "ServiceHealth.Read.All", status: "real" },
  { feature: "Reports — Microsoft usage", source: "Graph v1.0 /reports/*", scope: "Reports.Read.All", status: "needs-tenant" },
  { feature: "Security alerts", source: "Graph v1.0 /security/alerts_v2", scope: "SecurityEvents.Read.All", status: "needs-tenant" },
  { feature: "Content search", source: "Purview eDiscovery (Graph beta)", scope: "eDiscovery.Read.All", status: "needs-purview" },
  { feature: "Defender advanced hunting", source: "Defender API /api/advancedhunting/run", scope: "AdvancedHunting.Read.All", status: "needs-defender" },
  { feature: "Remediation actions", source: "Various PATCH/POST", scope: "module-specific Write", status: "framework" },
];

export default async function CapabilityMatrixPage() {
  return (
    <FrameworkPage
      module="Help"
      title="API capability matrix"
      subtitle="Per-feature mapping of Microsoft endpoints, required scopes, and current implementation status."
      currentPath="/capability-matrix"
      status="real"
      notes="Read the source-of-truth doc for full notes: docs/microsoft-graph/capability-matrix.md."
    >
      <Card>
        <CardHeader>
          <CardTitle>Feature → API</CardTitle>
          <CardDescription>
            {ROWS.filter((r) => r.status === "real").length} live ·{" "}
            {ROWS.filter((r) => r.status === "needs-tenant").length} needs
            tenant creds ·{" "}
            {ROWS.filter((r) => r.status === "needs-purview" || r.status === "needs-defender").length}{" "}
            needs licence ·{" "}
            {ROWS.filter((r) => r.status === "framework").length} framework
          </CardDescription>
        </CardHeader>
        <CardContent>
          <table className="min-w-full text-left text-sm">
            <thead className="text-xs uppercase tracking-wider text-slate-500">
              <tr>
                <th className="py-2">Feature</th>
                <th className="py-2">Source</th>
                <th className="py-2">Scope</th>
                <th className="py-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {ROWS.map((r) => (
                <tr key={r.feature} className="border-t border-slate-800/80">
                  <td className="py-2 text-slate-200">{r.feature}</td>
                  <td className="py-2 font-mono text-xs text-slate-400">{r.source}</td>
                  <td className="py-2 font-mono text-xs text-slate-400">{r.scope}</td>
                  <td className="py-2">
                    <Badge variant={VARIANT[r.status]}>{r.status}</Badge>
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
