import enum
import logging


class Models(enum.Enum):
    LLAMA2_TEST = "llama2"
    MIXTRAL = "dolphin-mixtral:v2.7"
    CODE_BOOGA = "codebooga:34b-v0.1-q4_0"

    @classmethod
    def get_model_by_name(cls, name: str) -> str:
        """
        Returns model by given name.
        """
        for model in cls:
            if model.name == name:
                return model.value
        else:
            logging.warning("Language not found")
            return cls.LLAMA2_TEST.value
