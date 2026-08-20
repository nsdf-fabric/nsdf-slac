.PHONY=dev
dev:
	@docker compose watch

.PHONY=build
build:
	@docker build -t nsdf-catalog .

.PHONY=up
up:
	@docker compose up -d

.PHONY=down
down:
	@docker compose down
	@docker volume rm catalog_postgres_data

.PHONY=rmdb
rmdb:
	@docker volume rm catalog_postgres_data

.PHONY=buildseed
buildseed:
	@docker build -f seed/Dockerfile -t nsdf-catalog-seed seed/

.PHONY=nexusseed
nexusseed:
	@cd nexusdm && go build -o bin/nexus ./cmd/

.PHONY=nexus
nexus:
	@cd nexusdm && ./bin/nexus
