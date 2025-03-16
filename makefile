.PHONY: up down recreate-db

up:
	docker-compose up --build

down:
	docker-compose down

recreate-db:
	docker-compose exec app python -m scripts.recreate_db