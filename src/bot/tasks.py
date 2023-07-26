from asyncio import run

from celery import Celery
from telegram import Update
from telegram.ext import ContextTypes

from src.api.tags_update import (
    assistance_disabled_traker_tag_updater, pollution_traker_tag_updater,
)
from src.bot.handlers.common import end_describing
from src.bot.handlers.pollution import save_and_exit_pollution
from src.bot.handlers.social import save_and_exit_from_social_problem
from src.bot.handlers.state_constants import FEATURES, IS_EXISTS, START_OVER
from src.bot.handlers.volunteer import save_and_exit_volunteer
from src.core.config import settings

celery_result_backend = settings.celery_connect_string.format(
    host := settings.redis_host,
    port := settings.redis_port,
)

celery_broker_url = settings.celery_connect_string.format(
    host := settings.redis_host,
    port := settings.redis_port,
)

celery = Celery(
    main="delo_zhivet",
    backend=celery_result_backend,
    broker=celery_broker_url,
)


@celery.task(name="tracker.tasks.task_bulk_remove_pollution_tag_in_tracker")
def task_bulk_remove_pollution_tag_in_tracker(old_tag_name: str, event_ticket_ids: list[str]) -> None:
    run(pollution_traker_tag_updater.bulk_remove_tag_from_queue(old_tag_name, event_ticket_ids))


@celery.task(name="tracker.tasks.task_bulk_remove_assistance_tag_in_tracker")
def task_bulk_remove_assistance_tag_in_tracker(old_tag_name: str, event_ticket_ids: list[str]) -> None:
    run(assistance_disabled_traker_tag_updater.bulk_remove_tag_from_queue(old_tag_name, event_ticket_ids))


@celery.task(name="tracker.tasks.task_bulkupdate_and_remove_pollution_tag_in_tracker")
def task_bulkupdate_and_remove_pollution_tag_in_tracker(
    old_tag_name: str, new_tag_name: str, event_ticket_ids: list[str]
) -> None:
    run(pollution_traker_tag_updater.bulkupdate_queue_and_remove_tag(old_tag_name, new_tag_name, event_ticket_ids))


@celery.task(name="tracker.tasks.task_bulkupdate_and_remove_assistance_tag_in_tracker")
def task_bulkupdate_and_remove_assistance_tag_in_tracker(
    old_tag_name: str, new_tag_name: str, event_ticket_ids: list[str]
) -> None:
    run(
        assistance_disabled_traker_tag_updater.bulkupdate_queue_and_remove_tag(
            old_tag_name, new_tag_name, event_ticket_ids
        )
    )


@celery.task(name="bot.tasks.save_social_problem_task")
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
        update.effective_user.id, update.effective_user.username, context.user_data[FEATURES]
    )
    return await end_describing(update, context)


@celery.task(name="bot.tasks.save_pollution_task")
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
    save_pollution_task.delay(update.effective_user.id, update.effective_user.username, context.user_data[FEATURES])
    return await end_describing(update, context)


@celery.task(name="bot.tasks.save_volunteer_task")
def save_volunteer_task(
    user_id: int,
    username: str,
    first_name: str,
    last_name: str,
    user_data: dict,
    volunteer_is_exists: bool,
) -> None:
    run(
        save_and_exit_volunteer(
            user_id,
            username,
            first_name,
            last_name,
            user_data,
            volunteer_is_exists,
        )
    )


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
        context.user_data[IS_EXISTS],
    )
    context.user_data.pop(IS_EXISTS, None)
    return await end_describing(update, context)
