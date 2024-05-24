FROM python:3.12

WORKDIR /app

COPY requirements.txt /app/

RUN pip install -r requirements.txt

COPY ./app /app
COPY alembic.ini /app/alembic.ini

#RUN alembic -c /app/alembic.ini upgrade head

CMD ["python", "main.py"]
