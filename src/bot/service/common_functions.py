from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.handlers.state_constants import (
    ADDRESS_COMMAND,
    ADDRESS_INPUT,
    ADDRESS_TEMPORARY,
    BACK,
    CURRENT_FEATURE,
    SELECTING_OVER,
    TYPING_ADDRESS,
)
from bot.service.dadata import get_fields_from_dadata


async def ask_for_input_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Предложить пользователю ввести данные о населенном пункте."""
    context.user_data[CURRENT_FEATURE] = update.callback_query.data
    text = "Укажите адрес:"
    button = [[InlineKeyboardButton(text="Назад", callback_data=BACK)]]
    keyboard = InlineKeyboardMarkup(button)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return TYPING_ADDRESS


async def address_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Обработчик данных о населенном пункте с выводом возможных вариантов."""
    user_input = update.message.text
    address = get_fields_from_dadata(user_input)
    if address is not None:
        text = (
            f"Это правильный адрес: {address['full_address']}? "
            'Если адрес не правильный, то выберите "Нет" и укажите более подробный вариант адреса, '
            "а мы постараемся определить его правильно!"
        )
        context.user_data[ADDRESS_TEMPORARY] = address

        buttons = [
            [
                InlineKeyboardButton(text="Да", callback_data=ADDRESS_COMMAND),
                InlineKeyboardButton(text="Нет", callback_data=ADDRESS_INPUT),
            ],
            [InlineKeyboardButton(text="Назад", callback_data=BACK)],
        ]

        keyboard = InlineKeyboardMarkup(buttons)

        await update.message.reply_text(text=text, reply_markup=keyboard)

    else:
        chat_text = "Не нашли такой адрес. Пожалуйста, укажи адрес подробнее:"
        buttons = [
            [
                InlineKeyboardButton(text="Указать адрес заново", callback_data=ADDRESS_INPUT),
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data=BACK),
            ],
        ]

        keyboard = InlineKeyboardMarkup(buttons)

        await update.message.reply_text(text=chat_text, reply_markup=keyboard)

    return SELECTING_OVER
