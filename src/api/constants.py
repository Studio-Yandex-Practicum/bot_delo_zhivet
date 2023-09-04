from enum import Enum


class VOLUNTEER_STATUS(Enum):
    otpusk = "otpusk"
    open = "open"
    closed = "closed"


class QUEUE(Enum):
    VOLUNTEER = "VOLUNTEER"
    SOCIAL = "SOCIAL"
    POLLUTION = "POLLUTION"


class LOGGER_API_EVENTS(Enum):
    bulk_remove_tag = "Bulk remove tag"
    bulk_update_tag = "Bulk update tag"
    cant_remove_tag = "Can't remove tag"
    tag_is_removed = "Tag successfully removed from queue"


class LOGGER_API_PROBLEMS(Enum):
    issues_in_queue = "There are issues with tag in queue."
    unprocessable_entity = "Tracker ServerError: Unprocessable entity"
