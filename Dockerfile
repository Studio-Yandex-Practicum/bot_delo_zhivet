FROM python:3.11.2-alpine3.17

RUN apk update && apk add gcc \
                          libpq-dev \
                          libc-dev \
                          libffi-dev \
                          --no-cache bash

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install poetry==1.3.2

WORKDIR /app

COPY ./pyproject.toml .

COPY ./poetry.lock .

COPY ./README.md .

RUN mkdir "src"

RUN echo "import this" > src/main.py

RUN poetry config virtualenvs.create false && poetry install --with prod

COPY . .
