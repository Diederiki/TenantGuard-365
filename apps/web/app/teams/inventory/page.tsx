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

const TEAMS = [
  { id: "t-1", name: "Finance", owners: 2, members: 12, guests: 0, channels: 4, last_activity: "2026-05-13", visibility: "private" },
  { id: "t-2", name: "Engineering", owners: 3, members: 24, guests: 2, channels: 9, last_activity: "2026-05-13", visibility: "private" },
  { id: "t-3", name: "Marketing", owners: 1, members: 7, guests: 1, channels: 5, last_activity: "2026-05-11", visibility: "public" },
  { id: "t-4", name: "All Hands", owners: 1, members: 132, guests: 0, channels: 1, last_activity: "2026-05-10", visibility: "private" },
];

export default async function TeamsInventoryPage() {
  return (
    <FrameworkPage
      module="Microsoft Teams"
      title="Team inventory"
      subtitle="All Teams with member + guest counts, channel counts, last activity."
      currentPath="/teams/inventory"
      status="needs-tenant"
      notes="Live data from Graph /teams + /teams/{id}/members."
    >
      <Card>
        <CardHeader>
          <CardTitle>Teams (demo)</CardTitle>
          <CardDescription>Public teams flagged for review.</CardDescription>
        </CardHeader>
        <CardContent>
          <table className="min-w-full text-left text-sm">
            <thead className="text-xs uppercase tracking-wider text-slate-500">
              <tr>
                <th className="py-2">Team</th>
                <th className="py-2">Visibility</th>
                <th className="py-2">Owners</th>
                <th className="py-2">Members</th>
                <th className="py-2">Guests</th>
                <th className="py-2">Channels</th>
                <th className="py-2">Last activity</th>
              </tr>
            </thead>
            <tbody>
              {TEAMS.map((t) => (
                <tr key={t.id} className="border-t border-slate-800/80 text-slate-300">
                  <td className="py-2">{t.name}</td>
                  <td className="py-2">
                    <Badge variant={t.visibility === "public" ? "attention" : "info"}>
                      {t.visibility}
                    </Badge>
                  </td>
                  <td className="py-2 font-mono">{t.owners}</td>
                  <td className="py-2 font-mono">{t.members}</td>
                  <td className="py-2 font-mono">{t.guests}</td>
                  <td className="py-2 font-mono">{t.channels}</td>
                  <td className="py-2 font-mono text-xs">{t.last_activity}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </FrameworkPage>
  );
}
