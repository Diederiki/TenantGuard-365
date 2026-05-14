import { FrameworkPage } from "../../../components/layout/FrameworkPage";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../components/ui/card";

export const dynamic = "force-dynamic";

const MB = [
  { id: "u-001", upn: "alice.admin@dev.local", size_gb: 3.4, item_count: 18233, archive: true, forwarding: false },
  { id: "u-002", upn: "bob.analyst@dev.local", size_gb: 1.9, item_count: 11050, archive: false, forwarding: false },
  { id: "u-006", upn: "frank.finance@dev.local", size_gb: 7.7, item_count: 42180, archive: true, forwarding: true },
  { id: "u-010", upn: "john.jansen@dev.local", size_gb: 18.2, item_count: 91220, archive: true, forwarding: false },
];

export default async function ExchangeMailboxesPage() {
  return (
    <FrameworkPage
      module="Exchange Online"
      title="Mailboxes"
      subtitle="Inventory of user mailboxes — size, item count, archive + forwarding flags."
      currentPath="/exchange/mailboxes"
      status="needs-tenant"
      notes="Live data from Graph /users/{id}/mailboxSettings + /reports/getMailboxUsageDetail."
    >
      <Card>
        <CardHeader>
          <CardTitle>Mailboxes (demo)</CardTitle>
          <CardDescription>Click an entry to drill into mailbox detail.</CardDescription>
        </CardHeader>
        <CardContent>
          <table className="min-w-full text-left text-sm">
            <thead className="text-xs uppercase tracking-wider text-slate-500">
              <tr>
                <th className="py-2">UPN</th>
                <th className="py-2">Size</th>
                <th className="py-2">Items</th>
                <th className="py-2">Archive</th>
                <th className="py-2">Forwarding</th>
              </tr>
            </thead>
            <tbody>
              {MB.map((m) => (
                <tr key={m.id} className="border-t border-slate-800/80 text-slate-300">
                  <td className="py-2">
                    <a className="text-brand-400 hover:underline" href={`/exchange/mailboxes/${m.id}`}>
                      {m.upn}
                    </a>
                  </td>
                  <td className="py-2 font-mono">{m.size_gb} GB</td>
                  <td className="py-2 font-mono">{m.item_count.toLocaleString()}</td>
                  <td className="py-2 text-xs">{m.archive ? "yes" : "no"}</td>
                  <td className="py-2 text-xs">{m.forwarding ? "external" : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </FrameworkPage>
  );
}
