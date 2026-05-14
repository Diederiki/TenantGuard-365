import { FrameworkPage } from "../../../components/layout/FrameworkPage";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../components/ui/card";

export const dynamic = "force-dynamic";

const ITEMS = [
  { site: "/sites/finance", resource: "/Shared Documents/2026-Budget.xlsx", level: "item", since: "2026-01-08" },
  { site: "/sites/engineering", resource: "/Shared Documents/Roadmap.pptx", level: "item", since: "2026-03-02" },
  { site: "/sites/legal", resource: "/Contracts/Vendor-A", level: "folder", since: "2025-12-15" },
];

export default async function SharePointBrokenInheritancePage() {
  return (
    <FrameworkPage
      module="SharePoint Online"
      title="Broken inheritance"
      subtitle="Items + folders with unique permissions. Inheritance breaks make permissions audit costly."
      currentPath="/sharepoint/broken-inheritance"
      status="needs-tenant"
      notes="Live data via Graph /sites/{id}/lists/{id}/items?$expand=fields,hasUniqueRoleAssignments. Aim < 50 per site."
    >
      <Card>
        <CardHeader>
          <CardTitle>Unique-permission items (demo)</CardTitle>
          <CardDescription>Sort by site to see hotspots.</CardDescription>
        </CardHeader>
        <CardContent>
          <table className="min-w-full text-left text-sm">
            <thead className="text-xs uppercase tracking-wider text-slate-500">
              <tr>
                <th className="py-2">Site</th>
                <th className="py-2">Resource</th>
                <th className="py-2">Level</th>
                <th className="py-2">Since</th>
              </tr>
            </thead>
            <tbody>
              {ITEMS.map((i, idx) => (
                <tr key={idx} className="border-t border-slate-800/80 text-slate-300">
                  <td className="py-2">{i.site}</td>
                  <td className="py-2 font-mono text-xs">{i.resource}</td>
                  <td className="py-2 text-xs">{i.level}</td>
                  <td className="py-2 font-mono text-xs">{i.since}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </FrameworkPage>
  );
}
