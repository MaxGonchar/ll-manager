from flask import session

from models.models import User


def start_session(user: User) -> None:
    session["user_id"] = str(user.id)
    session["user"] = user.email


def clear_session() -> None:
    session.clear()
