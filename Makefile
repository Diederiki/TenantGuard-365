# =============================================================================
# M365 Enterprise Control Center — task runner
# =============================================================================

SHELL := /bin/bash
COMPOSE := docker compose

.PHONY: help
help:
	@echo "Targets:"
	@echo "  make up            Start full stack (infra + api + web + worker)"
	@echo "  make up-infra      Start infra services only"
	@echo "  make ps            List services"
	@echo "  make logs          Tail logs"
	@echo "  make down          Stop services (keep volumes)"
	@echo "  make nuke          Stop AND wipe all data volumes (DESTRUCTIVE)"
	@echo "  make migrate       Run Alembic migrations to head"
	@echo "  make revision m='msg'  Create a new Alembic revision"
	@echo "  make seed          Seed local-dev tenant, roles, admin"
	@echo "  make bootstrap     migrate + seed in one shot"
	@echo "  make psql          psql shell into Postgres"
	@echo "  make redis-cli     redis-cli into Redis"
	@echo "  make os-health     OpenSearch cluster health"
	@echo "  make test          Run all unit tests inside containers"
	@echo "  make test-api      Run api tests"
	@echo "  make test-worker   Run worker tests"
	@echo "  make lint          Lint api + worker + web"
	@echo "  make fmt           Format api + worker (ruff)"
	@echo "  make typecheck     mypy (api+worker) + tsc (web)"

.PHONY: up
up:
	$(COMPOSE) up -d

.PHONY: up-infra
up-infra:
	$(COMPOSE) up -d postgres redis opensearch minio mailhog

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

.PHONY: migrate
migrate:
	$(COMPOSE) exec -T api alembic upgrade head

.PHONY: revision
revision:
	@test -n "$(m)" || (echo "Usage: make revision m='message'"; exit 1)
	$(COMPOSE) exec -T api alembic revision --autogenerate -m "$(m)"

.PHONY: seed
seed:
	$(COMPOSE) exec -T api python -m app.scripts.seed

.PHONY: bootstrap
bootstrap: up migrate seed

.PHONY: psql
psql:
	$(COMPOSE) exec postgres psql -U $${POSTGRES_USER:-tg365} -d $${POSTGRES_DB:-tg365}

.PHONY: redis-cli
redis-cli:
	$(COMPOSE) exec redis redis-cli

.PHONY: os-health
os-health:
	curl -fsS http://localhost:9200/_cluster/health | jq .

.PHONY: test
test: test-api test-worker

.PHONY: test-api
test-api:
	$(COMPOSE) exec -T api sh -c 'pip install -q -r requirements-dev.txt && pytest -q'

.PHONY: test-worker
test-worker:
	$(COMPOSE) exec -T worker sh -c 'pip install -q -r requirements-dev.txt && pytest -q'

.PHONY: lint
lint:
	$(COMPOSE) exec -T api sh -c 'pip install -q ruff==0.8.4 && ruff check .'
	$(COMPOSE) exec -T worker sh -c 'pip install -q ruff==0.8.4 && ruff check .'
	$(COMPOSE) exec -T web sh -c 'npm run lint'

.PHONY: fmt
fmt:
	$(COMPOSE) exec -T api sh -c 'pip install -q ruff==0.8.4 && ruff format . && ruff check --fix .'
	$(COMPOSE) exec -T worker sh -c 'pip install -q ruff==0.8.4 && ruff format . && ruff check --fix .'

.PHONY: typecheck
typecheck:
	$(COMPOSE) exec -T api sh -c 'pip install -q mypy==1.13.0 && mypy app'
	$(COMPOSE) exec -T worker sh -c 'pip install -q mypy==1.13.0 && mypy app'
	$(COMPOSE) exec -T web sh -c 'npm run typecheck'
