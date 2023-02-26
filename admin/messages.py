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
COLLECT_STATIC_ERROR = "В ходе сбора статики возникла ошибка. Подробности:\n{details}"
COLLECT_STATIC_INFO = "Собираем статику Flask-Admin в папку '{dst}'"
COLLECT_TEMPLATES_ERROR = "Копирование шаблонов Flask-Admin завершено с ошибкой. Подробности:\n{details}"
COLLECT_TEMPLATES_SUCCESS = "Копирование шаблонов Flask-Admin завершено успешно"
COMMON_ERROR = "Возникла ошибка. Подробности: {details}"
START_LOGGING = "Запуск логгера"
STOP_LOGGING = "Завершение работы логгера"
UNKNOWN_COMMAND = "Неизвестная команда {command}"

# Строковые константы модуля mail.py
RESET_PASSWORD_SUBJECT = "[Дело живёт] Сброс пароля админки"

# Строковые сообщения модуля views.py
ALREADY_REGISTRED = '<p>Вы уже зарегистрированы? <a href="{url}">Нажмите здесь, чтобы войти</a></p>'
BAD_TOKEN = "Недействительный токен"
RESTORE_PASSWORD_SEND = "На Вашу электронную почту отправлены инструкции по сбросу пароля"
SUGGEST_REGISTRATION = '<p>У Вас нет учетной записи? <a href="{url}">Нажмите здесь, чтобы зарегистрироваться</a></p>'
PASSWORD_CHANGED_SUCCESS = "Пароль успешно изменен"

# Строковые сообщения модуля forms.py
ACCOUNT_LABEL = "Учетная запись"
EMAIL_LABEL = "Электронная почта"
PASSWORD_LABEL = "Пароль"
REPEAT_PASSWORD = "Повторите пароль"
WRONG_USER = "Неверный пользователь"
ACCOUNT_BUSY = "Пользователь с такой учетной записью уже существует"
EMAIL_BUSY = "Пользователь с таким адресом электронной почты существует"
INPUT_EMAIL = "Введите Вашу электронную почту"
EMAIL_NOT_FOUND = "Пользователь с таким адресом электронной почты не найден"
