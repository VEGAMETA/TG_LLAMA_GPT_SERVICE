import enum


class Models(enum.Enum):
    MISTRAL = "mistral"
    LLAMA2_UNCENSORED_7B = "llama2-uncensored:7b"
    LLAMA2_UNCENSORED_70B = "llama2-uncensored:70b"
    CODE_LLAMA_7B = "codellama:7b"
    CODE_LLAMA_34B = "codellama:34b"
    CODE_LLAMA_PYTHON_34B = "codellama:34b-python-q8_0"
