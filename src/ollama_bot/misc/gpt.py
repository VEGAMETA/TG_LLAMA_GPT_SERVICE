import enum


class RequestStatus(enum.Enum):
    IDLE = 0
    PROCESSING = 1
    STOP_REQUEST = 2


class Models(enum.Enum):
    MIXTRAL = "dolphin-mixtral:v2.7"
    LLAMA2 = "llama2-uncensored:70b"
    LLAMA2_TEST = "llama2"
    CODE_LLAMA = "codellama:70b-code"
