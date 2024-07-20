from typing import List
from models.models import Tag
from extensions import db
from sqlalchemy.orm import Session


class TagsRepo:
    def __init__(self):
        self.session: Session = db.session

    def get_by_name(self, tag_name: str) -> Tag:
        return self.session.query(Tag).filter(Tag.tag == tag_name).first()

    def get_all(self) -> List[Tag]:
        return self.session.query(Tag).order_by(Tag.tag).all()
