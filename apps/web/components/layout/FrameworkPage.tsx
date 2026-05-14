import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { ReactNode } from "react";

import { AppShell } from "./AppShell";
import { Badge, BadgeVariant } from "../ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../ui/card";
import { fetchMe } from "../../lib/api";

export type FrameworkStatus =
  | "mock-only"
  | "framework"
  | "needs-tenant"
  | "needs-purview"
  | "needs-defender"
  | "real";

const STATUS_LABEL: Record<FrameworkStatus, { label: string; variant: BadgeVariant }> = {
  "mock-only": { label: "mock-only", variant: "info" },
  framework: { label: "framework", variant: "muted" },
  "needs-tenant": { label: "needs tenant creds", variant: "attention" },
  "needs-purview": { label: "needs Purview licence", variant: "attention" },
  "needs-defender": { label: "needs Defender licence", variant: "attention" },
  real: { label: "live", variant: "info" },
};

/**
 * Shared shell for the many pages that are framework / stub today. Renders
 * the standard AppShell with header, status chip, and a body section that
 * the caller fills. Adds an auth check + redirect to /sign-in for unauth
 * users so we don't have to repeat that boilerplate 30 times.
 */
export async function FrameworkPage({
  module,
  title,
  subtitle,
  currentPath,
  status,
  notes,
  permission,
  children,
}: {
  module: string;
  title: string;
  subtitle: string;
  currentPath: string;
  status: FrameworkStatus;
  notes?: ReactNode;
  /** Permission key the user must hold to view this page. */
  permission?: string;
  children?: ReactNode;
}) {
  const cookie = (await headers()).get("cookie") ?? "";
  const me = await fetchMe(cookie);
  if (!me) redirect("/sign-in");
  if (permission && !me.permissions.includes(permission)) {
    return (
      <AppShell me={me} currentPath={currentPath}>
        <main className="px-6 py-8">
          <Card>
            <CardHeader>
              <CardTitle>Forbidden</CardTitle>
              <CardDescription>
                You don&apos;t have the <code className="font-mono">{permission}</code>{" "}
                permission required to view this page. Ask a platform admin to
                grant it.
              </CardDescription>
            </CardHeader>
          </Card>
        </main>
      </AppShell>
    );
  }
  const s = STATUS_LABEL[status];
  return (
    <AppShell me={me} currentPath={currentPath}>
      <main className="px-6 py-8">
        <header className="mb-6 flex items-end justify-between">
          <div>
            <p className="mb-1 text-xs font-medium uppercase tracking-widest text-brand-400">
              {module}
            </p>
            <h1 className="text-3xl font-semibold tracking-tight text-slate-50">
              {title}
            </h1>
            <p className="mt-1 max-w-3xl text-sm text-slate-400">{subtitle}</p>
          </div>
          <Badge variant={s.variant}>{s.label}</Badge>
        </header>

        {notes ? (
          <Card className="mb-4">
            <CardContent>
              <div className="text-sm text-slate-300">{notes}</div>
            </CardContent>
          </Card>
        ) : null}

        {children}
      </main>
    </AppShell>
  );
}
