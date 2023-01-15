from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler

from bot import const
from bot.handlers import state_constants


async def volunteer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Регистрация волонтера"""
    keyboard = [
        KeyboardButton(
            "Сообщите свой город",
        ),
        KeyboardButton("Сообщите радиус на который готовы выезжать"),
        KeyboardButton("У вас есть автомобиль, варианты: да/ нет"),
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text("Заполните информацию о себе", reply_markup=reply_markup)


async def volunteer_register_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Регистрация волонтера."""
    text = (
        "Пожалуйста, укажите свой город (населенный пункт),"
        " и расстояние на которое вы готовы выезжать, а также наличие автомобиля."
    )
    buttons = [
        [
            InlineKeyboardButton(text="Добавить населенный пункт", callback_data=state_constants.CITY),
        ],
        [
            InlineKeyboardButton(text="Указать радиус активности", callback_data=state_constants.ACTIVITY_RADIUS),
        ],
        [
            InlineKeyboardButton(text="Указать наличие автомобиля", callback_data=state_constants.CAR),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return state_constants.ADD_VOLUNTEER


async def ask_for_input_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Prompt user to input data for selected feature."""
    context.user_data[state_constants.CURRENT_FEATURE] = update.callback_query.data
    text = "Введите название населенного пункта"

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text)

    return state_constants.CITY


async def ask_for_active_radius(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Prompt user to input data for selected feature."""
    context.user_data[state_constants.CURRENT_FEATURE] = update.callback_query.data
    text = "Введите расстояние, на которые ты готовы выезжать"

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text)

    return state_constants.ACTIVITY_RADIUS


async def parse_and_save_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Обработчик для распознавания и сохранения ввода города."""
    user_data = context.user_data
    user_data[state_constants.FEATURES][user_data[state_constants.CURRENT_FEATURE]] = update.message.text

    user_data[state_constants.START_OVER] = True

    return await ask_for_input_city(update, context)


async def parse_and_save_active_radius(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Обработчик для распознавания и сохранения ввода города."""
    user_data = context.user_data
    user_data[state_constants.FEATURES][user_data[state_constants.CURRENT_FEATURE]] = update.message.text

    user_data[state_constants.START_OVER] = True

    return await ask_for_input_city(update, context)


add_volunteer_conv = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(volunteer_register_handler, pattern=const.BECOME_VOLUNTEER_CMD),
    ],
    states={
        state_constants.CITY: [CallbackQueryHandler(ask_for_input_city, pattern=const.SPECIFY_CITY)],
        state_constants.ACTIVITY_RADIUS: [],
    },
)
