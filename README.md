# bot_delo_zhivet
Телеграм-бот для организации эко-субботников.


[![Checking with linters](https://github.com/Studio-Yandex-Practicum/bot_delo_zhivet/actions/workflows/lint.yml/badge.svg)](https://github.com/Studio-Yandex-Practicum/bot_delo_zhivet/actions/workflows/lint.yml)
[![Deploy status](https://github.com/Studio-Yandex-Practicum/bot_delo_zhivet/actions/workflows/bot_delo_zhivet_workflow.yml/badge.svg)](https://github.com/Studio-Yandex-Practicum/bot_delo_zhivet/actions/workflows/bot_delo_zhivet_workflow.yml)

___
## Оглавление:
1. [Установка poetry и запуск виртауального окружения](#Установка-poetry-и-запуск-виртауального-окружения)
2. [Установка pre-commit hook](#Установка-pre-commit-hook)
    1. [Установка pre-commit](#Установка-pre-commit)
    2. [Установка hook](#Установка-hook)
3. [Запуск бота](#Запуск-бота)
___
## Установка poetry и запуск виртауального окружения
Для Linux, macOS, Windows (WSL):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```
Установка автодополнений bash(опцонально)
```bash
poetry completions bash >> ~/.bash_completion
```
Создание виртуально окружения
```bash
poetry env use python3.10
```
Установка зависимостей
```bash
poetry install
```
Запуск оболочки и активация виртуального окружения
```bash
your@device:~/your_project_pwd/bot_delo_zhivet$ poetry shell
```
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
## Запуск бота
Для Linux, macOS, Windows (WSL):
```bash
your@device:~/your_project_pwd/bot_delo_zhivet/src/$ poetry run runbot
```
___
[:arrow_up:Оглавление](#Оглавление)

