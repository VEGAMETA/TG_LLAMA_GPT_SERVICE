from src.gpt.status import RequestStatus
from src.gpt.models import Models


# TODO: Rewrite whole models when hardware will be able (Postgres on docker(k8s))
class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.model = Models.MISTRAL
        self.request_status = RequestStatus.NONE
        self.context = []


def create_user(user_id):
    users[user_id] = User(user_id)


users: dict[int, User] = {}
