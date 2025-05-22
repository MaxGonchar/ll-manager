from extensions import db
from models.models import User
from repository.exceptions import UserAlreadyExistsException


from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


class UsersDAO:
    def __init__(self):
        self.session: Session = db.session

    def get_by_id(self, user_id: str) -> User | None:
        return self.session.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> User | None:
        return self.session.query(User).filter(User.email == email).first()

    def post(self, user: User):
        try:
            self.session.add(user)
            self.session.commit()
        except IntegrityError:
            raise UserAlreadyExistsException