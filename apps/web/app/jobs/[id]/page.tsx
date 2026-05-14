import { FrameworkPage } from "../../../components/layout/FrameworkPage";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../components/ui/card";

export const dynamic = "force-dynamic";

export default async function JobDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <FrameworkPage
      module="Admin"
      title={`Sync job ${id}`}
      subtitle="Per-job-run detail: status, rows in/out, error trace, structured log preview."
      currentPath={`/jobs/${id}`}
      status="framework"
      notes="Backend: GET /api/tenants/{tid}/jobs/{id}/runs/{runId}. Cancel button wires up alongside the stuck-run reaper in Phase 28."
    >
      <Card>
        <CardHeader>
          <CardTitle>Run history</CardTitle>
          <CardDescription>Last 20 runs.</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-slate-500">— framework only —</p>
        </CardContent>
      </Card>
    </FrameworkPage>
  );
}
