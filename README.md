# bot_delo_zhivet
Телеграм-бот для организации эко-субботников.

## Оглавление:

0. [Установка pre-commit hook](#Установка pre-commit hook)
    1. [Установка pre-commit](#Установка pre-commit)
    2. [Установка hook](#Установка hook)



## Установка pre-commit hook
Для того чтобы при каждом коммите выполнялись pre-commit проверки, необходимо:
1. Установить pre-commit
2. Установить pre-commit hooks

[:arrow_up:Оглавление](#Оглавление)

<details><summary>**Установка pre-commit**</summary>
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
</details>

<details><summary>**Установка hook**</summary>
Установка осуществляется hook командой
```bash
pre-commit install --all
```

В дальнейшем при выполнении команды `git commit` будут выполняться проверки перечисленные в файле `.pre-commit-config.yaml`.

Если не видно какая ошибка мешает выполнить commit, то можно запустить хуки в ручную можно командой

```bash
pre-commit run --all-files
```

[:arrow_up:Оглавление](#Оглавление)
</details>
