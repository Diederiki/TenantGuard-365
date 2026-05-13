# Threat model

> STRIDE-flavoured threat model for the M365 Enterprise Control Center.
> Reviewed at the end of every phase; updated when new attack surfaces are added.

## Scope

This document covers the **platform** (apps/api, apps/web, apps/worker, infra). Microsoft 365 itself is out of scope — Microsoft is the trust root for tenant data; we are a consumer.

## Assets

| Asset | Sensitivity | Notes |
|-------|-------------|-------|
| Microsoft Graph access tokens (per tenant) | Critical | Encrypted at rest; never in logs or browser. |
| App registration client secrets / certificates | Critical | Secret store only. |
| Technician session cookies | High | HTTP-only, Secure, SameSite=Lax. |
| Mirrored M365 user / group / mailbox / SharePoint data | High | Tenant-scoped, RBAC-gated. |
| Audit events (signins, file access, mailbox activity) | High | Append-only; partitioned. |
| Report exports (CSV/XLSX/PDF/HTML) | High | Stored in MinIO; download audited; checksum verified. |
| Content-search results / snippets | Critical | RBAC + legal gate; raw content not stored by default. |
| Technician audit logs | High | Tamper-evident; offsite shipping in production. |
| Infrastructure secrets (DB password, OS admin) | Critical | Env or secret store; never committed. |

## Trust boundaries

1. **Browser ↔ Caddy** — public internet. TLS termination. Untrusted client by default.
2. **Caddy ↔ apps/web** — same-host docker network.
3. **apps/web ↔ apps/api** — same-host docker network; session cookies relayed.
4. **apps/api ↔ Postgres/Redis/OpenSearch/MinIO** — internal only; never reachable from internet.
5. **apps/worker ↔ Microsoft Graph** — outbound HTTPS only; certificate validation enforced.
6. **Admin operator ↔ host** — SSH only, key auth, jump host where applicable.

## STRIDE

### Spoofing
| Threat | Mitigation |
|--------|-----------|
| Attacker impersonates a technician via stolen cookie. | HTTP-only + Secure + SameSite=Lax; IP/UA fingerprinting; idle + absolute timeout; sign-out on privilege change. |
| Attacker impersonates a tenant in multi-tenant mode. | Tenant ID stamped on every row; queries always scoped server-side; cross-tenant access denied at ORM layer. |
| Phished OIDC code. | PKCE on auth-code flow; state nonce; redirect-URI allow-list. |

### Tampering
| Threat | Mitigation |
|--------|-----------|
| Modification of audit logs. | Append-only at app layer; DB role separation; offsite log shipping. |
| Tampering with remediation in flight. | Approval signs a payload hash; worker verifies the hash before executing. |
| MITM on Graph traffic. | TLS, certificate validation; certificate pinning evaluated for high-risk envs. |
| Container image tamper. | Image digest pinning, signature verification in prod (Phase 10). |

### Repudiation
| Threat | Mitigation |
|--------|-----------|
| Technician denies running a destructive action. | Every action audited with actor, role, timestamp, target, payload hash, IP, UA, correlation ID. |
| Approver denies approval. | Approval row is signed (HMAC over the canonical action payload). |

### Information disclosure
| Threat | Mitigation |
|--------|-----------|
| Bulk export of sensitive data. | Per-export audit; row count and checksum recorded; large exports require reason; download links time-limited. |
| Token leak via logs. | Log scrubber drops `authorization`, `set-cookie`, known token keys, `client_secret`, `code`. |
| Reflected XSS in report names. | Strict CSP, output encoding, sanitiser on Markdown fields. |
| Open S3 / MinIO bucket. | Buckets default to private; presigned URLs only; expiration ≤ 15 minutes. |
| Search query leaks via referer. | `Referrer-Policy: same-origin`. |

### Denial of service
| Threat | Mitigation |
|--------|-----------|
| Abusive Graph polling. | Per-tenant concurrency caps; centralised rate-limit; one shared token bucket per tenant. |
| Cost amplification via huge exports. | Streaming exports with hard row caps and a soft cap that requires confirmation. |
| Worker queue flood. | Per-queue rate limits; dead-letter queues; manual replay only by admins. |
| Slowloris / connection exhaustion. | Caddy connection limits; FastAPI uvicorn worker limits. |

### Elevation of privilege
| Threat | Mitigation |
|--------|-----------|
| User escalates by editing UI to call an admin endpoint. | RBAC enforced server-side on every route. |
| Custom role broadens unexpectedly. | Permission strings are atomic; custom role builder shows the exact set granted; audit on every role change. |
| Worker container compromise reaches API. | Worker has its own DB credentials and Graph token cache reader; API has different ones. |
| Token cache decryption key leaked. | Master key in secret store, not env in prod; key rotation runbook; re-encryption job. |

## Out-of-scope risks (acknowledged but not solved here)

- Compromise of the host OS — managed by the deployment team via OS hardening, patching, EDR.
- Compromise of Microsoft Graph itself — Microsoft's responsibility.
- Physical access to the VPS — DC security and full-disk encryption are the deployer's responsibility.

## Annual review

Re-walk this model at:
- End of every phase
- Before any new module that touches a new Microsoft API
- After any incident, even if no platform code was at fault
