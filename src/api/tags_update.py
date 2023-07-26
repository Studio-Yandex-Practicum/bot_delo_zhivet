from yandex_tracker_client.exceptions import UnprocessableEntity

from src.api.constants import QUEUE
from src.api.tracker import client
from src.bot.handlers.loggers import PrintLogger, structlog
from src.core.db.model import (
    AbstractTag, Assistance_disabled, Pollution, Tag_Assistance, Tag_Pollution,
)

logger: PrintLogger = structlog.get_logger("tracker_tag_update")


class TrackerTagUpdater:
    """Класс для обновления тегов события в трекере"""

    def __init__(self, event_model: Pollution | Assistance_disabled, queue_name: str, tag_model: AbstractTag) -> None:
        self.event_model = event_model
        self.event_model = event_model
        self.queue = queue_name
        self.tag_model = tag_model

    def bulk_remove_event_tag(self, old_tag_name: str, event_ticket_ids: list[str]) -> None:
        bulk_change = client.bulkchange.update(event_ticket_ids, tags={"remove": [old_tag_name]})
        logger.info(f"Bulk remove tag: from {old_tag_name}  in {self.queue}. Status: {bulk_change.status}")
        bulk_change = bulk_change.wait()
        logger.info(f"Bulk remove tag: from {old_tag_name}  in {self.queue}. Status: {bulk_change.status}")

    def bulkupdate_event_tag(self, old_tag_name: str, new_tag_name: str, event_ticket_ids: list[str]) -> None:
        bulk_change = client.bulkchange.update(event_ticket_ids, tags={"remove": [old_tag_name], "add": [new_tag_name]})
        logger.info(
            f"Bulk update tag: from {old_tag_name} to {new_tag_name} in {self.queue}. Status: {bulk_change.status}"
        )
        bulk_change = bulk_change.wait()
        logger.info(
            f"Bulk update tag: from {old_tag_name} to {new_tag_name} in {self.queue}. Status: {bulk_change.status}"
        )

    def chek_any_issues_with_tag_exist(self, tag_name: str) -> bool:
        issues = client.issues.find(filter={"queue": self.queue, "tags": tag_name})
        if issues == []:
            False
        True

    def remove_tag_from_tracker(self, tag_name: str) -> bool:
        if self.chek_any_issues_with_tag_exist(tag_name):
            logger.info(f"No issues with tag {tag_name} exist in queue {self.queue}")
            return False
        queue = client.queues[self.queue]
        try:
            queue.perform_action("tags/_remove", "post", tag=tag_name)
            logger.info(f"Tag {tag_name} successfully removed from queue {self.queue}")
            return True
        except UnprocessableEntity as e:
            logger.info(f"Tried to remove the tag {tag_name} from queue {self.queue}. Got {e}")
            return False

    async def bulk_remove_tag_from_queue(self, old_tag_name: str, event_ticket_ids: list[str]):
        self.bulk_remove_event_tag(old_tag_name, event_ticket_ids)
        self.remove_tag_from_tracker(old_tag_name)

    async def bulkupdate_queue_and_remove_tag(self, old_tag_name: str, new_tag_name: str, event_ticket_ids: list[str]):
        self.bulkupdate_event_tag(old_tag_name, new_tag_name, event_ticket_ids)
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
