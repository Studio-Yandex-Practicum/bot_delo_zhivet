FROM python:3.11.2-alpine3.17 as build

RUN apk update && apk add gcc \
    libpq-dev \
    libc-dev \
    libffi-dev \
    --no-cache bash

RUN pip install poetry==1.3.2

WORKDIR /app

COPY ./pyproject.toml .

COPY ./poetry.lock .

COPY ./README.md .

RUN mkdir "src" && echo "import this" > src/main.py

RUN poetry install

FROM python:3.11.2-alpine3.17

COPY --from=build /root/.cache/pypoetry/virtualenvs/ /root/.cache/pypoetry/virtualenvs/

RUN pip install poetry==1.3.2

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY . .
