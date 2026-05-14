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

const ROLES = [
  { id: "62e90394-69f5-4237-9190-012177145e10", name: "Global Administrator", members: 2, risk: "critical" },
  { id: "b0f54661-2d74-4c50-afa3-1ec803f12efe", name: "Billing Administrator", members: 1, risk: "info" },
  { id: "194ae4cb-b126-40b2-bd5b-6091b380977d", name: "Security Administrator", members: 3, risk: "attention" },
  { id: "8424c6f0-a189-499e-bbd0-26c1753c96d4", name: "User Administrator", members: 2, risk: "attention" },
] as const;

export default async function EntraRolesPage() {
  return (
    <FrameworkPage
      module="Entra ID"
      title="Directory roles"
      subtitle="Active directory-role assignments. Highlights privileged roles first."
      currentPath="/entra/roles"
      status="needs-tenant"
      notes="Live data comes from Graph /directoryRoles. The number of Global Administrators should be 2-4 — alert anything else."
    >
      <Card>
        <CardHeader>
          <CardTitle>Privileged roles (demo)</CardTitle>
          <CardDescription>Sorted by built-in risk class.</CardDescription>
        </CardHeader>
        <CardContent>
          <table className="min-w-full text-left text-sm">
            <thead className="text-xs uppercase tracking-wider text-slate-500">
              <tr>
                <th className="py-2">Role</th>
                <th className="py-2">Members</th>
                <th className="py-2">Risk class</th>
                <th className="py-2">Role template ID</th>
              </tr>
            </thead>
            <tbody>
              {ROLES.map((r) => (
                <tr key={r.id} className="border-t border-slate-800/80 text-slate-300">
                  <td className="py-2">{r.name}</td>
                  <td className="py-2 font-mono">{r.members}</td>
                  <td className="py-2">
                    <Badge variant={r.risk as "critical" | "attention" | "info"}>{r.risk}</Badge>
                  </td>
                  <td className="py-2 font-mono text-xs text-slate-500">{r.id}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </FrameworkPage>
  );
}
