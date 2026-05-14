import { headers } from "next/headers";
import { redirect } from "next/navigation";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../components/ui/card";
import { fetchAudit, fetchMe } from "../../lib/api";
import { AuditGrid } from "./AuditGrid";

export const dynamic = "force-dynamic";

export default async function AuditPage({
  searchParams,
}: {
  searchParams: Promise<{ before_id?: string }>;
}) {
  const cookieHeader = (await headers()).get("cookie") ?? "";
  const me = await fetchMe(cookieHeader);
  if (!me) redirect("/sign-in");

  const params = await searchParams;
  const beforeId = params.before_id ? Number(params.before_id) : undefined;
  const page = await fetchAudit(cookieHeader, { beforeId });

  return (
    <main className="mx-auto max-w-6xl px-6 py-12">
      <header className="mb-8 flex items-end justify-between">
        <div>
          <p className="mb-1 text-xs font-medium uppercase tracking-widest text-brand-400">
            Audit
          </p>
          <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
            Technician audit log
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Append-only. Every privileged action shows up here, server-side.
          </p>
        </div>
        <a href="/" className="text-sm text-brand-400 hover:underline">
          ← Back to overview
        </a>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>Latest entries</CardTitle>
          <CardDescription>
            Newest first. Cursor-paginated by record id.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {"error" in page ? (
            <p className="text-sm text-rose-300">Failed to load: {page.error}</p>
          ) : page.items.length === 0 ? (
            <p className="text-sm text-slate-500">No audit entries yet.</p>
          ) : (
            <AuditGrid rows={page.items} nextCursor={page.next_cursor ?? null} />
          )}
        </CardContent>
      </Card>
    </main>
  );
}
