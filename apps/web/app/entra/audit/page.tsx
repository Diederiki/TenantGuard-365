import { FrameworkPage } from "../../../components/layout/FrameworkPage";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../components/ui/card";

export const dynamic = "force-dynamic";

const ROWS = [
  { at: "2026-05-13T19:01:00Z", actor: "alice.admin@dev.local", action: "User.Update", target: "ivy.intern@dev.local", reason: "department: Engineering" },
  { at: "2026-05-13T16:43:00Z", actor: "alice.admin@dev.local", action: "Group.AddMember", target: "Vendors-Read", reason: "added grace@vendor.example" },
  { at: "2026-05-13T12:12:00Z", actor: "system", action: "Application.UpdateApplication", target: "tg365-collector", reason: "secret rotated" },
];

export default async function EntraDirectoryAuditPage() {
  return (
    <FrameworkPage
      module="Entra ID"
      title="Directory audit"
      subtitle="Entra-side directory changes. Separate from this platform's own audit log."
      currentPath="/entra/audit"
      status="needs-tenant"
      notes="Live data from Graph beta /auditLogs/directoryAudits."
    >
      <Card>
        <CardHeader>
          <CardTitle>Recent (demo)</CardTitle>
          <CardDescription>Most recent on top.</CardDescription>
        </CardHeader>
        <CardContent>
          <table className="min-w-full text-left text-sm">
            <thead className="text-xs uppercase tracking-wider text-slate-500">
              <tr>
                <th className="py-2">When (UTC)</th>
                <th className="py-2">Actor</th>
                <th className="py-2">Action</th>
                <th className="py-2">Target</th>
                <th className="py-2">Detail</th>
              </tr>
            </thead>
            <tbody>
              {ROWS.map((r) => (
                <tr key={r.at} className="border-t border-slate-800/80 text-slate-300">
                  <td className="py-2 font-mono text-xs">{r.at}</td>
                  <td className="py-2 text-xs">{r.actor}</td>
                  <td className="py-2 font-mono text-xs">{r.action}</td>
                  <td className="py-2 text-xs">{r.target}</td>
                  <td className="py-2 text-xs text-slate-400">{r.reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </FrameworkPage>
  );
}
