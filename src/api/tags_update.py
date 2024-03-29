from yandex_tracker_client.exceptions import UnprocessableEntity

from src.api.constants import LOGGER_API_EVENTS, LOGGER_API_PROBLEMS, QUEUE
from src.api.tracker import client
from src.bot.handlers.loggers import PrintLogger, structlog
from src.core.db.model import (
    AbstractTag, Assistance_disabled, Pollution, Tag_Assistance, Tag_Pollution,
)

logger: PrintLogger = structlog.get_logger("tracker_tag_update")


class TrackerTagUpdater:
    """Класс для обновления тегов события в трекере"""

    def __init__(
        self, event_model: type[Pollution | Assistance_disabled], queue_name: str, tag_model: type[AbstractTag]
    ) -> None:
        self.event_model = event_model
        self.queue = queue_name
        self.tag_model = tag_model

    def bulk_remove_event_tag(self, old_tag_name: str, event_ticket_ids: list[str]) -> None:
        bulk_change = client.bulkchange.update(event_ticket_ids, tags={"remove": [old_tag_name]})
        logger.info(
            event=LOGGER_API_EVENTS.bulk_remove_tag.value,
            tag_name=old_tag_name,
            queue=self.queue,
            status=bulk_change.status,
        )
        bulk_change = bulk_change.wait()
        logger.info(
            event=LOGGER_API_EVENTS.bulk_remove_tag.value,
            tag_name=old_tag_name,
            queue=self.queue,
            status=bulk_change.status,
        )

    def bulk_update_event_tag(self, old_tag_name: str, new_tag_name: str, event_ticket_ids: list[str]) -> None:
        bulk_change = client.bulkchange.update(event_ticket_ids, tags={"remove": [old_tag_name], "add": [new_tag_name]})
        logger.info(
            event=LOGGER_API_EVENTS.bulk_update_tag.value,
            old_tag_name=old_tag_name,
            new_tag_name=new_tag_name,
            queue=self.queue,
            status=bulk_change.status,
        )
        bulk_change = bulk_change.wait()
        logger.info(
            event=LOGGER_API_EVENTS.bulk_update_tag.value,
            old_tag_name=old_tag_name,
            new_tag_name=new_tag_name,
            queue=self.queue,
            status=bulk_change.status,
        )

    def check_any_issues_with_tag_exist(self, tag_name: str) -> bool:
        issues = client.issues.find(filter={"queue": self.queue, "tags": tag_name})
        if issues == []:
            return False
        return True

    def remove_tag_from_tracker(self, tag_name: str) -> bool:
        if self.check_any_issues_with_tag_exist(tag_name):
            logger.info(
                event=LOGGER_API_EVENTS.cant_remove_tag.value,
                problem=LOGGER_API_PROBLEMS.issues_in_queue.value,
                tag_name=tag_name,
                queue=self.queue,
            )
            return False
        queue = client.queues[self.queue]
        try:
            queue.perform_action("tags/_remove", "post", tag=tag_name)
            logger.info(
                event=LOGGER_API_EVENTS.tag_is_removed.value,
                tag_name=tag_name,
                queue=self.queue,
            )
            return True
        except UnprocessableEntity as e:
            logger.info(
                event=LOGGER_API_EVENTS.cant_remove_tag.value,
                problem=LOGGER_API_PROBLEMS.unprocessable_entity.value,
                error=e,
                tag_name=tag_name,
                queue=self.queue,
            )
            return False

    async def bulk_remove_tag_from_queue(self, old_tag_name: str, event_ticket_ids: list[str]):
        self.bulk_remove_event_tag(old_tag_name, event_ticket_ids)
        self.remove_tag_from_tracker(old_tag_name)

    async def bulk_update_queue_and_remove_tag(self, old_tag_name: str, new_tag_name: str, event_ticket_ids: list[str]):
        self.bulk_update_event_tag(old_tag_name, new_tag_name, event_ticket_ids)
        self.remove_tag_from_tracker(old_tag_name)


pollution_traker_tag_updater = TrackerTagUpdater(
    Pollution,
    QUEUE.POLLUTION.value,
    Tag_Pollution,
)

assistance_disabled_traker_tag_updater = TrackerTagUpdater(
    Assistance_disabled,
    QUEUE.SOCIAL.value,
    Tag_Assistance,
)
