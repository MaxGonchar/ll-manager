from extensions import db
from models.models import Writings
from sqlalchemy.orm import Session


class WritingsRepo:
    def __init__(self, user_id: str):
        self.session: Session = db.session
        self.user_id = user_id

    def add(self, writings: Writings) -> None:
        self.session.add(writings)
        self.session.commit()
    
    def get(self, writings_id: str) -> Writings | None:
        return (
            self.session.query(Writings)
            .filter(
                Writings.id == writings_id,
                Writings.user_id == self.user_id,
            )
            .first()
        )
    
    def delete(self, writings_id: str) -> None:
        self.session.query(Writings).filter(
            Writings.id == writings_id
        ).delete()
        self.session.commit()
