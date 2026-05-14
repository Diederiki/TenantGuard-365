import { FrameworkPage } from "../../../components/layout/FrameworkPage";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../components/ui/card";

export const dynamic = "force-dynamic";

const ACCOUNTS = [
  { upn: "alice.admin@dev.local", used_gb: 28.4, quota_gb: 1024, files: 18033 },
  { upn: "bob.analyst@dev.local", used_gb: 9.1, quota_gb: 1024, files: 6044 },
  { upn: "frank.finance@dev.local", used_gb: 280.0, quota_gb: 1024, files: 88200 },
  { upn: "john.jansen@dev.local", used_gb: 412.6, quota_gb: 5120, files: 142100 },
];

export default async function OneDriveAccountsPage() {
  return (
    <FrameworkPage
      module="OneDrive"
      title="Accounts"
      subtitle="Per-user OneDrive storage and file count. Spot heavy hitters + quota breaches."
      currentPath="/onedrive/accounts"
      status="needs-tenant"
      notes="Live data from Graph /reports/getOneDriveUsageAccountDetail."
    >
      <Card>
        <CardHeader>
          <CardTitle>Top accounts (demo)</CardTitle>
          <CardDescription>Sorted by used GB.</CardDescription>
        </CardHeader>
        <CardContent>
          <table className="min-w-full text-left text-sm">
            <thead className="text-xs uppercase tracking-wider text-slate-500">
              <tr>
                <th className="py-2">UPN</th>
                <th className="py-2">Used</th>
                <th className="py-2">Quota</th>
                <th className="py-2">Files</th>
              </tr>
            </thead>
            <tbody>
              {ACCOUNTS.map((a) => (
                <tr key={a.upn} className="border-t border-slate-800/80 text-slate-300">
                  <td className="py-2 font-mono text-xs">{a.upn}</td>
                  <td className="py-2 font-mono">{a.used_gb} GB</td>
                  <td className="py-2 font-mono text-xs">{a.quota_gb} GB</td>
                  <td className="py-2 font-mono">{a.files.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </FrameworkPage>
  );
}
