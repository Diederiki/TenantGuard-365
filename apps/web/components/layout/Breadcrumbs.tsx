import Link from "next/link";

const LABELS: Record<string, string> = {
  "": "Overview",
  audit: "Audit log",
  reports: "Reports",
  scheduled: "Scheduled",
  entra: "Entra ID",
  sharepoint: "SharePoint",
  onedrive: "OneDrive",
  exchange: "Exchange",
  teams: "Teams",
  "service-health": "Service health",
  security: "Security",
  alerts: "Alerts",
  rules: "Rules",
  investigations: "Investigations",
  "content-search": "Content search",
  remediation: "Remediation",
  jobs: "Sync jobs",
  delegation: "Delegation",
  settings: "Settings",
  graph: "Graph connection",
};

export function Breadcrumbs({ path }: { path: string }) {
  const parts = path.split("/").filter(Boolean);
  const trail: { href: string; label: string }[] = [
    { href: "/", label: "Overview" },
  ];
  let acc = "";
  for (const p of parts) {
    acc += `/${p}`;
    trail.push({ href: acc, label: LABELS[p] ?? p });
  }
  return (
    <nav className="text-xs text-slate-500" aria-label="Breadcrumb">
      {trail.map((t, i) => (
        <span key={t.href}>
          {i > 0 ? <span className="mx-1 text-slate-700">/</span> : null}
          {i === trail.length - 1 ? (
            <span className="text-slate-300">{t.label}</span>
          ) : (
            <Link className="hover:text-slate-300" href={t.href}>
              {t.label}
            </Link>
          )}
        </span>
      ))}
    </nav>
  );
}
