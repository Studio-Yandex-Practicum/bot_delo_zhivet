from telegram.ext import CallbackQueryHandler, ConversationHandler

from src.bot.handlers.social import back_to_add_social
from src.bot.handlers.state_constants import ADD_SOCIAL_TAG, BACK, SAVE_TAG

from .callbacks import input_social_tag, save_social_tag_to_context

add_social_tag_conv = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(input_social_tag, pattern="^" + ADD_SOCIAL_TAG + "$"),
    ],
    states={
        SAVE_TAG: [CallbackQueryHandler(save_social_tag_to_context)],
    },
    fallbacks=[
        CallbackQueryHandler(back_to_add_social, pattern=BACK),
    ],
    persistent=True,
    name="add_social_tag_conv",
    allow_reentry=True,
)
