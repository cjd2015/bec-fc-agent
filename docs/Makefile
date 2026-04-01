# BEC Agent - Makefile
# 版本: 1.0
# 更新时间: 2026-03-31

PROJECT_DIR ?= /opt/bec-agent
POSTGRES_COMPOSE_FILE ?= $(PROJECT_DIR)/postgres/docker-compose.secure.yml
SCHEMA_FILE ?= $(PROJECT_DIR)/schema.sql
SEED_FILE ?= $(PROJECT_DIR)/seed.sql
POSTGRES_CONTAINER ?= bec-postgres
DB_USER ?= bec_user
DB_NAME ?= bec_agent
NGINX_CONF ?= /etc/nginx/conf.d/datahive.top.conf
FRONTEND_DIST ?= /var/www/datahive.top

.PHONY: help postgres-up postgres-down postgres-restart postgres-logs postgres-ps init-schema seed-db reset-db nginx-test nginx-reload frontend-deploy health-check

help:
	@echo "Available targets:"
	@echo "  postgres-up        Start PostgreSQL container"
	@echo "  postgres-down      Stop PostgreSQL container"
	@echo "  postgres-restart   Restart PostgreSQL container"
	@echo "  postgres-logs      Tail PostgreSQL logs"
	@echo "  postgres-ps        Show PostgreSQL container status"
	@echo "  init-schema        Import schema.sql into database"
	@echo "  seed-db            Import seed.sql into database"
	@echo "  reset-db           Re-import schema.sql and seed.sql"
	@echo "  nginx-test         Validate nginx config"
	@echo "  nginx-reload       Reload nginx"
	@echo "  frontend-deploy    Placeholder for deploying frontend dist"
	@echo "  health-check       Check PostgreSQL container health"

postgres-up:
	docker compose -f $(POSTGRES_COMPOSE_FILE) up -d

postgres-down:
	docker compose -f $(POSTGRES_COMPOSE_FILE) down

postgres-restart:
	docker compose -f $(POSTGRES_COMPOSE_FILE) down
	docker compose -f $(POSTGRES_COMPOSE_FILE) up -d

postgres-logs:
	docker logs -f $(POSTGRES_CONTAINER)

postgres-ps:
	docker ps | grep $(POSTGRES_CONTAINER) || true

init-schema:
	cat $(SCHEMA_FILE) | docker exec -i $(POSTGRES_CONTAINER) psql -U $(DB_USER) -d $(DB_NAME)

seed-db:
	cat $(SEED_FILE) | docker exec -i $(POSTGRES_CONTAINER) psql -U $(DB_USER) -d $(DB_NAME)

reset-db: init-schema seed-db

nginx-test:
	nginx -t

nginx-reload:
	nginx -s reload

frontend-deploy:
	@echo "Upload frontend build files to $(FRONTEND_DIST) manually or via rsync/scp"

health-check:
	docker inspect $(POSTGRES_CONTAINER) | grep -A 20 Health || true
