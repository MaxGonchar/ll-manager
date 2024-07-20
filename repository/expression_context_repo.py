from typing import List, Optional

from extensions import db
from sqlalchemy.orm import Session
from models.models import ExpressionContext


class ExpressionContextRepo:
    def __init__(self, expression_id: str):
        self.expression_id = expression_id
        self.session: Session = db.session

    def post(self, context: ExpressionContext) -> None:
        self.session.add(context)
        self.session.commit()

    def get(self) -> List[ExpressionContext]:
        return (
            self.session.query(ExpressionContext)
            .filter(ExpressionContext.expression_id == self.expression_id)
            .order_by(ExpressionContext.added)
            .all()
        )

    def get_by_id(self, context_id: str) -> Optional[ExpressionContext]:
        return (
            self.session.query(ExpressionContext)
            .filter(ExpressionContext.id == context_id)
            .first()
        )
