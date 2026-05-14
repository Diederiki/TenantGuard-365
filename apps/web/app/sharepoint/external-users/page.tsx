import { FrameworkPage } from "../../../components/layout/FrameworkPage";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../components/ui/card";

export const dynamic = "force-dynamic";

const EXT = [
  { email: "charlie@partner.example", sites: 3, last_access: "2026-05-12", invited_by: "alice.admin@dev.local" },
  { email: "grace@vendor.example", sites: 1, last_access: "2026-04-30", invited_by: "frank.finance@dev.local" },
  { email: "ex@old.example", sites: 5, last_access: "2025-11-02", invited_by: "(removed)" },
];

export default async function SharePointExternalUsersPage() {
  return (
    <FrameworkPage
      module="SharePoint Online"
      title="External users"
      subtitle="Guest accounts with access to one or more sites. Stale guests flagged for review."
      currentPath="/sharepoint/external-users"
      status="needs-tenant"
      notes="Stale = last access > 90 days. Generate Phase-28 cleanup report from this list."
    >
      <Card>
        <CardHeader>
          <CardTitle>External users (demo)</CardTitle>
          <CardDescription>Click an entry to see which sites grant access.</CardDescription>
        </CardHeader>
        <CardContent>
          <table className="min-w-full text-left text-sm">
            <thead className="text-xs uppercase tracking-wider text-slate-500">
              <tr>
                <th className="py-2">Email</th>
                <th className="py-2">Sites</th>
                <th className="py-2">Last access</th>
                <th className="py-2">Invited by</th>
              </tr>
            </thead>
            <tbody>
              {EXT.map((e) => (
                <tr key={e.email} className="border-t border-slate-800/80 text-slate-300">
                  <td className="py-2 font-mono text-xs">{e.email}</td>
                  <td className="py-2 font-mono">{e.sites}</td>
                  <td className="py-2 font-mono text-xs">{e.last_access}</td>
                  <td className="py-2 text-xs">{e.invited_by}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </FrameworkPage>
  );
}
