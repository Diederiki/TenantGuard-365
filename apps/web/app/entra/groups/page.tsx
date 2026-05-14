import { FrameworkPage } from "../../../components/layout/FrameworkPage";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../components/ui/card";

export const dynamic = "force-dynamic";

const DEMO = [
  { id: "g-1", name: "Finance team", type: "Microsoft 365", members: 12, owners: 2 },
  { id: "g-2", name: "Engineering team", type: "Microsoft 365", members: 24, owners: 3 },
  { id: "g-3", name: "All Staff", type: "Security", members: 132, owners: 1 },
  { id: "g-4", name: "Vendors-Read", type: "Security", members: 7, owners: 1 },
];

export default async function EntraGroupsPage() {
  return (
    <FrameworkPage
      module="Entra ID"
      title="Groups"
      subtitle="Inventory of Microsoft 365 + Security groups, with member + owner counts."
      currentPath="/entra/groups"
      status="needs-tenant"
      notes="Live data comes from the entra.groups collector. Configure Graph credentials and run the collector to populate."
    >
      <Card>
        <CardHeader>
          <CardTitle>Groups ({DEMO.length} demo)</CardTitle>
          <CardDescription>Sortable list. Click a row to drill in (Phase 28).</CardDescription>
        </CardHeader>
        <CardContent>
          <table className="min-w-full text-left text-sm">
            <thead className="text-xs uppercase tracking-wider text-slate-500">
              <tr>
                <th className="py-2">Group</th>
                <th className="py-2">Type</th>
                <th className="py-2">Members</th>
                <th className="py-2">Owners</th>
              </tr>
            </thead>
            <tbody>
              {DEMO.map((g) => (
                <tr key={g.id} className="border-t border-slate-800/80 text-slate-300">
                  <td className="py-2">{g.name}</td>
                  <td className="py-2 font-mono text-xs">{g.type}</td>
                  <td className="py-2 font-mono">{g.members}</td>
                  <td className="py-2 font-mono">{g.owners}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </FrameworkPage>
  );
}
