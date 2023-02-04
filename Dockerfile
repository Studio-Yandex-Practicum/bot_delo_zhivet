FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install poetry==1.3.2

WORKDIR /app
COPY . .
RUN poetry config virtualenvs.create false
RUN poetry install
# RUN alembic stamp head
# RUN alembic revision --autogenerate
# RUN alembic upgrade head
CMD ["poetry", "run", "runbot"]
