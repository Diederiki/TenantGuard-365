import { FrameworkPage } from "../../../../components/layout/FrameworkPage";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../../components/ui/card";
import { Badge } from "../../../../components/ui/badge";
import { DEMO_ENTRA_USERS } from "../../../../lib/demoData";

export const dynamic = "force-dynamic";

export default async function EntraUserDetail({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const user = DEMO_ENTRA_USERS.find((u) => u.id === id) ?? null;

  return (
    <FrameworkPage
      module="Entra ID"
      title={user ? user.display_name : "User detail"}
      subtitle={
        user ? user.user_principal_name : "No user with that ID in the demo set."
      }
      currentPath={`/entra/users/${id}`}
      status="mock-only"
      notes="Live data from Graph /users/{id} once the entra.users collector has run. Adds last sign-in, group memberships, license assignments, MFA status."
    >
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Profile</CardTitle>
            <CardDescription>Top-level directory attributes.</CardDescription>
          </CardHeader>
          <CardContent>
            {user ? (
              <dl className="space-y-1 text-sm">
                <dt className="text-xs uppercase tracking-wider text-slate-500">Display name</dt>
                <dd className="text-slate-100">{user.display_name}</dd>
                <dt className="text-xs uppercase tracking-wider text-slate-500">UPN</dt>
                <dd className="font-mono text-xs text-slate-300">{user.user_principal_name}</dd>
                <dt className="text-xs uppercase tracking-wider text-slate-500">Email</dt>
                <dd className="text-slate-300">{user.mail ?? "—"}</dd>
                <dt className="text-xs uppercase tracking-wider text-slate-500">Type</dt>
                <dd>
                  <Badge variant={user.user_type === "Guest" ? "attention" : "info"}>
                    {user.user_type}
                  </Badge>
                </dd>
                <dt className="text-xs uppercase tracking-wider text-slate-500">Account</dt>
                <dd>
                  <Badge variant={user.account_enabled ? "info" : "critical"}>
                    {user.account_enabled ? "enabled" : "disabled"}
                  </Badge>
                </dd>
                <dt className="text-xs uppercase tracking-wider text-slate-500">Department / Title</dt>
                <dd className="text-slate-300">
                  {user.department ?? "—"} / {user.job_title ?? "—"}
                </dd>
                <dt className="text-xs uppercase tracking-wider text-slate-500">Office</dt>
                <dd className="text-slate-300">{user.office_location ?? "—"}</dd>
                <dt className="text-xs uppercase tracking-wider text-slate-500">Last sign-in</dt>
                <dd className="font-mono text-xs text-slate-300">{user.last_signin_at ?? "—"}</dd>
              </dl>
            ) : (
              <p className="text-sm text-slate-500">User not found in the demo set.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Group memberships</CardTitle>
            <CardDescription>
              Direct + transitive. Live data needs Graph /users/{id}/transitiveMemberOf.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-slate-500">— framework only —</p>
          </CardContent>
        </Card>
      </div>
    </FrameworkPage>
  );
}
