install:
	pip install -r requirements.txt

migrate:
	docker exec $(CONTAINER) alembic revision --autogenerate

upgrade:
	docker exec $(CONTAINER) alembic upgrade head

downgrade:
	docker exec $(CONTAINER) alembic downgrade -1