import { FrameworkPage } from "../../../../components/layout/FrameworkPage";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../../components/ui/card";

export const dynamic = "force-dynamic";

export default async function InvestigationDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <FrameworkPage
      module="Security"
      title={`Investigation ${id}`}
      subtitle="Case file: timeline, attached alerts, assigned analyst, notes."
      currentPath={`/security/investigations/${id}`}
      status="framework"
      notes="Backend: GET /api/security/investigations/{id} + /events. Notes are appended to InvestigationCaseEvent."
    >
      <Card>
        <CardHeader>
          <CardTitle>Timeline</CardTitle>
          <CardDescription>Append-only event stream.</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-slate-500">— framework only —</p>
        </CardContent>
      </Card>
    </FrameworkPage>
  );
}
