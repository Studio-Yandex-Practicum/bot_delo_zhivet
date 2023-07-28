# Строковые сообщения модуля .database
DBAPI_ERROR = "Возникла ошибка при обращении к БД через DBAPI. Подробности:\n{details}"
DBAPI_LOGGER = "Возникла ошибка при обращении к БД через DBAPI."
DB_COMMON_ERROR = "Возникла общая ошибка при обращении к БД {db_info}. Подробности:\n{details}"
DB_COMMON_LOGGER = "Возникла общая ошибка при обращении к БД"

# Строковые сообщения модуля __init__.py
DB_NOT_READY_FOR_INIT_APP_ERROR = (
    "База данных не готова для создания и запуска приложения '{app_name}'. Подробности:\n{details}"
)
DB_NOT_READY_FOR_INIT_APP_LOGGER = "База данных не готова для создания и запуска приложения."
MISSING_REQUIRED_TABLES_ERROR = (
    "Не обнаружены таблицы, необходимые для создания и "
    "запуска приложения '{app_name}'.\n"
    "Список отсутствующих таблиц: {not_existing_tables}"
)
MISSING_REQUIRED_TABLES_LOGGER = "Не обнаружены таблицы, необходимые для создания и запуска приложения"

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

# Строковые константы модуля mail.py
RESET_PASSWORD_SUBJECT = "[Дело живёт] Сброс пароля админки"

# Строковые сообщения модуля views.py
ALREADY_REGISTRED = '<p>Вы уже зарегистрированы? <a href="{url}">Нажмите здесь, чтобы войти</a></p>'
BAD_TOKEN = "Недействительный токен"
MAIL_SEND_SUCCESS = "Сообщение с темой '{subject}' отправлено на адрес '{recipients}'."
MAIL_SEND_ERROR = "Ошибка отправки сообщения с темой '{subject}' на адрес '{recipients}'. Подробности: {details}"
RESTORE_PASSWORD_SEND = "На Вашу электронную почту отправлены инструкции по сбросу пароля."
SUGGEST_REGISTRATION = '<p>У Вас нет учетной записи? <a href="{url}">Нажмите здесь, чтобы зарегистрироваться</a></p>'
PASSWORD_CHANGED_SUCCESS = "Пароль успешно изменен"

# Строковые сообщения модуля forms.py
ACCOUNT_LABEL = "Учетная запись"
EMAIL_LABEL = "Электронная почта"
PASSWORD_LABEL = "Пароль"
REPEAT_PASSWORD = "Повторите пароль"
WRONG_USER = "Неверный пользователь"
WRONG_PASSWORD = "Неверный пароль"
ACCOUNT_BUSY = "Пользователь с такой учетной записью уже существует"
EMAIL_BUSY = "Пользователь с таким адресом электронной почты существует"
INPUT_EMAIL = "Введите Вашу электронную почту"
EMAIL_NOT_FOUND = "Пользователь с таким адресом электронной почты не найден"
DISSALOWED_CHARS_IN_ACCOUNT = "Учетная запись должна содержать только латинские буквы"
DISSALOWED_CHARS_IN_PASWORD = "Пароль не должен содержать знаки табуляции и пробелы"
PASSWORD_CONTAINS_ACCOUNT = "Пароль не должен содержать в себе учетную запись независимо от регистра"
PASSWORD_TOO_LONG = "Пароль не должен быть больше {max_len} символов"
REQUIRED_FIELD = "Это поле является обязательным"
LOGIN_LENGTH = "Длина логина должна составлять от 1 до 20 символов"
INVALID_EMAIL = "Некорректный адрес электронной почты"
PASSWORD_LENGTH = "Минимальная длина пароля должна составлять 8 символов"
EQUAL_PASSWORDS = "Пароли не совпадают"

# Строковые сообщения модуля utils.py
TOKEN_VALIDATION_ERROR = "Не удалось провести валидацию токена."
GET_DATABASE_FIELDS = "Извлекаем поля из базы"
GENERATE_RESET_TOKEN = "Генерируем токен для сброса пароля"
USER_NOT_FOUND = "Не удалось найти пользователя для сброса пароля"
TAG_EXISTS = "В базе уже существует похожий тег!"
TAG_CHECKED = "Тег прошел проверку уникальности"
