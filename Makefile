.PHONY: lint dcu dcd

lint:
	@echo "Linting..."
	ruff check --fix . 
	ruff format .

dcu:
	@echo "Docker Compose Up..."
	docker compose up

dcd:
	@echo "Docker Compose Down..."
	docker compose down
