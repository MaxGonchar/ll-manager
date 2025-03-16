from extensions import db
from models.models import Dialogue
from sqlalchemy.orm import Session


class DialogueTrainingRepo:
    def __init__(self, user_id: str):
        self.session: Session = db.session
        self.user_id = user_id

    def get(self, dialogue_id: str | None = None) -> list[Dialogue] | Dialogue:
        if dialogue_id:
            return self.session.query(Dialogue).filter(Dialogue.id == dialogue_id).first()
        return self.session.query(Dialogue.id, Dialogue.title, Dialogue.description).all()


    def create(self, dialogue: Dialogue):
        self.session.add(dialogue)
        self.session.commit()


    def update(self, user_id: str, dialogue: Dialogue) -> None:
        # update dialogue
        pass

    def delete(self, dialogue_id: str) -> None:
        self.session.query(Dialogue).filter(Dialogue.id == dialogue_id).delete()
        self.session.commit()
