from ollama_bot.misc.user import UserPermission
from ollama_bot.misc.gpt import Models, RequestStatus
from ollama_bot.models.language import Languages, Language


# TODO: Postgres
class User:
    def __init__(self,
                 user_id: int,
                 context: list[int] = [],
                 model: Models = Models.LLAMA2_TEST,
                 language: Language = Languages.EN,
                 permission: UserPermission = UserPermission.REGULAR,
                 request_status: RequestStatus = RequestStatus.IDLE,
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

    def set_model(self, model: Models) -> None:
        self.model = model

    @classmethod
    def create_user(cls, user_id) -> 'User':
        user = User(user_id)
        users[user_id] = user
        return user


# Dummy
users: dict[int, User] = {}
