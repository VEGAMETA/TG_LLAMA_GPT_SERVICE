import enum

gpt_requests = {}


class GPTRequestStatus(enum.Enum):
    Stopped = 0
    Processing = 1
    StopRequest = 2
