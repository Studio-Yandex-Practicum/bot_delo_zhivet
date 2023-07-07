## Это список полезных команд.
Использование его подразумевает что вы уже установили себе poetry, настроили енв файлы и смогли развернуть проект. Помните что все docker команды выполняются с запущеным движком Docker из корня проекта.

## Запуски в контейнерах
### Запуск ВСЕХ сервисов бота (db, bot, flask admin, redis, celery, flower): 

```bash
docker compose -f infrastructure/docker_compose_files/docker-compose-local.yaml up -d --build
```

* Накатить миграции :

```bash
docker compose -f infrastructure/docker_compose_files/docker-compose-local.yaml exec bot poetry run alembic upgrade head
```

* Cобрать статитку:

```bash
docker compose -f infrastructure/docker_compose_files/docker-compose-local.yaml exec web poetry run python admin/manage.py collectstatic --static_folder static --overwrite
```
### Остановить ВСЕ сервисы бота
```bash
docker compose -f infrastructure/docker_compose_files/docker-compose-local.yaml stop
```
### Ссылки на сервисы бота:
* flask-админка: http://localhost/admin/login/
* flower: http://localhost:5555/


## Локальные и частичные запуски

### Запуск контейнера с базой который в docker-compose-local.yaml (тот же что и в запусках всего в контейнерах)

```bash
docker compose -f infrastructure/docker_compose_files/docker-compose-local.yaml up db -d
```
* Накатить  миграции :
```bash
alembic upgrade head
```

### Запуск отдельного контейнера с базой (у него отдельный вольюм с данными!)

```bash
docker compose -f infrastructure/docker_compose_files/postgres-local.yaml up -d --build
```

* Накатить  миграции :
```bash
alembic upgrade head
```

* Сформировать новую миграцию:
```bash
alembic revision --autogenerate -m "you_migration_name"
```

**Каждую новую autogenerate-миграцию необходимо проверить перед применением [по документации](https://geoalchemy-2.readthedocs.io/en/latest/alembic.html#interactions-between-alembic-and-geoalchemy-2)**, в том числе проверить выполнение следующих правил: <br/>
a) remove the `create_index` statement in the `upgrade()` function <br/>
b) remove the `drop_index` statement in the `downgrade()` function <br/>

### Локальный Запуск Flask-admin:
должен быть запущен хоть какой то контейнер с базой
docker-compose-local.yaml или postgres-local.yaml , какой будет запущен к тому фласк и присоеденится
```bash
flask run
```

### Локальный запуск бота:
не о чень полезно, тк без контейнеров с celery ничего не отправить, но мало ли что 
должен быть запущен хоть какой то контейнер с базой
docker-compose-local.yaml или postgres-local.yaml , какой будет запущен к тому бот и присоеденится
```bash
poetry run runbot
```

## Команда для установки зависимостей poetry
может понадобиться если были добавлены новые либы.
```bash
poetry install --with dev
```