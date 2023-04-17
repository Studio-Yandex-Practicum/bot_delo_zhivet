[![Master Branch](https://img.shields.io/badge/branch-master-brightgreen?labelColor=343a42)](https://github.com/Studio-Yandex-Practicum/bot_delo_zhivet/tree/master) [![Checking with linters](https://github.com/Studio-Yandex-Practicum/bot_delo_zhivet/actions/workflows/lint.yml/badge.svg?branch=master)]( https://github.com/Studio-Yandex-Practicum/bot_delo_zhivet/actions/workflows/lint.yml) [![Deploy status](https://github.com/Studio-Yandex-Practicum/bot_delo_zhivet/actions/workflows/bot_delo_zhivet_workflow.yml/badge.svg?branch=master)](https://github.com/Studio-Yandex-Practicum/bot_delo_zhivet/actions/workflows/bot_delo_zhivet_workflow.yml)<br/>
[![Develop Branch](https://img.shields.io/badge/branch-develop-brightgreen?labelColor=343a42)](https://github.com/Studio-Yandex-Practicum/bot_delo_zhivet/tree/develop) [![Checking with linters](https://github.com/Studio-Yandex-Practicum/bot_delo_zhivet/actions/workflows/lint.yml/badge.svg?branch=develop)]( https://github.com/Studio-Yandex-Practicum/bot_delo_zhivet/actions/workflows/lint.yml) [![Deploy status](https://github.com/Studio-Yandex-Practicum/bot_delo_zhivet/actions/workflows/bot_delo_zhivet_workflow.yml/badge.svg?branch=develop)](https://github.com/Studio-Yandex-Practicum/bot_delo_zhivet/actions/workflows/bot_delo_zhivet_workflow.yml)

# bot_delo_zhivet
Телеграм-бот для организации эко-субботников.

___
## Оглавление:
1. [Установка poetry и запуск виртауального окружения](#Установка-poetry-и-запуск-виртауального-окружения)
2. [Установка pre-commit hook](#Установка-pre-commit-hook)
    1. [Установка pre-commit](#Установка-pre-commit)
    2. [Установка hook](#Установка-hook)
3. [Подключение системы мониторинга Sentry](#Подключение-системы-мониторинга-Sentry)
4. [Запуск базы и применение миграций на локальной машине](#Запуск-базы-и-применение-миграций-на-локальной-машине)
5. [Запуск бота](#Запуск-бота)
___
## Установка poetry и запуск виртауального окружения
Для Linux, macOS, Windows (WSL):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```
Для Windows (Powershell):
```bash
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```
В macOS и Windows сценарий установки предложит добавить папку с исполняемым файлом poetry в переменную PATH. Сделайте это, выполнив следующую команду:

macOS
```bash
export PATH="/Users/jetbrains/.local/bin:$PATH"
```
Windows
```bash
$Env:Path += ";C:\Users\jetbrains\AppData\Roaming\Python\Scripts"; setx PATH "$Env:Path"
```
Не забудьте поменять jetbrains на имя вашего пользователя. Настройка окружения poetry для pycharm [тут](https://www.jetbrains.com/help/pycharm/poetry.html)

Для проверки установки выполните следующую команду:
```bash
poetry --version
```
Установка автодополнений bash(опцонально)
```bash
poetry completions bash >> ~/.bash_completion
```
Создание виртуально окружения
```bash
poetry env use python3.10
```
Установка зависимостей (для разработки)
```bash
poetry install --with dev
```
Запуск оболочки и активация виртуального окружения
```bash
your@device:~/your_project_pwd/bot_delo_zhivet$ poetry shell
```
Проверка активации виртуального окружения
```bash
poetry env list
```
___
## Запуск базы и применение миграций на локальной машине
Сначала поднимаем контейнер с базой Postgres
```bash
docker-compose -f postgres-local.yaml up -d --build
```
Если есть чьи-то миграции в проекте, то применяем их
```bash
alembic upgrade head
```
Если производятся изменения в моделях:

**Каждую новую autogenerate-миграцию необходимо проверить перед применением по доке:**
https://geoalchemy-2.readthedocs.io/en/latest/alembic.html#interactions-between-alembic-and-geoalchemy-2
в том числе проверить выполнение следующих правил:remove the create_index statement in the upgrade() function.
1. remove the `drop_index` statement in the `downgrade()` function.
1. remove the `create_index` statement in the `upgrade()` function.


```bash
alembic stamp head
```
1.
```bash
alembic revision --autogenerate -m "you_migration_name"
```
2.
Дальше применяем:
```bash
alembic upgrade head
```

[:arrow_up:Оглавление](#Оглавление)
___
## Установка pre-commit hook
Для того чтобы при каждом коммите выполнялись pre-commit проверки, необходимо:
1. Установить pre-commit
2. Установить pre-commit hooks

[:arrow_up:Оглавление](#Оглавление)

### Установка pre-commit

Модуль pre-commit уже добавлен в requirements, таким образом после настройки виртуального окружения, должен установится автоматически
Если этого не произошло, то установка осуществляется согласно требованиям [инструкций](https://pre-commit.com/#install):
* установка через менеджер пакетов brew `brew install pre-commit`
* установка через poetry `poetry add pre-commit`
* установка через pip `pip install pre-commit`

Проверить установку pre-commit можно командой (при активированном виртуальном окружении):
```bash
pre-commit --version
```
```bash
>>pre-commit 2.20.0
```

[:arrow_up:Оглавление](#Оглавление)



### Установка hook

Установка осуществляется hook командой
```bash
pre-commit install --all
```

В дальнейшем при выполнении команды `git commit` будут выполняться проверки перечисленные в файле `.pre-commit-config.yaml`.

Если не видно какая ошибка мешает выполнить commit, то можно запустить хуки в ручную можно командой

```bash
pre-commit run --all-files
```
___
### Подключение системы мониторинга Sentry
1. Зарегистрируйтесь на платформе:
https://sentry.io/signup/
2. Подключите Sentry к админке, для этого:
    - Создайте новый проект, выбрав при этом платформу FLASK.
      https://<your-organization>-ac.sentry.io/projects/new/
    - В настройках проекта перейдите в раздел "Client Keys", скопируйте ключ DSN (Data Source Name).
      https://<your-organization>-ac.sentry.io/settings/projects/<your-project>/keys/
    - Присвойте переменной SENTRY_DSN_ADMIN в файле .env полученное значение.
3. Подключите Sentry к боту, выполнив для этого аналогичные шаги:
    - Создайте еще один проект, выбрав при этом платформу PYTHON.
    - В настройках проекта перейдите в раздел "Client Keys", скопируйте ключ DSN.
    - Присвойте переменной SENTRY_DSN_BOT в файле .env полученное значение.
___
## Запуск бота
Переименуйте файл .env.example в .env и заполните его.
Запуск может быть в режимах polling и webhook. Для режима webhook в файле .env должны быть указаны параметры WEBHOOK_DOMAIN и WEBHOOK_PORT. Подробнее об этом написано [в официальном гайде telegram](https://core.telegram.org/bots/webhooks)

### Запуск бота осуществляется командой
Для Linux, macOS, Windows (WSL):
```bash
your@device:~/your_project_pwd/bot_delo_zhivet/$ poetry run runbot
```
## Запуск admin:
```bash
flask run
```
После запуска:

Перейти по ссылке в терминала, ввести логин(admin) и пароль(admin123)
___
[:arrow_up:Оглавление](#Оглавление)
