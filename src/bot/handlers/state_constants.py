# Обозначим состояния главного менюSELECTING_ACTION
import re

from telegram.ext import ConversationHandler

# Константы для API трекера
VOLUNTEER = "VOLUNTEER"
SOCIAL = "SOCIAL"
POLLUTION = "POLLUTION"

SELECTING_ACTION = "select_action"
ADDING_VOLUNTEER = "adding_volunteer"
MAKING_DONATION = "making_donations"
ADDING_ECO_TASK = "adding_eco_task"
ADDING_SOCIAL_TASK = "adding_social_task"
SELECTING_FEATURE = "selecting_feature"

# Обозначим состояния второго диалога второго уровня
SPECIFY_ACTIVITY_RADIUS = "radius"
SPECIFY_CAR_AVAILABILITY = "has_car"
TYPING_ADDRESS = "typing_address"
TYPING_RADIUS = "typing_radius"
TYPING = "TYPING"
SOCIAL_PROBLEM_TYPING = "social_problem_typing"
SOCIAL_PROBLEM_ADDRESS = "social_problem_address"
SELECTING_OVER = "selecting_address"
DADATA_UNAVAILABLE = "dadata_unavailable"

# Состояния диалога Получение Телефонного номера
SPECIFY_PHONE_PERMISSION = "phone"
RETURN_DATA = "return_data"


# Meta состояния
STOPPING = "stopping"
SHOWING = "showing"

# Ярлык for ConversationHandler.END
END = ConversationHandler.END

# Различные константы для проекта
NO_COMMENT_PHASE = "Комментариев не оставили"
ADD_POLLUTION_TAG = "ADD_POLLUTION_TAG"
ADD_SOCIAL_TAG = "ADD_SOCIAL_TAG"
TAG_ID = "tag_id"
TAG_BUTTON_CALLBACK_PREFIX = f"{TAG_ID}="
TAG_ID_PATTERN_RAW = f"{TAG_ID}=(?P<{TAG_ID}>.*)"
TAG_ID_PATTERN = re.compile(TAG_ID_PATTERN_RAW)
NO_TAG = "NO_TAG"
TAGS = "tags"
POLLUTION_TAGS = "POLLUTION_TAGS"
SOCIAL_TAGS = "SOCIAL_TAGS"
LONGITUDE = "longitude"
LATITUDE = "latitude"
GEOM = "geometry"
FILE_PATH = "file_path"
START_OVER = "start_over"
IS_EXISTS = "is_exists"
FEATURES = "features"
CURRENT_FEATURE = "current_feature"
CURRENT_LEVEL = "current_level"
ADDRESS_COMMAND = "CITY="
ADDRESS_TEMPORARY = "address_temporary"
UNRESTRICTED_ADDRESS = "unrestricted_address"
RADIUS_COMMAND = "RADIUS="
CAR_COMMAND = "CAR="
POLLUTION_FOTO = "photo"
POLLUTION_COORDINATES = "pollution_coordinates"
POLLUTION_COMMENT = "comment"
SOCIAL_COMMENT = "comment"
COMMENT = "comment"
SAVE = "save"
ACTIVITY_RADIUS = [
    list(range(5, 30, 5)),
    list(range(30, 110, 20)),
    list(range(100, 250, 50)),
]
TELEGRAM_ID = "telegram_id"
TELEGRAM_USERNAME = "telegram_username"
FIRST_NAME = "first_name"
LAST_NAME = "last_name"
ADDRESS_INPUT = "address_input"
BACK = "back"
ADDRESS = "full_address"
VALIDATE = "validate"
PHONE_INPUT = "phone_input"
PHONE_COMMAND = "phone="

# Различные сообщения пользователю

GREETING_MESSAGE = (
    "Я бот экологического проекта «Дело живёт»."
    " Я могу принять заявку на помощь, или зарегистрировать тебя волонтёром."
    " Выбери, что хочешь сделать:"
)

FEATURES_DESCRIPTION = (
    "- Свой адрес, можно без квартиры, для удобства расчетов расстояния;\n"
    "- Расстояние, на которое ты готов выезжать;\n"
    "- Наличие автомобиля, и готовность задействовать его;\n"
    "- [Опционально] Номер телефона для связи."
)

REGISTER_GREETING = "Для регистрации волонтером вам надо указать:\n"
EDIT_PROFILE_GREETING = "Выберите данные для изменения:\n"

TOP_LEVEL_MENU_TEXT = "Можно выбрать новое действие или закончить разговор, набрав команду /stop"

SECOND_LEVEL_TEXT_BASE = "Понял-принял! Укажите информацию для остальных пунктов или нажмите на кнопку " "<b>{}</b>{}:"
SECOND_LEVEL_TEXT = SECOND_LEVEL_TEXT_BASE.format("Отправить заявку", " (она появится, когда всё будет заполнено)")
SECOND_LEVEL_UPDATE_TEXT = SECOND_LEVEL_TEXT_BASE.format("Сохранить", "")


CHECK_MARK = "\U00002705"  # Эмодзи галочки

HELP_TEXT = (
    "«Дело Живёт» помогает волонтёрам узнать, где требуется их помощь и организует локальные команды "
    "для решения экологических проблем.\n"
    "Наш бот может принять заявку на помощь и зарегистрировать тебя волонтёром.\n"
    "Присоединяйся!\n"
    "Подробнее на сайте: {site_info}"
)
SITE_INFO = "https://delozhivet.ru/"

STOP_TEXT = "Всего доброго! Отправь /start, когда я снова понадоблюсь."
