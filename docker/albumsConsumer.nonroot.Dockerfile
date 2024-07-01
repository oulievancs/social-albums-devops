FROM python:3.11-slim-bullseye

RUN apt-get update && apt-get install -y pkg-config python3-dev build-essential default-libmysqlclient-dev

WORKDIR /usr/app

RUN groupadd -r appuser && useradd -r -g appuser -d /usr/app -s /sbin/nologin appuser
ENV PATH=$PATH:/usr/app/.local/bin

COPY ../requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir common \
    transformationLoad

COPY common/mySQLDb.py common/.
COPY .env.kube .env

COPY transformationLoad/transformationAndLoadApp.py transformationLoad/.

RUN chown -R appuser:appuser /usr/app

USER appuser:appuser

CMD ["python", "transformationLoad/transformationAndLoadApp.py"]