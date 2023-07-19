from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.exceptions import DadataUnavailabilityError
from bot.handlers.state_constants import (
    ADDRESS_TEMPORARY,
    CURRENT_FEATURE,
    SELECTING_OVER,
    TYPING_ADDRESS,
    UNRESTRICTED_ADDRESS,
)
from bot.keyboards import ADDRESS_FOUND_KB, ADDRESS_NOT_FOUND_KB, BACK_KB, DADATA_UNAVAILABLE_KB
from bot.service.dadata import get_fields_from_dadata


async def ask_for_input_address(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
    """Предложить пользователю ввести данные о населенном пункте."""
    context.user_data[CURRENT_FEATURE] = update.callback_query.data
    await update.callback_query.edit_message_text(
        text="Укажите адрес:",
        reply_markup=BACK_KB,
    )

    return TYPING_ADDRESS


async def address_processor(
    unrestricted_address: str,
    context: ContextTypes.DEFAULT_TYPE,
) -> tuple[str, InlineKeyboardMarkup]:
    """
    Процесс проверки адреса и добавления данных в контекст.
    Возвращает текст сообщения и клавиатуру.
    """
    try:
        address = await get_fields_from_dadata(unrestricted_address)
    except DadataUnavailabilityError:
        context.user_data[ADDRESS_TEMPORARY] = {
            UNRESTRICTED_ADDRESS: unrestricted_address,
        }
        text = "Сервис временно недоступен, пожалуйста, попробуйте позже."
        keyboard = DADATA_UNAVAILABLE_KB
    else:
        if address is not None:
            text = (
                f"Это правильный адрес: {address['full_address']}? "
                'Если адрес не правильный, то выберите "Нет" '
                "и укажите более подробный вариант адреса, "
                "а мы постараемся определить его правильно!"
            )
            context.user_data[ADDRESS_TEMPORARY] = address
            keyboard = ADDRESS_FOUND_KB
        else:
            text = "Не нашли такой адрес. Пожалуйста, укажите адрес подробнее:"
            keyboard = ADDRESS_NOT_FOUND_KB

    return text, keyboard


async def address_confirmation(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
    """Обработчик данных о населенном пункте с ручного ввода."""
    unrestricted_address = update.message.text
    text, keyboard = await address_processor(unrestricted_address, context)

    await update.message.reply_text(text=text, reply_markup=keyboard)

    return SELECTING_OVER


async def retry_address_confirmation(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str:
    """Обработчик данных о населенном пункте при повторной попытке."""
    unrestricted_address = context.user_data[ADDRESS_TEMPORARY][UNRESTRICTED_ADDRESS]
    text, keyboard = await address_processor(
        unrestricted_address,
        context,
    )
    if text == update.callback_query.message.text:
        await update.callback_query.answer("Сервис недоступен")
    else:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=keyboard,
        )

    return SELECTING_OVER
