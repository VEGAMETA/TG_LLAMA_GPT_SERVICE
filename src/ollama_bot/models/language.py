import enum
import csv
from collections import defaultdict

columns = defaultdict(list)

with open('./src/resources/languages.csv', encoding="utf-8") as file:
    reader = csv.DictReader(file,  delimiter=";")
    for row in reader:
        for k, v in row.items():
            columns[k].append(v.replace("\\n", "\n"))


class Language:
    def __init__(self, name: str, flag: str, dictionary: dict[str, str]):
        self.name = name
        self.flag = flag
        self.dictionary = dictionary


class Languages(enum.Enum):
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
