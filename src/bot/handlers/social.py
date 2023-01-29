from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
)

from api.tracker import client
from bot.handlers.start import start
from bot.handlers.state_constants import (
    END,
    START_OVER,
    FEATURES,
    SELECTING_FEATURE,
    SOCIAL_COMMENT,
    SOCIAL_ADDRESS,
    SAVE,
    CURRENT_FEATURE,
    SOCIAL_PROBLEM_TYPING,
    SOCIAL,
    TELEGRAM_ID,
)
from src.bot.service.assistance_disabled import create_new_social


async def input_social_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавление информации"""

    # TODO: Если вбиваем адрес, нужна проверка корректности(или отдельная функция инпута адреса с проверкой)

    context.user_data[CURRENT_FEATURE] = update.callback_query.data
    text = "Отлично, что ты хочешь добавить?"
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text)

    return SOCIAL_PROBLEM_TYPING


async def save_social_problem_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_data[FEATURES][user_data[CURRENT_FEATURE]] = update.message.text
    user_data[START_OVER] = True

    return await report_about_social_problem(update, context)


async def report_about_social_problem(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> str:
    text = "Заполните данные об обращении"
    buttons = [
        [
            InlineKeyboardButton(text="Указать адрес", callback_data=SOCIAL_ADDRESS),
        ],
        [
            InlineKeyboardButton(
                text="Напишите комментарий", callback_data=SOCIAL_COMMENT
            )
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data=str(END)),
        ],
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    if not context.user_data.get(START_OVER):
        context.user_data[FEATURES] = {}
        text = "Пожалуйста, выберите функцию для добавления."
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        if check_data(context.user_data[FEATURES]) is True:
            buttons.append(
                [InlineKeyboardButton(text="Сохранить и выйти", callback_data=SAVE)]
            )
            keyboard = InlineKeyboardMarkup(buttons)

        text = "Готово! Пожалуйста, выберите функцию для добавления."
        if update.message is not None:
            await update.message.reply_text(text=text, reply_markup=keyboard)
        else:
            await update.callback_query.edit_message_caption(
                text, reply_markup=keyboard
            )

    context.user_data[START_OVER] = False
    return SELECTING_FEATURE


async def save_and_exit_from_social_problem(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Сохранение данных в базу и отправка в трекер"""
    context.user_data[START_OVER] = True
    user_data = context.user_data[FEATURES]
    user_data[TELEGRAM_ID] = update.effective_user.id
    city = user_data[SOCIAL_ADDRESS]
    comment = user_data[SOCIAL_COMMENT]
    client.issues.create(
        queue=SOCIAL, summary=city, description=comment,
    )
    create_new_social(user_data)
    await start(update, context)
    return END


def check_data(user_data):
    if SOCIAL_ADDRESS in user_data and SOCIAL_COMMENT in user_data:
        return True
    else:
        return False
