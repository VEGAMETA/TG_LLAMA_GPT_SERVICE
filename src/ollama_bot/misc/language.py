import csv
import enum
import logging
from collections import defaultdict

columns = defaultdict(list)

try:
    file = open('./src/resources/languages.csv', encoding="utf-8")
except FileNotFoundError:
    file = open('../src/resources/languages.csv', encoding="utf-8")
finally:
    reader = csv.DictReader(file,  delimiter=";")
    for row in reader:
        for k, v in row.items():
            columns[k].append(v.replace("\\n", "\n"))
    file.close()


class Language:
    """
    Default language class.
    """

    def __init__(self, name: str, flag: str, dictionary: dict[str, str]):
        self.name = name
        self.flag = flag
        self.dictionary = dictionary


class Languages(enum.Enum):
    """
    Languages enum.
    """
    EN: Language = Language(
        name="English",
        flag="🇬🇧/🇺🇸",
        dictionary=dict(zip(columns.get("Instance"), columns.get("English")))
    )
    RU: Language = Language(
        name="Русский",
        flag="🇷🇺",
        dictionary=dict(zip(columns.get("Instance"), columns.get("Russian")))
    )


async def get_language(name: str) -> "Language":
    """
    Returns dictionary by given name.
    """
    for language in Languages:
        if language.name == name:
            return language.value.dictionary
    else:
        logging.warning("Language not found")
        return Languages.EN.value.dictionary
