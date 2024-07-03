FROM python:3.11-slim-bullseye

RUN apt-get update && apt-get install -y pkg-config python3-dev build-essential default-libmysqlclient-dev

WORKDIR /usr/app

RUN groupadd -r appuser && useradd -r -g appuser -d /usr/app -s /sbin/nologin appuser
ENV PATH=$PATH:/usr/app/.local/bin

COPY ../requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir common \
    api

COPY common/mySQLDb.py common/.
COPY common/webUtils.py common/.
COPY *.kube .

COPY api/apiServer.py api/.

RUN chown -R appuser:appuser /usr/app

USER appuser:appuser

EXPOSE 5000/tcp

CMD ["gunicorn", "api.apiServer:app", "-w", "4", "-b", "0.0.0.0:5000"]