FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/

RUN apt-get update && apt-get install -y ffmpeg
RUN pip install -r requirements.txt --no-cache-dir

COPY ./app /app

# INFO: 以下の行はコンテナ起動後にexecで実行するように
#RUN alembic -c /app/alembic.ini upgrade head

CMD ["python", "main.py"]
