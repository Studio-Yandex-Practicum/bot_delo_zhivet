[![Master Branch](https://img.shields.io/badge/branch-master-brightgreen?labelColor=343a42)](https://github.com/Studio-Yandex-Practicum/bot_delo_zhivet/tree/master) [![Checking with linters](https://github.com/Studio-Yandex-Practicum/bot_delo_zhivet/actions/workflows/lint.yml/badge.svg?branch=master)]( https://github.com/Studio-Yandex-Practicum/bot_delo_zhivet/actions/workflows/lint.yml) [![Deploy status](https://github.com/Studio-Yandex-Practicum/bot_delo_zhivet/actions/workflows/bot_delo_zhivet_workflow.yml/badge.svg?branch=master)](https://github.com/Studio-Yandex-Practicum/bot_delo_zhivet/actions/workflows/bot_delo_zhivet_workflow.yml)<br/>
[![Develop Branch](https://img.shields.io/badge/branch-develop-brightgreen?labelColor=343a42)](https://github.com/Studio-Yandex-Practicum/bot_delo_zhivet/tree/develop) [![Checking with linters](https://github.com/Studio-Yandex-Practicum/bot_delo_zhivet/actions/workflows/lint.yml/badge.svg?branch=develop)]( https://github.com/Studio-Yandex-Practicum/bot_delo_zhivet/actions/workflows/lint.yml) [![Deploy status](https://github.com/Studio-Yandex-Practicum/bot_delo_zhivet/actions/workflows/bot_delo_zhivet_workflow.yml/badge.svg?branch=develop)](https://github.com/Studio-Yandex-Practicum/bot_delo_zhivet/actions/workflows/bot_delo_zhivet_workflow.yml)

# bot_delo_zhivet
Телеграм-бот для организации эко-субботников.

### Оглавление:
1. [Установка Poetry и запуск виртуального окружения](#установка-poetry-и-запуск-виртуального-окружения)
    1. [Установка Poetry](#установка-poetry)
    2. [Запуск виртуального окружения](#запуск-виртуального-окружения)
    3. [Потенциальные проблемы](#потенциальные-проблемы)
2. [Установка pre-commit hooks](#установка-pre-commit-hooks)
    1. [Установка pre-commit](#установка-pre-commit)
    2. [Установка hooks](#установка-hooks)
3. [Запуск бота на локальной машине](#запуск-бота-на-локальной-машине)
    1. [Настройка env-файлов](#1-настройка-env-файлов)
    2. [Запуск сервисов бота в Docker](#2-запуск-сервисов-бота-в-docker)
    3. [Отдельный запуск базы и применение миграций на локальной машине](#3-отдельный-запуск-базы-и-применение-миграций-на-локальной-машине)
4. [Deprecated](#deprecated)
---

## Установка Poetry и запуск виртуального окружения

ℹ️ [Документация Poetry](https://python-poetry.org/docs/#installation)

### Установка Poetry

Для Linux, macOS, Windows (WSL):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```
Для Windows (Powershell):
```bash
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```
В macOS и Windows сценарий установки предложит добавить папку с исполняемым файлом Poetry в переменную PATH. Сделайте это, выполнив следующую команду (не забудьте поменять {USERNAME} на имя вашего пользователя):

macOS
```bash
export PATH="/Users/{USERNAME}/.local/bin:$PATH"
```
Windows
```bash
$Env:Path += ";C:\Users\{USERNAME}\AppData\Roaming\Python\Scripts"; setx PATH "$Env:Path"
```
Проверить установку:
```bash
poetry --version
```
Установка автодополнений bash (опционально):
```bash
poetry completions bash >> ~/.bash_completion
```

### Запуск виртуального окружения

🔖 [Настройка окружения Poetry для PyCharm](https://www.jetbrains.com/help/pycharm/poetry.html)

Создание виртуального окружения:
```bash
poetry env use python3.10
```
Установка зависимостей (для разработки):
```bash
poetry install --with dev
```
Запуск оболочки и активация виртуального окружения (из папки проекта):
```bash
poetry shell
```
Проверка активации виртуального окружения:
```bash
poetry env list
```

### Потенциальные проблемы

*(проверено на macOS + VSCode)*

**a. виртуальное окружение Poetry недоступно при выборе интерпретатора**

С высокой вероятностью виртуальное окружение создалось вне папки проекта. Командой ниже можно удостовериться, что окружение будет создано внутри пути проекта:
```bash
poetry config virtualenvs.in-project true
```
Если проект уже был создан, придется пересоздать окружение:
```bash
poetry env list  # вывести имя текущего окружения
poetry env remove <current environment>  # удалить текущее окружение
poetry install --with dev  # создаст новое окружение с уже с учетом нового конфига virtualenvs.in-project true
```

**b. путь к Poetry не прописан / приходится указывать заново при переоткрытии проекта в редакторе**

В зависимости от типа используемой оболочки, найдите и откройте bashrc / zshrc файл:
```bash
nano ~/.zshrc
```
Если в файле нет этой строки, добавьте ее и сохраните изменения (не забудьте указать свой {USERNAME}):
```bash
export PATH="/Users/{USERNAME}/.local/bin:$PATH"
```

[:arrow_up: Оглавление](#оглавление)

---

## Установка pre-commit hooks
Для того, чтобы при каждом коммите выполнялись pre-commit проверки, необходимо:
- [Установить pre-commit](#установка-pre-commit)
- [Установить pre-commit hooks](#установка-hooks)

### Установка pre-commit

Модуль pre-commit уже добавлен в requirements и должен установиться вместе с виртуальным окружением автоматически.

Проверить наличие pre-commit можно командой (при активированном виртуальном окружении):
```bash
pre-commit --version
# >> pre-commit 2.21.0
```
Если этого не произошло, то необходимо [установить pre-commit по официальной инструкции](https://pre-commit.com/#install):
* установка через менеджер пакетов brew: `brew install pre-commit`
* установка через poetry: `poetry add pre-commit`
* установка через pip: `pip install pre-commit`

[:arrow_up: Оглавление](#оглавление)

___

### Установка hooks

Установка хуков:
```bash
pre-commit install --all
```

В дальнейшем, при выполнении команды `git commit` будут выполняться проверки, перечисленные в файле `.pre-commit-config.yaml`.

Если не видно, какая именно ошибка мешает выполнить commit, можно запустить хуки вручную командой:

```bash
pre-commit run --all-files
```

[:arrow_up: Оглавление](#оглавление)

___

## Запуск бота на локальной машине

### 1. Настройка env-файлов

1. В папке infrastructure/ есть директория `.env.examples` с константами, которые необходимо заполнить тестовыми значениями. Создайте рядом с ней НОВУЮ директорию с именем
```
.env_files
```
скопируйте в нее все файлы из `.env.examples`
Удалите из имени файлов `.example` после окончания их настройки.
Инструкция и примеры значений: https://www.notion.so/env-8b7403f73b604daf90253041de4fec19
НЕ ИЗМЕНЯЙТЕ файлы в `.env.examples`

2. Запускать бота можно в режимах **polling** и **webhook**. Для режима webhook в файле `.env.telegram` должны быть указаны параметры WEBHOOK_DOMAIN и WEBHOOK_PORT. Подробнее [в официальном гайде Telegram](https://core.telegram.org/bots/webhooks).

### 2. Запуск сервисов бота в Docker

1. Запустить Docker

2. Если был запущен локальный контейнер с базой, остановить его:

остановить контейнер
```bash
docker compose -f infrastructure/docker_compose_files/postgres-local.yaml stop
# для остановки и удаления контейнера, тома и связей:
# docker compose -f infrastructure/docker_compose_files/postgres-local.yaml down
```

3. Запуск сервисов бота (database, bot, flask admin, redis, celery, flower):


```bash
docker compose -f infrastructure/docker_compose_files/docker-compose-local.yaml up -d --build
```

4. Установить миграции (и активировать Flask админ панель):

```bash
docker compose -f infrastructure/docker_compose_files/docker-compose-local.yaml exec bot poetry run alembic upgrade head
```

Смотреть заполненные заявки, прошедшие celery, можно во flower: http://localhost:5555/ <br/>
Доступ к админ панели Flask: http://localhost/admin/

5. Если Flask-admin загружается без статики - ее можно собрать. Из корневой директории проекта с активным виртуальным окружением запустите скрипт collectstatic:

```bash
docker compose -f infrastructure/docker_compose_files/docker-compose-local.yaml exec web poetry run python admin/manage.py collectstatic --static_folder static --overwrite
```


6. *Если docker compose выбрасывает ошибку на стадии установки Poetry в runtime, попробуйте добавить в Dockerfile дополнительные пакеты для второй стадии сборки*:
```bash
FROM python:3.11.2-alpine3.17

RUN apk update && apk add --no-cache \
    gcc \
    libc-dev \
    libffi-dev \
    libpq-dev
```

### 3. Отдельный запуск базы и применение миграций на локальной машине

1. Запустить Docker

2. Поднять контейнер с базой:


```bash
docker compose -f infrastructure/docker_compose_files/postgres-local.yaml up -d --build
```

3. Применить миграции:

из КОРНЯ проекта
```bash
alembic upgrade head
```

4. Если произошли изменения в моделях:

**Каждую новую autogenerate-миграцию необходимо проверить перед применением [по документации](https://geoalchemy-2.readthedocs.io/en/latest/alembic.html#interactions-between-alembic-and-geoalchemy-2)**, в том числе проверить выполнение следующих правил: <br/>
a) remove the `create_index` statement in the `upgrade()` function <br/>
b) remove the `drop_index` statement in the `downgrade()` function <br/>

Выставить указатель на последнюю актуальную версию базы данных:
```bash
alembic stamp head
```

Сформировать новую миграцию:
```bash
alembic revision --autogenerate -m "you_migration_name"
```

Проверить сформированную миграцию по пунктам **a-b** выше, **если все условия учтены** - применить ее:
```bash
alembic upgrade head
```

[:arrow_up: Оглавление](#оглавление)
___

### Локальный Запуск Flask-admin с базой в докере
Если виртуальное окружение активно и запущен `postgres-local.yaml`:

1. Выполнить в теринале

из КОРНЯ проекта
```
flask run
```
2. Перейти по ссылке из терминала, ввести логин и пароль.
___
