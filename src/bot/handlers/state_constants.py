# Обозначим состояния главного менюSELECTING_ACTION
from telegram.ext import ConversationHandler

SELECTING_ACTION = "select_action"
ADDING_VOLUNTEER = "adding_volunteer"
MAKING_DONATION = "making_donations"
ADDING_ECO_TASK = "adding_eco_task"
ADDING_SOCIAL_TASK = "adding_social_task"
SELECTING_FEATURE = "selecting_feature"

# Обозначим состояния второго диалога второго уровня
SPECIFY_CITY = "specify_city"
SPECIFY_ACTIVITY_RADIUS = "specify_activity_radius"
SPECIFY_CAR_AVAILABILITY = "specify_car_availability"
TYPING_CITY = "typing_city"
TYPING_RADIUS = "typing_radius"
TYPING = "TYPING"

SELECTING_OVER = "selecting_city"

# Meta состояния
STOPPING = "stopping"
SHOWING = "showing"

# Ярлык for ConversationHandler.END
END = ConversationHandler.END

# Различные константы для проекта
START_OVER = "start_over"
FEATURES = "features"
CURRENT_FEATURE = "current_feature"
CURRENT_LEVEL = "current_level"
CITY_COMMAND = "CITY="
RADIUS_COMMAND = "RADIUS="
CAR_COMMAND = "CAR="
POLLUTION_FOTO = "pollution_foto"
POLLUTION_COORDINATES = "pollution_coordinates"
POLLUTION_COMMENT = "pollution_comment"
SAVE = "save"
ACTIVITY_RADIUS = [
    list(range(5, 30, 5)),
    list(range(30, 110, 20)),
    list(range(100, 250, 50)),
]

# Различные сообщения пользователю

GREETING_MESSAGE = (
    'Привет, {username}. Я бот экологического проекта "Дело живёт".'
    " Я могу принять заявку на помощь, или зарегистрировать тебя волонтером."
    " Выбери необходимое действие."
)

TOP_LEVEL_MENU_TEXT = "Ты можешь выбрать необходимое действие или закончить разговор. Для отмены отправь /stop"
