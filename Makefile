build:
	@docker build -t slac-dashboard .
up:
	@docker compose up -d
down:
	@docker compose down
