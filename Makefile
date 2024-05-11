install:
	pip install -r requirements.txt

migrate:
	alembic revision --autogenerate

upgrade:
	alembic upgrade head

downgrade:
	alembic downgrade -1