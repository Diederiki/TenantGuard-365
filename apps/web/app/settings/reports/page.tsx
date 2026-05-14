import { FrameworkPage } from "../../../components/layout/FrameworkPage";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../components/ui/card";

export const dynamic = "force-dynamic";

const FIELDS = [
  { label: "Default export format", value: "CSV (UTF-8 BOM)" },
  { label: "Scheduled-report retention", value: "90 days" },
  { label: "Sensitive-report approval", value: "required for security.* + audit.export" },
  { label: "Watermarking", value: "(placeholder — Phase 28)" },
  { label: "Report access rule", value: "RBAC by report category" },
];

export default async function ReportSettingsPage() {
  return (
    <FrameworkPage
      module="Settings"
      title="Report settings"
      subtitle="Defaults for exports, retention, watermarking, access rules."
      currentPath="/settings/reports"
      status="framework"
      notes="Editing lives in Phase 28 alongside a `report_settings` row. Read-only today."
    >
      <Card>
        <CardHeader>
          <CardTitle>Effective defaults</CardTitle>
          <CardDescription>Backed by env + code, not yet DB-overridable.</CardDescription>
        </CardHeader>
        <CardContent>
          <table className="min-w-full text-left text-sm">
            <thead className="text-xs uppercase tracking-wider text-slate-500">
              <tr>
                <th className="py-2">Setting</th>
                <th className="py-2">Value</th>
              </tr>
            </thead>
            <tbody>
              {FIELDS.map((f) => (
                <tr key={f.label} className="border-t border-slate-800/80">
                  <td className="py-2 text-slate-200">{f.label}</td>
                  <td className="py-2 font-mono text-xs text-slate-300">{f.value}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </FrameworkPage>
  );
}
