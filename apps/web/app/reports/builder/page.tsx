import { FrameworkPage } from "../../../components/layout/FrameworkPage";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../components/ui/card";

export const dynamic = "force-dynamic";

export default async function ReportBuilderPage() {
  return (
    <FrameworkPage
      module="Reports"
      title="Report builder"
      subtitle="Compose a custom report: pick a base dataset, filters, columns, sort, then save."
      currentPath="/reports/builder"
      status="framework"
      notes="Backed by SavedReport rows. UI for builder lands in Phase 28 — until then operators define reports in Python under apps/api/app/reports/builtins.py."
    >
      <Card>
        <CardHeader>
          <CardTitle>Step 1 — Choose dataset</CardTitle>
          <CardDescription>One of: entra.users, sharepoint.permissions, audit, jobs.</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-slate-500">— framework only —</p>
        </CardContent>
      </Card>
    </FrameworkPage>
  );
}
