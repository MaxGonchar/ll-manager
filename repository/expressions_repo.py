from typing import List
from models.models import Expression
from extensions import db
from sqlalchemy.orm import Session, attributes


class ExpressionsRepo:
    def __init__(self):
        self.session: Session = db.session

    def get(self) -> List[Expression]:
        return (
            self.session.query(Expression)
            .order_by(Expression.added.desc())
            .all()
        )

    def get_by_id(self, expression_id: str) -> Expression:
        return (
            self.session.query(Expression)
            .filter(Expression.id == expression_id)
            .first()
        )

    def search(self, pattern: str) -> List[Expression]:
        return (
            self.session.query(Expression)
            .filter(
                Expression.expression.match(pattern),
            )
            .order_by(Expression.added.desc())
            .all()
        )

    def update(self, expression: Expression) -> None:
        attributes.flag_modified(expression, "properties")
        self.session.add(expression)
        self.session.commit()
