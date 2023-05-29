from telegram.ext import CallbackQueryHandler, ConversationHandler

from src.bot.handlers.pollution import (
    back_to_select_option_to_report_about_pollution,
)
from src.bot.handlers.state_constants import ADD_POLLUTION_TAG, BACK, SAVE_TAG

from .callbacks import input_pollution_tag, save_pollution_tag_to_context

add_pollution_tag_conv = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(input_pollution_tag, pattern="^" + ADD_POLLUTION_TAG + "$"),
    ],
    states={
        SAVE_TAG: [CallbackQueryHandler(save_pollution_tag_to_context)],
    },
    fallbacks=[
        CallbackQueryHandler(back_to_select_option_to_report_about_pollution, pattern=BACK),
    ],
    persistent=True,
    name="add_pollution_tag_conv",
    allow_reentry=True,
)
