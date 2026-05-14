import { FrameworkPage } from "../../../components/layout/FrameworkPage";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../components/ui/card";

export const dynamic = "force-dynamic";

export default async function ContentSearchDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <FrameworkPage
      module="Security"
      title={`Content search ${id}`}
      subtitle="Search profile detail: scope, query, run history, results export."
      currentPath={`/content-search/${id}`}
      status="needs-purview"
      notes="Content search is licence-gated (Purview eDiscovery). Today this is framework only; running a real search requires the eDiscovery role assignment in Purview."
    >
      <Card>
        <CardHeader>
          <CardTitle>Run history</CardTitle>
          <CardDescription>Reason-of-search captured per run for audit.</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-slate-500">— framework only —</p>
        </CardContent>
      </Card>
    </FrameworkPage>
  );
}
