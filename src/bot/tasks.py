from asyncio import run

from celery import Celery
from telegram import Update
from telegram.ext import ContextTypes

from src.core.config import settings
from src.bot.handlers.state_constants import START_OVER, FEATURES
from src.bot.handlers.common import end_describing
from src.bot.handlers.social import save_and_exit_from_social_problem
from src.bot.handlers.pollution import save_and_exit_pollution
from src.bot.handlers.volunteer import save_and_exit_volunteer

celery = Celery(
    main='delo_zhivet',
    backend=settings.celery_result_backend,
    broker=settings.celery_broker_url,
)


@celery.task(name='bot.tasks.save_social_problem_task')
def save_social_problem_task(
        user_id: int,
        username: str,
        user_data,
) -> None:
    run(save_and_exit_from_social_problem(user_id, username, user_data))


async def save_social_problem(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
) -> int:
    context.user_data[START_OVER] = True
    save_social_problem_task.delay(
        update.effective_user.id,
        update.effective_user.username,
        context.user_data[FEATURES]
    )
    return await end_describing(update, context)


@celery.task(name='bot.tasks.save_pollution_task')
def save_pollution_task(
        user_id: int,
        username: str,
        user_data,
) -> None:
    run(save_and_exit_pollution(user_id, username, user_data))


async def save_pollution(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
) -> int:
    context.user_data[START_OVER] = True
    save_pollution_task.delay(
        update.effective_user.id,
        update.effective_user.username,
        context.user_data[FEATURES]
    )
    return await end_describing(update, context)


@celery.task(name='bot.tasks.save_volunteer_task')
def save_volunteer_task(
        user_id: int,
        username: str,
        first_name: str,
        last_name: str,
        user_data,
) -> None:
    run(save_and_exit_volunteer(
        user_id,
        username,
        first_name,
        last_name,
        user_data,
    ))


async def save_volunteer(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
) -> int:
    context.user_data[START_OVER] = True
    save_volunteer_task.delay(
        update.effective_user.id,
        update.effective_user.username,
        update.effective_user.first_name,
        update.effective_user.last_name,
        context.user_data[FEATURES],
    )
    return await end_describing(update, context)
