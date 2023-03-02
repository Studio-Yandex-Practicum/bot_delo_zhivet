# Строковые сообщения модуля .database
DBAPI_ERROR = "Возникла ошибка при обращении к БД {db_info} через DBAPI. " "Подробности:\n{details}"
DB_COMMON_ERROR = "Возникла общая ошибка при обращении к БД {db_info}. " "Подробности:\n{details}"

# Строковые сообщения модуля __init__.py
DB_NOT_READY_FOR_INIT_APP_ERROR = (
    "База данных не готова для создания и запуска приложения '{app_name}'. " "Подробности:\n{details}"
)
MISSING_REQUIRED_TABLES_ERROR = (
    "Не обнаружены таблицы, необходимые для создания и "
    "запуска приложения '{app_name}'.\n"
    "Список отсутствующих таблиц: {not_existing_tables}"
)

# Строковые сообщения модуля manage.py
APP_TEMPLATE_FOLDER_COPY_SUCCESS = "Копирование существующих шаблонов успешно завершено"
APP_TEMPLATE_FOLDER_NOT_FOUND = "Не найдена папка с шаблонами приложения. Будут скопированы только шаблоны Flask-Admin"
COLLECT_STATIC_CLEAR_DIR_INFO = "Очищаем папку '{dst}'"
COLLECT_STATIC_DIR_ALREADY_EXIST = (
    "Папка {dst} уже существует. Значение параметра --overwrite {overwrite}. Не будет произведено никаких действий"
)
COLLECT_STATIC_ERROR = "В ходе сбора статики возникла ошибка. Подробности:\n{details}"
COLLECT_STATIC_INFO = "Собираем статику Flask-Admin в папку '{dst}'"
COLLECT_TEMPLATES_ERROR = "Копирование шаблонов Flask-Admin завершено с ошибкой. Подробности:\n{details}"
COLLECT_TEMPLATES_SUCCESS = "Копирование шаблонов Flask-Admin завершено успешно"
COMMON_ERROR = "Возникла ошибка. Подробности: {details}"
START_LOGGING = "Запуск логгера"
STOP_LOGGING = "Завершение работы логгера"
UNKNOWN_COMMAND = "Неизвестная команда {command}"
