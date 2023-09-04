FROM python:3.11.4-slim as build

WORKDIR /app

COPY ./pyproject.toml ./poetry.lock ./README.md ./

RUN mkdir "src" && echo "import this" > src/main.py \
    && pip install poetry==1.3.2 \
    && poetry install --without dev --no-interaction --no-ansi


FROM python:3.11.4-slim

COPY --from=build /root/.cache/pypoetry/virtualenvs/ /root/.cache/pypoetry/virtualenvs/

RUN pip install poetry==1.3.2

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 

COPY . .
