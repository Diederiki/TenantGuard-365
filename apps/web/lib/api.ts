/**
 * Small fetch wrapper for talking to the API.
 *
 * Browser-side calls hit the API through the Next.js host (proxied or same
 * origin in prod). For server components we use the in-cluster URL.
 */

export function apiBaseUrl(opts?: { serverSide?: boolean }): string {
  if (opts?.serverSide) {
    return process.env.API_INTERNAL_URL ?? "http://api:8000";
  }
  return process.env.NEXT_PUBLIC_API_URL ?? "";
}

export type MeResponse = {
  id: string;
  email: string;
  display_name: string;
  is_active: boolean;
  role_keys: string[];
  permissions: string[];
};

export type AuditEntry = {
  id: number;
  tenant_id: string | null;
  actor_id: string | null;
  actor_display: string;
  actor_type: string;
  action: string;
  target_type: string | null;
  target_id: string | null;
  target_label: string | null;
  result: string;
  event_time: string;
};

export type AuditPage = {
  items: AuditEntry[];
  next_cursor: number | null;
};

export async function fetchMe(cookieHeader: string): Promise<MeResponse | null> {
  // Demo mode short-circuit so the whole app is browsable without an API.
  // Lazy import to keep this module client/server safe.
  if (/(?:^|; )tg365_demo=1\b/.test(cookieHeader)) {
    const { DEMO_ME } = await import("./demoData");
    return DEMO_ME;
  }
  const base = apiBaseUrl({ serverSide: true });
  try {
    const r = await fetch(`${base}/api/me`, {
      headers: { cookie: cookieHeader },
      cache: "no-store",
    });
    if (r.status === 401) return null;
    if (!r.ok) throw new Error(`/api/me ${r.status}`);
    return (await r.json()) as MeResponse;
  } catch {
    return null;
  }
}

export async function fetchAudit(
  cookieHeader: string,
  opts: { limit?: number; beforeId?: number } = {},
): Promise<AuditPage | { error: string }> {
  if (/(?:^|; )tg365_demo=1\b/.test(cookieHeader)) {
    const { DEMO_AUDIT } = await import("./demoData");
    return DEMO_AUDIT;
  }
  const base = apiBaseUrl({ serverSide: true });
  const params = new URLSearchParams();
  params.set("limit", String(opts.limit ?? 50));
  if (opts.beforeId) params.set("before_id", String(opts.beforeId));
  const r = await fetch(`${base}/api/audit?${params}`, {
    headers: { cookie: cookieHeader },
    cache: "no-store",
  });
  if (!r.ok) return { error: `${r.status}` };
  return (await r.json()) as AuditPage;
}

export function csrfHeader(): Record<string, string> {
  if (typeof document === "undefined") return {};
  const match = document.cookie.match(/(?:^|; )tg365_csrf=([^;]+)/);
  return match ? { "X-CSRF-Token": decodeURIComponent(match[1]) } : {};
}
