from asyncio import run

from celery import Celery
from telegram import Update
from telegram.ext import ContextTypes

from src.core.config import settings
from .handlers.common import end_describing
from .handlers.social import save_and_exit_from_social_problem
from .handlers.pollution import save_and_exit_pollution
from .handlers.volunteer import save_and_exit_volunteer

celery = Celery(
    main='delo_zhivet',
    backend=settings.celery_result_backend,
    broker=settings.celery_broker_url,
)


@celery.task
def save_social_problem_task(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
) -> None:
    run(save_and_exit_from_social_problem(update, context))


async def save_social_problem(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
) -> int:
    save_social_problem_task.delay(update, context)
    return await end_describing(update, context)


@celery.task
def save_pollution_task(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
) -> None:
    run(save_and_exit_pollution(update, context))


async def save_pollution(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
) -> int:
    save_pollution_task.delay(update, context)
    return await end_describing(update, context)


@celery.task
def save_volunteer_task(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
) -> None:
    run(save_and_exit_volunteer(update, context))


async def save_volunteer(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
) -> int:
    save_volunteer_task.delay(update, context)
    return await end_describing(update, context)
