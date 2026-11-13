.PHONY: up down logs rebuild test
up:
	docker compose up --build -d
logs:
	docker compose logs -f --tail=80
down:
	docker compose down
rebuild:
	docker compose up -d --build
# Install backend/requirements-dev.txt before running
test:
	cd backend && pytest -q
