FROM python:3.11-alpine

RUN apk update && apk add gcc \
                          libpq-dev \
                          libc-dev \
                          libffi-dev \
                          --no-cache bash

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install poetry==1.3.2
# RUN pip install psycopg2==2.9.5

WORKDIR /app
COPY . .
RUN poetry config virtualenvs.create false && poetry install --with prod

# RUN poetry config virtualenvs.create false
# RUN poetry install
# CMD ["poetry", "run", "runbot", "&", "poetry", "run", "python", "admin/run.py"]

#EXPOSE 5000
#EXPOSE 5432
#ENTRYPOINT ["poetry", "run", "runbot"]

#RUN sleep 5
#EXPOSE 5001
#EXPOSE 5002
ENTRYPOINT ["flask"]

CMD ["run", "--host", "0.0.0.0", "--port", "5000"]

#CMD ["poetry", "run", "runbot"]
#CMD ["poetry", "show"]