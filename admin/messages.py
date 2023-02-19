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

# Строковые сообщения модуля commands.py
COLLECT_STATIC_CLEAR_DIR_INFO = "Очищаем папку '{dst}'"
COLLECT_STATIC_ERROR = "В ходе сбора статики возникла ошибка. Подробности:\n{details}"
COLLECT_STATIC_INFO = "Собираем статику Flask-Admin в папку '{dst}'"
COLLECT_TEMPLATES_ERROR = "Копирование шаблонов Flask-Admin завершено с ошибкой. Подробности:\n{details}"
COLLECT_TEMPLATES_SUCCESS = "Копирование шаблонов Flask-Admin завершено успешно"
