import enum
from src.models.gpt import Models, RequestStatus
from src.models.language import Languages, Language


class UserPermission(enum.Enum):
    NONE = 0
    REGULAR = 1
    ADVANCED = 2
    PRO = 3
    ADMIN = 5


# TODO: Rewrite whole models when hardware will be able (Postgres on docker(k8s))
class User:
    def __init__(self,
                 user_id: int,
                 context: list[int] = [],
                 model: Models = Models.MISTRAL,
                 language: Language = Languages.EN.value,
                 permission: UserPermission = UserPermission.NONE,
                 request_status: RequestStatus = RequestStatus.NONE,
                 server_id: int = 0) -> None:
        self.user_id = user_id
        self.context = context
        self.model = model
        self.language = language
        self.permission = permission
        self.request_status = request_status
        self.server_id = server_id

    def set_language(self, language: Languages) -> None:
        self.language = language

    @classmethod
    def create_user(cls, user_id) -> 'User':
        user = User(user_id)
        users[user_id] = user
        return user


users: dict[int, User] = {}
