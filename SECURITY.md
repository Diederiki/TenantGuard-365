# Security

> Security model summary. Detailed docs live in `docs/security/`.

## Reporting vulnerabilities

If you discover a security issue:

1. **Do not file a public GitHub issue.**
2. Email the project owner privately or open a private security advisory in this repository.
3. Include reproduction steps, scope, and impact.

For Microsoft 365 tenant-side findings discovered while operating the platform, follow your organisation's incident response process and notify your CISO / security operations lead. Sensitive tenant data must not leave the platform's exports without an approved investigation case.

## Threat model

See [docs/security/threat-model.md](docs/security/threat-model.md).

Headline threats this platform addresses:

| Threat | Mitigation |
|--------|------------|
| Stolen technician session | Short-lived sessions, IP/UA fingerprint logging, RBAC enforced server-side, full audit trail. |
| Over-broad Graph permissions | Per-feature permission documentation, permission gap detector, optional features hidden until consent. |
| Token exfiltration | Token cache encrypted at rest with a key from secret store; tokens never logged; never returned to browser. |
| Bulk data exfiltration | Every export audited (actor, filters, row count, checksum); large exports require reason/comment; rate-limited. |
| Destructive remediation by mistake | Disabled by default; dry-run mode; second-technician approval; per-action rollback notes. |
| Microsoft Graph throttling | Centralised Graph client with 429/`Retry-After` honoured; exponential backoff; per-tenant concurrency caps; cancellation. |
| SQL/XSS/CSRF injection | Parameterised queries (SQLAlchemy), output encoding, strict CSP, SameSite cookies, CSRF token on state-changing routes. |
| Container escape | Non-root containers, minimal base images, read-only root FS where practical, no privileged mode. |
| Supply-chain compromise | Pinned dependencies, dependency scanning in CI, signed images in production (Phase 10). |

## Authentication

See [docs/security/auth-model.md](docs/security/auth-model.md).

- Production: **Entra ID OIDC only.** No local password login in production.
- Optional break-glass local account is opt-in via environment flag and disabled by default. When enabled it requires WebAuthn or TOTP MFA before first use.
- Dev mock auth (`AUTH_MODE=mock`) refuses to start when `ENVIRONMENT=production`.
- Sessions: HTTP-only, Secure, SameSite=Lax cookies; rotated on privilege change; idle timeout enforced server-side.

## Authorization

See [docs/security/rbac.md](docs/security/rbac.md).

- RBAC is enforced on **every** API endpoint via a permission dependency. Frontend hides controls based on the same model but the server is the source of truth.
- Permissions are atomic strings (e.g. `sharepoint.sites.read`, `reports.export`, `remediation.approve`).
- Delegation can scope a role to specific tenants, domains, SharePoint sites, departments, or regions.
- Sensitive permissions (`remediation.execute`, `content_search.run`, `audit.read.raw`) are not assigned to built-in roles by default.

## Audit

See [docs/security/audit-model.md](docs/security/audit-model.md).

Every privileged action produces a record with:

- Actor (user ID + display name)
- Actor role(s) at action time
- Action name
- Target entity (type + ID + label)
- Old value / new value (where safe to record)
- Timestamp (UTC, with millisecond precision)
- IP address
- User agent
- Correlation ID and request ID
- Result (success/failure)
- Failure reason (where applicable)

Audit records are append-only at the application layer. The database enforces this via a row-level policy that denies `UPDATE` and `DELETE` on `technician_audit_logs` except for the platform's audit-rotation job, which runs under a separate role.

## Data classification

| Class | Examples | Storage |
|-------|----------|---------|
| Public | Build metadata, version | Anywhere |
| Internal | Tenant settings, RBAC config | Postgres |
| Sensitive | Mailbox audit events, SharePoint sharing links, user sign-in history | Postgres + OpenSearch with index ACLs |
| Highly sensitive | Content-search results that include personal data, OAuth tokens | Postgres + encrypted columns; tokens only in encrypted token cache; export gated by `content_search.export` permission and second-technician acknowledgement |

Raw mailbox or document content is **not** ingested by default. Content-search runs return metadata and snippets only; full content remains in Microsoft 365.

## Secrets

- All secrets read from environment or a secret store. Never committed.
- `.env.example` is a template only; the real `.env` is git-ignored.
- Tokens, signing keys, and database passwords are never written to logs. The API has a log scrubber that drops known secret keys.
- Container images bake **no** secrets.

## Cryptography

- Token-cache encryption: AES-GCM with a 256-bit data key, sealed by a master key from the secret store. Key rotation is documented in `docs/operations/runbooks.md`.
- Hashing of identifiers used in correlation: BLAKE3 with a per-tenant salt.
- TLS terminates at the reverse proxy (Caddy or Nginx) in production with Let's Encrypt certificates and HSTS.

## Network

- Local dev: services on a private Docker network. Only the web port is published to the host.
- Production: only `:443` and `:80` (for ACME challenge) exposed publicly. Postgres, Redis, OpenSearch, MinIO are bound to the Docker network and never to the public interface.

## Dependency & container hygiene

- Pinned versions (`pyproject.toml` + `package-lock.json`).
- CI dependency scan: planned for Phase 10.
- Containers run as non-root with `USER 10001` (or similar) and `cap_drop: ALL` in production.

## Secure defaults checklist

- [x] No remediation by default
- [x] No password login in production
- [x] No raw content ingestion by default
- [x] HTTPS-only cookies in non-dev environments
- [x] Strict Content-Security-Policy on the web app (Phase 1)
- [x] RBAC enforced server-side
- [x] Audit log append-only
- [x] Token cache encrypted
- [x] All exports audited
