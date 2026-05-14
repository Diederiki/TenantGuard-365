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

const LINKS = [
  { id: "l1", site: "/sites/marketing", resource: "/Public/Brand-guidelines.pdf", scope: "anonymous", access: "view", expires: null, risk: "critical" },
  { id: "l2", site: "/sites/engineering", resource: "/Shared Documents/Roadmap.pptx", scope: "specific-people", access: "edit", expires: "2026-08-01", risk: "attention" },
  { id: "l3", site: "/sites/finance", resource: "/Shared Documents/2026-Budget.xlsx", scope: "specific-people", access: "view", expires: "2026-06-01", risk: "info" },
];

export default async function SharePointSharingLinksPage() {
  return (
    <FrameworkPage
      module="SharePoint Online"
      title="Sharing links"
      subtitle="Anonymous + organisation + specific-people links across all sites."
      currentPath="/sharepoint/sharing-links"
      status="needs-tenant"
      notes="Live data: SharePoint sharing-link collector. Anonymous links without an expiry are flagged critical."
    >
      <Card>
        <CardHeader>
          <CardTitle>Active links (demo)</CardTitle>
          <CardDescription>Sort by risk descending.</CardDescription>
        </CardHeader>
        <CardContent>
          <table className="min-w-full text-left text-sm">
            <thead className="text-xs uppercase tracking-wider text-slate-500">
              <tr>
                <th className="py-2">Site</th>
                <th className="py-2">Resource</th>
                <th className="py-2">Scope</th>
                <th className="py-2">Access</th>
                <th className="py-2">Expires</th>
                <th className="py-2">Risk</th>
              </tr>
            </thead>
            <tbody>
              {LINKS.map((l) => (
                <tr key={l.id} className="border-t border-slate-800/80 text-slate-300">
                  <td className="py-2">{l.site}</td>
                  <td className="py-2 font-mono text-xs">{l.resource}</td>
                  <td className="py-2 text-xs">{l.scope}</td>
                  <td className="py-2 text-xs">{l.access}</td>
                  <td className="py-2 font-mono text-xs">{l.expires ?? "never"}</td>
                  <td className="py-2">
                    <Badge variant={l.risk as "info" | "attention" | "critical"}>{l.risk}</Badge>
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
