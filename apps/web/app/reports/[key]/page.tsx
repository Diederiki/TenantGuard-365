import { FrameworkPage } from "../../../components/layout/FrameworkPage";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../components/ui/card";

export const dynamic = "force-dynamic";

export default async function ReportDetailPage({
  params,
}: {
  params: Promise<{ key: string }>;
}) {
  const { key } = await params;
  return (
    <FrameworkPage
      module="Reports"
      title={key}
      subtitle="Run, schedule, export. Live preview shows the first 50 rows."
      currentPath={`/reports/${key}`}
      status="framework"
      notes="Backend: POST /api/reports/{key}/run returns a run id; GET /api/reports/runs/{id} streams the rows."
    >
      <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Run now</CardTitle>
            <CardDescription>Synchronous for small reports.</CardDescription>
          </CardHeader>
          <CardContent>
            <button
              type="button"
              disabled
              className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
            >
              Run (framework)
            </button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Schedule</CardTitle>
            <CardDescription>Cron expression + recipients.</CardDescription>
          </CardHeader>
          <CardContent>
            <button
              type="button"
              disabled
              className="rounded-md border border-slate-800 px-4 py-2 text-sm text-slate-400 disabled:opacity-50"
            >
              New schedule (framework)
            </button>
          </CardContent>
        </Card>
      </div>
    </FrameworkPage>
  );
}
