import enum
from aiogram.utils.markdown import hbold


class Language:
    def __init__(self, name: str, flag: str, dictionary: dict[str, str]):
        self.name = name
        self.flag = flag
        self.dictionary = dictionary


class Languages(enum.Enum):
    EN: Language = Language(
        name="English",
        flag="🇬🇧/🇺🇸",
        dictionary={
            "greeting": "Hello, ",
            "start": "\nI am gpt bot based on open-source models!\n"
                     "Feel free to ask any question.\n"
                     f"type {hbold('/help')} for info",
            "restart": f"Hello again!\nType {hbold('/help')} for info",
            "help": "List of commands",
            "clear": "Context cleared.",

            "set_model": "Please select a model",
            "set_model_after": "Model has beem chosen: ",

            "set_language": "Please select a language",
            "set_language_after": "English",
            "command_help": "Help",
            "command_stop": "Stop",
            "command_clear": "Clear context",
            "command_set_language": "Set language",
            "command_set_model": "Set model",
            "command_cancel": "Cancel"
        }
    )
    RU: Language = Language(
        name="Русский",
        flag="🇷🇺",
        dictionary={
            "greeting": "Здравствуйте, ",
            "start": "\nЯ gpt бот, собранный из моделей в открытом доступе!\n"
                     "Задавайте любой вопрос.\n"
                     f"Напишите {hbold('/help')} для отображения команд",
            "restart": f"И снова здравствуйте!\nНапишите {hbold('/help')} для отображения команд",
            "help": "Список команд",
            "clear": "Контекст очищен.",

            "set_model": "Пожалуйста, выберите модель",
            "set_model_after": "Выбранная модель: ",

            "set_language": "Пожалуйста, выберите язык",
            "set_language_after": "Русский",
            "command_help": "Помощь",
            "command_stop": "Остановить",
            "command_clear": "Очистить контекст",
            "command_set_language": "Изменить язык",
            "command_set_model": "Изменить модель",
        }
    )
    ISV: Language = Language(
        name="Medžuslovjansky\nМеджусловјанскы",
        flag="-",
        dictionary={
            "greeting": "",

        }
    )