# Use the official Ubuntu base image
FROM python:3.11-slim-bullseye

# Set environment variables to avoid user interaction during installation
ENV DEBIAN_FRONTEND=noninteractive

# Update the package list and install Python
RUN apt-get update && \
    apt-get install -y python3 python3-pip pkg-config python3-dev build-essential default-libmysqlclient-dev && \
    apt-get clean

# Verify Python installation
RUN python3 --version

WORKDIR /usr/app

RUN groupadd -r appuser && useradd -r -g appuser -d /usr/app -s /sbin/nologin appuser
ENV PATH=$PATH:/usr/app/.local/bin

COPY ../requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir dataPreparation \
    dataPreparation/common \
    resources

COPY common/mongoDb.py dataPreparation/common/.
COPY common/neo4JConnection.py dataPreparation/common/.
COPY common/webUtils.py dataPreparation/common/.
COPY dataPreparation/* dataPreparation/.
COPY resources/* resources/.
COPY .env.kube .env

# Expose the port the app runs on (if needed)
# EXPOSE 5000

# Set the command to keep the container running
CMD ["bash", "-c", "while true; do sleep 30; done"]