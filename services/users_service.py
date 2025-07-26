from typing import Optional
from uuid import uuid4

from dao.user_dao import UsersDAO
from models.models import User
from helpers.hash_helper import hash_psw, is_psw_matching
from helpers.time_helpers import get_current_utc_time
from constants import Role
from services.exceptions import (
    UserNotFoundException,
    PasswordDoesntMatchException,
)

DEFAULT_USER_PROPERTIES = {
    "nativeLang": "uk",
    "challenges": {
        "dailyTraining": {
            "learnListSize": 50,
            "practiceCountThreshold": 50,
            "knowledgeLevelThreshold": 0.9,
            "learning_list": [],
        }
    },
}


class UsersService:
    def __init__(self):
        self.repo = UsersDAO()

    def create_user(
        self,
        email: str,
        password: str,
        first: Optional[str],
        last: Optional[str],
        role: str = Role.SELF_EDUCATED.value,
    ) -> User:
        user = User(
            id=str(uuid4()),
            email=email,
            password_hash=hash_psw(password),
            role=role,
            first=first,
            last=last,
            properties=DEFAULT_USER_PROPERTIES,
            added=get_current_utc_time(),
            updated=get_current_utc_time(),
            last_login=get_current_utc_time(),
        )
        self.repo.post(user)

        return user

    def login(self, email: str, psw: str) -> User:
        if not (user := self.repo.get_by_email(email)):
            raise UserNotFoundException

        if not is_psw_matching(psw, user.password_hash):
            raise PasswordDoesntMatchException

        user.last_login = get_current_utc_time()
        self.repo.post(user)

        return user
