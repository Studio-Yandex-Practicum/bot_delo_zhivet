from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.state_constants import ADDRESS_COMMAND, ADDRESS_INPUT, BACK, DADATA_UNAVAILABLE

# Buttons
BACK_BTN = InlineKeyboardButton(text="Назад", callback_data=BACK)
RETRY_BTN = InlineKeyboardButton(
    text="Попробовать еще раз",
    callback_data=DADATA_UNAVAILABLE,
)
CONFIRM_ADDRESS_BTN = InlineKeyboardButton(
    text="Да",
    callback_data=ADDRESS_COMMAND,
)
CANCEL_ADDRESS_BTN = InlineKeyboardButton(
    text="Нет",
    callback_data=ADDRESS_INPUT,
)
RETRY_INPUT_ADDRESS_BTN = InlineKeyboardButton(
    text="Указать адрес заново",
    callback_data=ADDRESS_INPUT,
)

# Keyboards
BACK = InlineKeyboardMarkup(
    [
        [BACK_BTN],
    ]
)
DADATA_UNAVAILABLE = InlineKeyboardMarkup(
    [
        [RETRY_BTN],
        [BACK_BTN],
    ],
)
ADDRESS_FOUND = InlineKeyboardMarkup(
    [
        [CONFIRM_ADDRESS_BTN, CANCEL_ADDRESS_BTN],
        [BACK_BTN],
    ]
)
ADDRESS_NOT_FOUND = InlineKeyboardMarkup(
    [
        [RETRY_INPUT_ADDRESS_BTN],
        [BACK_BTN],
    ]
)
