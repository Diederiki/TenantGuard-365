import { FrameworkPage } from "../../components/layout/FrameworkPage";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../components/ui/card";

export const dynamic = "force-dynamic";

const DEMO = [
  { id: "exp-2026-05-13-001", report: "SharePoint anonymous links", format: "csv", size_kb: 412, by: "Alice Admin", at: "2026-05-13T16:00:00Z" },
  { id: "exp-2026-05-13-002", report: "Entra guests", format: "xlsx", size_kb: 88, by: "Bob Analyst", at: "2026-05-13T11:42:00Z" },
  { id: "exp-2026-05-12-001", report: "Audit log – last 30 days", format: "csv", size_kb: 12480, by: "Alice Admin", at: "2026-05-12T22:01:00Z" },
];

export default async function ExportsPage() {
  return (
    <FrameworkPage
      module="Reports"
      title="Exports"
      subtitle="Generated report exports. Streamed from MinIO; signed URLs expire after 15 minutes."
      currentPath="/exports"
      status="framework"
      notes="Listing reads `report_exports` table joined to MinIO object metadata. Today this page renders demo fixtures."
    >
      <Card>
        <CardHeader>
          <CardTitle>Recent exports</CardTitle>
          <CardDescription>
            Sorted newest first. Each row links to a signed-URL download in
            the real implementation.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <table className="min-w-full text-left text-sm">
            <thead className="text-xs uppercase tracking-wider text-slate-500">
              <tr>
                <th className="py-2">When (UTC)</th>
                <th className="py-2">Report</th>
                <th className="py-2">Format</th>
                <th className="py-2">Size</th>
                <th className="py-2">By</th>
                <th className="py-2">ID</th>
              </tr>
            </thead>
            <tbody>
              {DEMO.map((r) => (
                <tr key={r.id} className="border-t border-slate-800/80 text-slate-300">
                  <td className="py-2 font-mono text-xs">{r.at}</td>
                  <td className="py-2">{r.report}</td>
                  <td className="py-2 font-mono text-xs uppercase">{r.format}</td>
                  <td className="py-2 font-mono text-xs">{r.size_kb} KB</td>
                  <td className="py-2 text-xs">{r.by}</td>
                  <td className="py-2 font-mono text-xs text-slate-500">{r.id}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </FrameworkPage>
  );
}
