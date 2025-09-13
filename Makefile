.PHONY: up down rebuild logs ps pull create refine list show versions finalize diff health

up:
	docker compose up -d --build

rebuild:
	docker compose build api && docker compose up -d api

down:
	docker compose down

logs:
	docker compose logs -f

ps:
	docker compose ps

pull:
	docker compose pull

create:
	uv run python api_client.py draft --title "$(TITLE)" --counterparty "$(COUNTERPARTY)" --jurisdiction "$(JURISDICTION)"

refine:
	uv run python api_client.py refine --id $(ID) --instructions "$(INSTR)"

list:
	uv run python api_client.py list

show:
	uv run python api_client.py show --id $(ID) $(if $(VERSION),--version $(VERSION),)

versions:
	uv run python api_client.py versions --id $(ID)

finalize:
	uv run python api_client.py finalize --id $(ID)

diff:
	uv run python api_client.py diff --id $(ID) --a $(A) --b $(B)

health:
	curl -sf localhost:8000/health && echo OK || (echo FAIL && exit 1)
