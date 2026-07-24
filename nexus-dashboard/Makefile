.PHONY: dev
dev:
	@docker compose watch

.PHONY: build
build:
	@docker build -t nexus-dashboard .

.PHONY: up
up:
	@docker compose up -d

.PHONY: down
down:
	@docker compose down
