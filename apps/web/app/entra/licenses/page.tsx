import { FrameworkPage } from "../../../components/layout/FrameworkPage";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../components/ui/card";

export const dynamic = "force-dynamic";

const LICS = [
  { sku: "Microsoft 365 E5", purchased: 50, consumed: 47 },
  { sku: "Microsoft 365 E3", purchased: 200, consumed: 188 },
  { sku: "Microsoft Defender for Office 365 P2", purchased: 50, consumed: 47 },
  { sku: "Purview Insider Risk Management", purchased: 25, consumed: 4 },
  { sku: "Power BI Pro", purchased: 60, consumed: 33 },
];

export default async function EntraLicensesPage() {
  return (
    <FrameworkPage
      module="Entra ID"
      title="Licenses"
      subtitle="Consumed vs purchased per SKU. Spot under- and over-provisioning fast."
      currentPath="/entra/licenses"
      status="needs-tenant"
      notes="Live data from Graph /subscribedSkus."
    >
      <Card>
        <CardHeader>
          <CardTitle>SKU usage (demo)</CardTitle>
          <CardDescription>Bar shows utilisation %.</CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="space-y-3">
            {LICS.map((l) => {
              const pct = Math.round((l.consumed / l.purchased) * 100);
              const bar = pct > 95 ? "bg-rose-500" : pct > 80 ? "bg-amber-500" : "bg-emerald-500";
              return (
                <li key={l.sku}>
                  <div className="mb-1 flex items-center justify-between">
                    <span className="text-sm text-slate-200">{l.sku}</span>
                    <span className="font-mono text-xs text-slate-400">
                      {l.consumed} / {l.purchased} ({pct}%)
                    </span>
                  </div>
                  <div className="h-2 w-full overflow-hidden rounded-full bg-slate-800">
                    <div className={`${bar} h-full`} style={{ width: `${pct}%` }} />
                  </div>
                </li>
              );
            })}
          </ul>
        </CardContent>
      </Card>
    </FrameworkPage>
  );
}
