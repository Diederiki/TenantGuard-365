# Local development

## Requirements

- Windows 11, macOS, or Linux
- Docker Desktop / Engine **24+** with Compose v2
- 8 GB RAM free for containers (OpenSearch needs ~1.5 GB)
- 20 GB free disk for volumes
- Git
- A Microsoft 365 tenant where you have **Global Administrator** (only needed for Phase 3+; not required for Phase 0/1)

## Bootstrap (Phase 0 — infra only)

```bash
git clone https://github.com/Diederiki/TenantGuard-365.git
cd TenantGuard-365
cp .env.example .env
# Edit .env — change DEV_SESSION_SECRET, POSTGRES_PASSWORD, MINIO_ROOT_PASSWORD,
# and TOKEN_CACHE_MASTER_KEY before doing anything beyond first-run smoke test.
```

Bring up infrastructure:

```bash
docker compose up -d postgres redis opensearch minio mailhog
docker compose ps
```

Expected:

```
NAME              STATUS                  PORTS
tg365-postgres    Up (healthy)            127.0.0.1:5432->5432/tcp
tg365-redis       Up (healthy)            127.0.0.1:6379->6379/tcp
tg365-opensearch  Up (healthy)            127.0.0.1:9200->9200/tcp
tg365-minio       Up (healthy)            127.0.0.1:9000->9000/tcp, 9001->9001/tcp
tg365-mailhog     Up                      127.0.0.1:1025->1025/tcp, 8025->8025/tcp
```

Smoke tests:

```bash
curl -fsS http://localhost:9200/_cluster/health | jq .status
docker compose exec redis redis-cli ping
docker compose exec postgres psql -U tg365 -d tg365 -c "select version();"
curl -fsS http://localhost:9000/minio/health/live
open http://localhost:8025      # Mailhog UI (or just browse)
```

If any container is unhealthy, see [Troubleshooting](#troubleshooting).

## Phase 0 app placeholders

`docker compose up -d` with the `app` profile starts placeholder `api`/`web`/`worker` containers that print a banner and sleep. They exist so `docker compose config` validates and so you can confirm the network topology.

```bash
docker compose --profile app up -d
docker compose logs api web worker --tail=5
```

In Phase 1 these are replaced with real FastAPI / Next.js / worker images.

## Filesystem layout you should expect

```
TenantGuard-365/
├── apps/
│   ├── api/        Phase 1: FastAPI service
│   ├── web/        Phase 1: Next.js app
│   └── worker/     Phase 1: Celery/Dramatiq workers
├── packages/
│   ├── shared-types/   shared TS/Python types
│   └── ui/             shared web components
├── infra/
│   ├── caddy/      production reverse proxy
│   ├── nginx/      alternative reverse proxy
│   ├── postgres/   init scripts
│   └── scripts/    operational helpers
├── docs/           you are here
├── tests/          unit / integration / e2e / security / load
├── docker-compose.yml         dev
├── docker-compose.prod.yml    prod overlay
├── .env.example
├── Makefile
└── README.md
```

## Useful Make targets

| Command | What |
|---------|------|
| `make up` | start infra (postgres, redis, opensearch, minio, mailhog) |
| `make up-app` | also start app placeholders |
| `make ps` | list services |
| `make logs` | tail logs |
| `make down` | stop services (keep volumes) |
| `make nuke` | stop AND wipe all data volumes — destructive |
| `make psql` | `psql` shell into Postgres |
| `make redis-cli` | redis-cli into Redis |
| `make os-health` | OpenSearch cluster health |

## Troubleshooting

### OpenSearch fails with `vm.max_map_count` error (Linux)

```bash
sudo sysctl -w vm.max_map_count=262144
echo "vm.max_map_count=262144" | sudo tee /etc/sysctl.d/99-opensearch.conf
```

On Docker Desktop (Windows/macOS) the VM is usually pre-configured.

### Postgres won't come up

- Check that port 5432 isn't already bound by a local install.
- Re-create the volume: `docker compose down -v && docker compose up -d postgres`.

### MinIO console "default password" prompt

That means you didn't change `MINIO_ROOT_PASSWORD` in `.env`. Change it, then `docker compose up -d --force-recreate minio`.

### Mailhog isn't catching mail

- Confirm `SMTP_HOST=mailhog` and `SMTP_PORT=1025` in `.env`.
- Open http://localhost:8025 to see captured mail.

### Slow on Windows

Use WSL2 with Docker Desktop's WSL integration. Mount the repo from a Linux filesystem (e.g. `~/code/TenantGuard-365`), not from `/mnt/c/...`.

## Resetting everything

```bash
make nuke   # asks for confirmation; wipes all volumes
```

Then re-bootstrap.
