FROM python:3.11-slim

RUN apt-get update && apt-get install -y curl

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip3 install poetry

WORKDIR /app
#COPY ../poetry.lock ../pyproject.toml ./
#COPY ../poetry.lock ./
COPY pyproject.toml .
COPY . .
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

