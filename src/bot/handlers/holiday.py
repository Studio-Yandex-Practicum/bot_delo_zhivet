from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from .state_constants import FEATURES, HOLIDAY_START, START_OVER
from .volunteer import add_volunteer


async def endless_holiday_now_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    if HOLIDAY_START not in context.user_data[FEATURES]:
        context.user_data[FEATURES][HOLIDAY_START] = datetime.now().timestamp()
    else:
        context.user_data[FEATURES].pop(HOLIDAY_START)
    context.user_data[START_OVER] = True
    return await add_volunteer(update, context)


async def stop_holiday_now_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    if HOLIDAY_START not in context.user_data[FEATURES]:
        context.user_data[FEATURES][HOLIDAY_START] = None
    else:
        context.user_data[FEATURES].pop(HOLIDAY_START)
    context.user_data[START_OVER] = True
    return await add_volunteer(update, context)
