import { FrameworkPage } from "../../../../components/layout/FrameworkPage";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../../components/ui/card";

export const dynamic = "force-dynamic";

export default async function SharePointSiteDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <FrameworkPage
      module="SharePoint Online"
      title={`Site ${id}`}
      subtitle="Per-site detail: storage, sharing posture, external users, broken inheritance."
      currentPath={`/sharepoint/sites/${id}`}
      status="framework"
      notes="Live data: GET /sites/{id} + /sites/{id}/permissions + /sites/{id}/drives."
    >
      <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Storage + activity</CardTitle>
            <CardDescription>Sourced from getSharePointSiteUsageDetail.</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-slate-500">— framework only —</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Sharing summary</CardTitle>
            <CardDescription>External users, anonymous links, sharing-link counts.</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-slate-500">— framework only —</p>
          </CardContent>
        </Card>
      </div>
    </FrameworkPage>
  );
}
