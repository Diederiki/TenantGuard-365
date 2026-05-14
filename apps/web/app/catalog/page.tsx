import { FrameworkPage } from "../../components/layout/FrameworkPage";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../components/ui/card";
import { FEATURES } from "../../lib/featureCatalog";
import { CatalogGrid } from "./CatalogGrid";

export const dynamic = "force-dynamic";

function countBy<K extends string>(arr: { [k: string]: unknown }[], key: K): Record<string, number> {
  const out: Record<string, number> = {};
  for (const x of arr) {
    const v = String(x[key]);
    out[v] = (out[v] ?? 0) + 1;
  }
  return out;
}

export default async function CatalogPage() {
  const byStatus = countBy(FEATURES as unknown as { [k: string]: unknown }[], "status");
  const byPriority = countBy(FEATURES as unknown as { [k: string]: unknown }[], "priority");
  const real = byStatus["implemented_real_api"] ?? 0;
  const mock = byStatus["implemented_mock_only"] ?? 0;
  const fw = byStatus["framework_ready"] ?? 0;
  const blocked =
    (byStatus["needs_graph_permission"] ?? 0) +
    (byStatus["needs_purview"] ?? 0) +
    (byStatus["needs_defender"] ?? 0) +
    (byStatus["needs_exchange_powershell"] ?? 0) +
    (byStatus["needs_sharepoint_api_validation"] ?? 0);

  return (
    <FrameworkPage
      module="Help"
      title="Feature parity catalog"
      subtitle="Every capability the platform claims, mapped to a Microsoft API, a UI page, an implementation status."
      currentPath="/catalog"
      status="real"
      notes="Source: apps/api/app/registry/features.py. The same data ships at GET /api/catalog/features. Use the filters to narrow by module / status / priority."
    >
      <div className="mb-4 grid grid-cols-2 gap-2 md:grid-cols-5">
        <Card>
          <CardHeader>
            <CardDescription>Total</CardDescription>
            <CardTitle>{FEATURES.length}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader>
            <CardDescription>Live</CardDescription>
            <CardTitle>{real}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader>
            <CardDescription>Mock only</CardDescription>
            <CardTitle>{mock}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader>
            <CardDescription>Framework</CardDescription>
            <CardTitle>{fw}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader>
            <CardDescription>Needs permission / licence</CardDescription>
            <CardTitle>{blocked}</CardTitle>
          </CardHeader>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Catalog</CardTitle>
          <CardDescription>
            MVP {byPriority["MVP"] ?? 0} · Phase 2 {byPriority["Phase 2"] ?? 0} · Phase 3{" "}
            {byPriority["Phase 3"] ?? 0} · Future {byPriority["Future"] ?? 0}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <CatalogGrid features={FEATURES} />
        </CardContent>
      </Card>
    </FrameworkPage>
  );
}
