# Production VPS deployment

> Target: **Ubuntu 24.04 LTS** on a VPS sized for a single tenant.
> Phase 10 finalises this; here is the planned shape so we can keep the architecture aligned.

## Recommended sizing (single tenant)

| Tenant size (M365 users) | vCPU | RAM | Disk |
|--------------------------|------|-----|------|
| < 500 | 2 | 8 GB | 100 GB SSD |
| 500 – 5 000 | 4 | 16 GB | 250 GB SSD |
| 5 000 – 50 000 | 8 | 32 GB | 500 GB SSD + OpenSearch on its own volume |

OpenSearch is almost always the constraint. If you cross 50 000 mailboxes you should plan for a small dedicated OpenSearch host.

## Hostname & DNS

- Pick `m365cc.<your-domain>` or similar.
- Point an A/AAAA record at the VPS public IP.
- Optional second name for the MinIO endpoint (only needed if you expose exports externally — not recommended).

## Host preparation

```bash
sudo apt update && sudo apt -y full-upgrade
sudo apt -y install ca-certificates curl gnupg ufw fail2ban unattended-upgrades

# Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
sudo apt update
sudo apt -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Service account
sudo useradd -m -s /bin/bash tg365
sudo usermod -aG docker tg365

# Firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 443/udp           # HTTP/3 via Caddy
sudo ufw --force enable

# Kernel for OpenSearch
echo "vm.max_map_count=262144" | sudo tee /etc/sysctl.d/99-opensearch.conf
sudo sysctl --system

# Unattended upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

## Filesystem layout

```
/opt/tg365/
├── repo/                    # git clone target
├── env/.env                 # secret-store mount, 0640 root:tg365
├── data/
│   ├── postgres/
│   ├── redis/
│   ├── opensearch/
│   └── minio/
├── caddy/
│   ├── Caddyfile
│   └── data/                # ACME state
└── backups/
    ├── postgres/
    ├── opensearch-snapshots/
    └── minio/
```

Mount `data/` on a separate disk if possible. Snapshot daily.

## Compose deployment

```bash
sudo -u tg365 -i
cd /opt/tg365
git clone https://github.com/Diederiki/TenantGuard-365.git repo
cd repo

# Place .env from secret store (do NOT use .env.example values in prod)
ln -s /opt/tg365/env/.env .env

# Bring up
docker compose -f docker-compose.yml -f docker-compose.prod.yml pull
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

docker compose ps
```

## Caddy reverse proxy

`infra/caddy/Caddyfile`:

```caddy
m365cc.example.com {
    encode zstd gzip

    handle /api/* {
        reverse_proxy api:8000 {
            header_up X-Forwarded-Host {host}
            header_up X-Real-IP {remote_host}
        }
    }

    handle /auth/* {
        reverse_proxy api:8000
    }

    handle {
        reverse_proxy web:3000
    }

    header {
        Strict-Transport-Security "max-age=63072000; includeSubDomains; preload"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "DENY"
        Referrer-Policy "same-origin"
    }
}
```

ACME (Let's Encrypt) certificates are obtained automatically by Caddy.

## TLS posture

- HTTPS only (Caddy enforces redirect from `:80`).
- HSTS preload header set.
- TLS ≥ 1.2; modern cipher suites (Caddy default).
- HTTP/3 enabled on UDP 443.

## Secrets in production

**Never** keep the real `.env` in the git checkout. Options, in order of preference:

1. Mount from an external secret store (Vault Agent, sops + age, doppler-cli) into `/opt/tg365/env/.env` with mode 0640.
2. Use Docker Compose secrets (`secrets:` block) for `.env`-style values that don't change. Less flexible.

Required production-only values:

- Strong random `DEV_SESSION_SECRET` (renamed to `SESSION_SECRET` in prod; treat the env name as legacy).
- Strong random `TOKEN_CACHE_MASTER_KEY`.
- `POSTGRES_PASSWORD`, `MINIO_ROOT_PASSWORD`, `OPENSEARCH_ADMIN_PASSWORD`.
- `ENTRA_CLIENT_ID`, `ENTRA_TENANT_ID`, `ENTRA_CLIENT_SECRET` (or certificate path).
- `COLLECTOR_CLIENT_ID`, `COLLECTOR_TENANT_ID`, `COLLECTOR_CLIENT_SECRET` or cert.
- Real SMTP credentials.

## Backups

See [docs/operations/backup-restore.md](../operations/backup-restore.md). Summary:

- Postgres: nightly `pg_dump` + WAL archive to off-host storage.
- OpenSearch: daily snapshot to MinIO bucket; replicate MinIO off-host.
- MinIO: `mc mirror` to an off-host S3 endpoint with object-lock.

## Monitoring

See [docs/operations/monitoring.md](../operations/monitoring.md). Summary:

- Containers ship logs to journald and (optionally) to a remote syslog/SIEM.
- Prometheus scraping is wired in Phase 10.
- Alerting on: container down, DB connection failures, Graph error rate, audit-shipper backlog.

## Upgrades

1. Read `CHANGELOG.md`.
2. `git fetch && git checkout <tag>`.
3. `docker compose pull`.
4. Backup: trigger an extra Postgres dump + MinIO mirror.
5. `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d`.
6. Apply migrations: `docker compose exec api alembic upgrade head`.
7. Run smoke checks (`/healthz`, `/readyz`, sample report).

## Rollback

- Container images are pinned by digest in `docker-compose.prod.yml`. Roll back by reverting the digest and `docker compose up -d`.
- DB migrations should be backwards-compatible across one release window. If a destructive migration is required, the release notes will say so explicitly; restore from backup is the rollback path.

## Production security checklist (Phase 10 sign-off)

- [ ] HTTPS only with HSTS preload
- [ ] No ports exposed publicly except 80/443
- [ ] Containers run non-root, read-only root FS, no privileged mode
- [ ] All secrets from secret store, none from env files committed
- [ ] Backups verified by quarterly restore drill
- [ ] Audit log shipping to immutable sink
- [ ] Conditional Access policy scoped to portal app
- [ ] Patch cadence documented; unattended-upgrades active
- [ ] EDR or equivalent on the host
- [ ] Disaster recovery drill executed and documented
