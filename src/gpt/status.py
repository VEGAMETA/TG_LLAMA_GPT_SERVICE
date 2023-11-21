import enum


class RequestStatus(enum.Enum):
    NONE = 0
    PROCESSING = 1
    STOP_REQUEST = 2
