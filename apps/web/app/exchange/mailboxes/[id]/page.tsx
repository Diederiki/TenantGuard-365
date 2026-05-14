import { FrameworkPage } from "../../../../components/layout/FrameworkPage";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../../components/ui/card";

export const dynamic = "force-dynamic";

export default async function ExchangeMailboxDetail({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <FrameworkPage
      module="Exchange Online"
      title={`Mailbox ${id}`}
      subtitle="Per-mailbox detail: size, item count, rules, forwarding, delegates."
      currentPath={`/exchange/mailboxes/${id}`}
      status="framework"
      notes="Live data: GET /users/{id}/mailboxSettings + /users/{id}/messageRules to surface inbox rules. Forwarding rules surface here too."
    >
      <Card>
        <CardHeader>
          <CardTitle>Inbox rules</CardTitle>
          <CardDescription>Forwarding to external addresses is highlighted.</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-slate-500">— framework only —</p>
        </CardContent>
      </Card>
    </FrameworkPage>
  );
}
