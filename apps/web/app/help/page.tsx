import { FrameworkPage } from "../../components/layout/FrameworkPage";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../components/ui/card";

export const dynamic = "force-dynamic";

const DOCS: { href: string; title: string; desc: string }[] = [
  {
    href: "https://github.com/Diederiki/TenantGuard-365/blob/main/README.md",
    title: "README",
    desc: "Project overview, local dev quickstart, the high-level architecture diagram.",
  },
  {
    href: "https://github.com/Diederiki/TenantGuard-365/blob/main/docs/operations/full-platform-verification-report.md",
    title: "Verification report",
    desc: "Latest autonomous-run audit. What works, what's pending, production-readiness score.",
  },
  {
    href: "https://github.com/Diederiki/TenantGuard-365/blob/main/docs/security/vulnerability-analysis.md",
    title: "Vulnerability analysis",
    desc: "Running internal-security review with status per finding.",
  },
  {
    href: "https://github.com/Diederiki/TenantGuard-365/blob/main/docs/operations/performance-efficiency-analysis.md",
    title: "Performance & efficiency",
    desc: "Hot spots and headline wins. Refreshed each phase.",
  },
  {
    href: "https://github.com/Diederiki/TenantGuard-365/blob/main/docs/microsoft-graph/capability-matrix.md",
    title: "Graph capability matrix",
    desc: "Which Microsoft API every feature uses and what licence it needs.",
  },
  {
    href: "https://github.com/Diederiki/TenantGuard-365/blob/main/docs/microsoft-graph/required-permissions.md",
    title: "Required permissions",
    desc: "Per-collector minimum scopes. Use these in the app registration.",
  },
  {
    href: "https://github.com/Diederiki/TenantGuard-365/blob/main/docs/admin/user-management.md",
    title: "Admin: user management",
    desc: "Auth methods, creating users, enrolling TOTP, disabling accounts.",
  },
  {
    href: "https://github.com/Diederiki/TenantGuard-365/blob/main/docs/admin/settings.md",
    title: "Admin: settings",
    desc: "Tour of every settings card and what env var maps to it.",
  },
  {
    href: "https://github.com/Diederiki/TenantGuard-365/blob/main/docs/admin/rbac.md",
    title: "Admin: RBAC",
    desc: "Built-in roles, custom roles, scope expression syntax.",
  },
  {
    href: "https://github.com/Diederiki/TenantGuard-365/blob/main/docs/operations/runbook.md",
    title: "Operations runbook",
    desc: "Day-2 playbook. Backup, restore, scaling, incident handling.",
  },
];

export default async function HelpPage() {
  return (
    <FrameworkPage
      module="Help"
      title="Documentation"
      subtitle="In-app index of the docs that ship with this repo. Every link below points at the source-controlled markdown."
      currentPath="/help"
      status="real"
    >
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        {DOCS.map((d) => (
          <a
            key={d.href}
            href={d.href}
            target="_blank"
            rel="noopener noreferrer"
            className="block"
          >
            <Card className="h-full hover:border-brand-700">
              <CardHeader>
                <CardTitle>{d.title}</CardTitle>
                <CardDescription>{d.desc}</CardDescription>
              </CardHeader>
              <CardContent>
                <span className="text-xs text-brand-400">Open ↗</span>
              </CardContent>
            </Card>
          </a>
        ))}
      </div>
    </FrameworkPage>
  );
}
