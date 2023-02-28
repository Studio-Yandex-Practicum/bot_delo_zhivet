# Обозначим состояния главного менюSELECTING_ACTION
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
SPECIFY_CITY = "specify_city"
SPECIFY_ACTIVITY_RADIUS = "radius"
SPECIFY_CAR_AVAILABILITY = "has_car"
TYPING_CITY = "typing_city"
TYPING_SOCIAL_CITY = "typing_social_city"
TYPING_RADIUS = "typing_radius"
TYPING = "TYPING"
SOCIAL_PROBLEM_TYPING = "social_problem_typing"
SOCIAL_PROBLEM_ADDRESS = "social_problem_address"
SELECTING_OVER = "selecting_city"

# Meta состояния
STOPPING = "stopping"
SHOWING = "showing"

# Ярлык for ConversationHandler.END
END = ConversationHandler.END

# Различные константы для проекта
LONGITUDE = "longitude"
LATITUDE = "latitude"
GEOM = "geometry"
FILE_PATH = "file_path"
START_OVER = "start_over"
FEATURES = "features"
CURRENT_FEATURE = "current_feature"
CURRENT_LEVEL = "current_level"
CITY_COMMAND = "CITY="
CITY_SOCIAL = "SOCIAL_CITY="
RADIUS_COMMAND = "RADIUS="
CAR_COMMAND = "CAR="
POLLUTION_FOTO = "photo"
POLLUTION_COORDINATES = "pollution_coordinates"
POLLUTION_COMMENT = "comment"
SOCIAL_ADDRESS = "social_address"
SOCIAL_COMMENT = "comment"
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
SLEEP_TIME = 3
CITY_INPUT = "city_input"
BACK = "back"
CITY = "city"

# Различные сообщения пользователю

GREETING_MESSAGE = (
    'Привет, {username}. Я бот экологического проекта "Дело живёт".'
    " Я могу принять заявку на помощь, или зарегистрировать тебя волонтером."
    " Выбери необходимое действие."
)

TOP_LEVEL_MENU_TEXT = "Можно выбрать новое действие или закончить разговор, набрав команду /stop"

SECOND_LEVEL_TEXT = (
    "Понял-принял! Укажите информацию для остальных пунктов или нажмите на кнопку "
    "<b>Отправить заявку</b> (она появится, когда всё будет заполнено):"
)

HELP_TEXT = (
    "«Дело Живёт» помогает волонтёрам узнать, где требуется их помощь и организует локальные команды "
    "для решения экологических проблем.\n"
    "Наш бот может принять заявку на помощь и зарегистрировать тебя волонтёром.\n"
    "Присоединяйся!\n"
    "Подробнее на сайте: {site_info}"
)
SITE_INFO = (
    "https://delozhivet.ru/"
)
