from typing import Optional
from models.models import User
from extensions import db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from repository.exceptions import UserAlreadyExistsException


class UsersRepo:
    def __init__(self):
        self.session: Session = db.session

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.session.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.session.query(User).filter(User.email == email).first()

    def post(self, user: User):
        try:
            self.session.add(user)
            self.session.commit()
        except IntegrityError:
            raise UserAlreadyExistsException
