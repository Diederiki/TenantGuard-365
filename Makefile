# =============================================================================
# M365 Enterprise Control Center — task runner
# Most developer commands live here. Mirror in scripts/ for CI.
# =============================================================================

SHELL := /bin/bash
COMPOSE := docker compose

.PHONY: help
help:
	@echo "Targets:"
	@echo "  make up            # start infra services (postgres, redis, opensearch, minio, mailhog)"
	@echo "  make up-app        # start app services too (api, web, worker) — Phase 1+"
	@echo "  make ps            # list services"
	@echo "  make logs          # tail logs"
	@echo "  make down          # stop services (keep volumes)"
	@echo "  make nuke          # stop services AND wipe volumes (DESTRUCTIVE)"
	@echo "  make psql          # psql shell into Postgres"
	@echo "  make redis-cli     # redis-cli into Redis"
	@echo "  make os-health     # OpenSearch cluster health"
	@echo "  make minio-console # open MinIO console URL"
	@echo "  make mailhog       # open Mailhog UI URL"

.PHONY: up
up:
	$(COMPOSE) up -d postgres redis opensearch minio mailhog

.PHONY: up-app
up-app:
	$(COMPOSE) --profile app up -d

.PHONY: ps
ps:
	$(COMPOSE) ps

.PHONY: logs
logs:
	$(COMPOSE) logs -f --tail=200

.PHONY: down
down:
	$(COMPOSE) down

.PHONY: nuke
nuke:
	@echo "This wipes ALL local data (postgres, redis, opensearch, minio)."
	@read -p "Type 'WIPE' to confirm: " ans && [ "$$ans" = "WIPE" ]
	$(COMPOSE) down -v

.PHONY: psql
psql:
	$(COMPOSE) exec postgres psql -U $${POSTGRES_USER:-tg365} -d $${POSTGRES_DB:-tg365}

.PHONY: redis-cli
redis-cli:
	$(COMPOSE) exec redis redis-cli

.PHONY: os-health
os-health:
	curl -fsS http://localhost:9200/_cluster/health | jq .

.PHONY: minio-console
minio-console:
	@echo "MinIO console: http://localhost:9001"

.PHONY: mailhog
mailhog:
	@echo "Mailhog UI:    http://localhost:8025"
