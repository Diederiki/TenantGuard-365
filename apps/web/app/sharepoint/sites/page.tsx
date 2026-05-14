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

const SITES = [
  { id: "s-1", url: "/sites/finance", visibility: "private", storage_gb: 18.2, items: 4220, last_activity: "2026-05-13" },
  { id: "s-2", url: "/sites/marketing", visibility: "public", storage_gb: 9.4, items: 2014, last_activity: "2026-05-12" },
  { id: "s-3", url: "/sites/engineering", visibility: "private", storage_gb: 41.5, items: 12099, last_activity: "2026-05-13" },
  { id: "s-4", url: "/sites/hr", visibility: "private", storage_gb: 7.1, items: 1822, last_activity: "2026-05-09" },
  { id: "s-5", url: "/sites/legal", visibility: "private", storage_gb: 12.0, items: 3110, last_activity: "2026-05-11" },
];

export default async function SharePointSitesPage() {
  return (
    <FrameworkPage
      module="SharePoint Online"
      title="Sites"
      subtitle="Tenant SharePoint sites with size, item count, and last-activity timestamp."
      currentPath="/sharepoint/sites"
      status="needs-tenant"
      notes="Live data from Graph /sites + /reports/getSharePointSiteUsageDetail."
    >
      <Card>
        <CardHeader>
          <CardTitle>Sites (demo)</CardTitle>
          <CardDescription>Public sites are flagged for review.</CardDescription>
        </CardHeader>
        <CardContent>
          <table className="min-w-full text-left text-sm">
            <thead className="text-xs uppercase tracking-wider text-slate-500">
              <tr>
                <th className="py-2">URL</th>
                <th className="py-2">Visibility</th>
                <th className="py-2">Storage</th>
                <th className="py-2">Items</th>
                <th className="py-2">Last activity</th>
              </tr>
            </thead>
            <tbody>
              {SITES.map((s) => (
                <tr key={s.id} className="border-t border-slate-800/80 text-slate-300">
                  <td className="py-2">
                    <a className="text-brand-400 hover:underline" href={`/sharepoint/sites/${s.id}`}>
                      {s.url}
                    </a>
                  </td>
                  <td className="py-2">
                    <Badge variant={s.visibility === "public" ? "attention" : "info"}>
                      {s.visibility}
                    </Badge>
                  </td>
                  <td className="py-2 font-mono">{s.storage_gb} GB</td>
                  <td className="py-2 font-mono">{s.items.toLocaleString()}</td>
                  <td className="py-2 font-mono text-xs">{s.last_activity}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </FrameworkPage>
  );
}
