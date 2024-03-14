import enum


class Models(enum.Enum):
    LLAMA2_TEST = "llama2"
    MIXTRAL = "dolphin-mixtral:v2.7"
    CODE_BOOGA = "codebooga:34b-v0.1-q8_0"
    
    @classmethod
    def get_model_by_name(cls, name: str) -> str:
        for model in cls:
            if model.name == name:
                return model.value
