from enum import Enum


class VOLUNTEER_STATUS(Enum):
    otpusk = "otpusk"
    open = "open"
    closed = "closed"


class QUEUE(Enum):
    VOLUNTEER = "VOLUNTEER"
    SOCIAL = "SOCIAL"
    POLLUTION = "POLLUTION"
