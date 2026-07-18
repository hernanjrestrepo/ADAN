.PHONY: up down logs migrate seed test-backend test-frontend lint

up:
	docker compose -f infra/docker-compose.yml up -d --build

down:
	docker compose -f infra/docker-compose.yml down

logs:
	docker compose -f infra/docker-compose.yml logs -f

migrate:
	docker compose -f infra/docker-compose.yml exec api alembic upgrade head

seed:
	docker compose -f infra/docker-compose.yml exec api python /app/../scripts/seed_demo.py

test-backend:
	cd backend && .venv/Scripts/python.exe -m pytest -v

test-frontend-e2e:
	cd frontend && npm run test:e2e

lint:
	cd backend && .venv/Scripts/python.exe -m ruff check .
	cd frontend && npm run lint
