import { FrameworkPage } from "../../../../components/layout/FrameworkPage";
import { Badge } from "../../../../components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../../components/ui/card";

export const dynamic = "force-dynamic";

export default async function AlertDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <FrameworkPage
      module="Security"
      title={`Alert ${id}`}
      subtitle="Triage view: rule, signals, suggested actions, history."
      currentPath={`/security/alerts/${id}`}
      status="framework"
      notes="Backend: GET /api/security/alerts/{id}. Actions: acknowledge, escalate, open investigation."
    >
      <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Signals</CardTitle>
            <CardDescription>Evidence that triggered the rule.</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-1 text-sm text-slate-300">
              <li>Sign-in from new country (NL → AE) <Badge variant="attention">medium</Badge></li>
              <li>Mailbox rule created → external <Badge variant="critical">high</Badge></li>
              <li>SharePoint anonymous link created <Badge variant="critical">high</Badge></li>
            </ul>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Suggested next steps</CardTitle>
            <CardDescription>Dry-run only. Apply manually.</CardDescription>
          </CardHeader>
          <CardContent>
            <ol className="space-y-1 text-sm text-slate-300">
              <li>1. Force token revoke for the user.</li>
              <li>2. Remove the suspicious inbox rule.</li>
              <li>3. Revoke + reissue anonymous links.</li>
            </ol>
          </CardContent>
        </Card>
      </div>
    </FrameworkPage>
  );
}
