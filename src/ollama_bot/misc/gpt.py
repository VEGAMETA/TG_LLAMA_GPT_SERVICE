import enum


class RequestStatus(enum.Enum):
    IDLE = 0
    PROCESSING = 1
    STOP_REQUEST = 2


class Models(enum.Enum):
    LLAMA2_TEST = "llama2"
    MIXTRAL = "dolphin-mixtral:v2.7"
    CODE_BOOGA = "codebooga:34b-v0.1-q8_0"
