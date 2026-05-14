import { FrameworkPage } from "../../../components/layout/FrameworkPage";
import { Badge } from "../../../components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../components/ui/card";

export const dynamic = "force-dynamic";

const MEMBERS = [
  { team: "Engineering", upn: "grace@vendor.example", role: "guest", joined: "2025-11-12" },
  { team: "Marketing", upn: "charlie@partner.example", role: "guest", joined: "2026-02-01" },
  { team: "Finance", upn: "frank.finance@dev.local", role: "owner", joined: "2024-01-08" },
  { team: "Engineering", upn: "erin.engineer@dev.local", role: "owner", joined: "2023-09-22" },
];

export default async function TeamsMembersPage() {
  return (
    <FrameworkPage
      module="Microsoft Teams"
      title="Team members"
      subtitle="Cross-team membership view — easy way to spot one external user spanning multiple teams."
      currentPath="/teams/members"
      status="needs-tenant"
      notes="Live data: /teams/{id}/members per team. Cached for 1 hour."
    >
      <Card>
        <CardHeader>
          <CardTitle>Membership (demo)</CardTitle>
          <CardDescription>Guests highlighted.</CardDescription>
        </CardHeader>
        <CardContent>
          <table className="min-w-full text-left text-sm">
            <thead className="text-xs uppercase tracking-wider text-slate-500">
              <tr>
                <th className="py-2">Team</th>
                <th className="py-2">UPN</th>
                <th className="py-2">Role</th>
                <th className="py-2">Joined</th>
              </tr>
            </thead>
            <tbody>
              {MEMBERS.map((m, i) => (
                <tr key={i} className="border-t border-slate-800/80 text-slate-300">
                  <td className="py-2">{m.team}</td>
                  <td className="py-2 font-mono text-xs">{m.upn}</td>
                  <td className="py-2">
                    <Badge variant={m.role === "guest" ? "attention" : "info"}>{m.role}</Badge>
                  </td>
                  <td className="py-2 font-mono text-xs">{m.joined}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </FrameworkPage>
  );
}
