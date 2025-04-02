from models.models import UserExpression, Expression, ExpressionContext
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError
from extensions import db
from typing import List, Optional
from helpers.time_helpers import get_current_utc_time
from repository.exceptions import UserExpressionNotFoundException


class UserExpressionsRepo:
    def __init__(self, user_id: str) -> None:
        self.session: Session = db.session
        self.user_id = user_id

    def get_all_trained_expressions(self) -> List[UserExpression]:
        return (
            self.session.query(UserExpression)
            .filter(
                UserExpression.user_id == self.user_id,
                UserExpression.last_practice_time.is_not(None),
            )
            .order_by(UserExpression.last_practice_time.asc())
            .all()
        )

    def get_oldest_trained_expression(self) -> Optional[UserExpression]:
        return (
            self.session.query(UserExpression)
            .filter(
                UserExpression.user_id == self.user_id,
                UserExpression.last_practice_time.is_not(None),
            )
            .order_by(UserExpression.last_practice_time.asc())
            .first()
        )
    
    # TODO: combine with get_oldest_trained_expression
    def get_oldest_trained_expressions(self, limit: int) -> List[UserExpression]:
        return (
            self.session.query(UserExpression)
            .filter(
                UserExpression.user_id == self.user_id,
                UserExpression.last_practice_time.is_not(None),
            )
            .order_by(UserExpression.last_practice_time.asc())
            .limit(limit)
            .all()
        )
    
    def get_oldest_trained_expressions_with_excludes(self, limit: int, excludes: List[str]) -> List[UserExpression]:
        return (
            self.session.query(UserExpression)
            .filter(
                UserExpression.user_id == self.user_id,
                UserExpression.last_practice_time.is_not(None),
                UserExpression.expression_id.not_in(excludes),
            )
            .order_by(UserExpression.last_practice_time.asc())
            .limit(limit)
            .all()
        )

    def get_oldest_trained_expression_with_context(
        self,
    ) -> Optional[UserExpression]:
        return (
            self.session.query(UserExpression)
            .join(
                ExpressionContext,
                UserExpression.expression_id
                == ExpressionContext.expression_id,
            )
            .filter(
                UserExpression.user_id == self.user_id,
                UserExpression.last_practice_time.is_not(None),
            )
            .order_by(UserExpression.last_practice_time.asc())
            .first()
        )

    def count_trained_expressions(self) -> int:
        return (
            self.session.query(UserExpression)
            .filter(
                UserExpression.user_id == self.user_id,
                UserExpression.last_practice_time.is_not(None),
            )
            .count()
        )

    def count_trained_expressions_having_context(self) -> int:
        return (
            self.session.query(func.distinct(UserExpression.expression_id))
            .join(
                ExpressionContext,
                UserExpression.expression_id
                == ExpressionContext.expression_id,
            )
            .filter(
                UserExpression.user_id == self.user_id,
                UserExpression.last_practice_time.is_not(None),
            )
            .count()
        )

    def get(
        self,
        include: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> List[UserExpression]:

        if exclude and include:
            raise TypeError(
                "Only one argument can be accepted: include or exclude"
            )

        if exclude:
            return self._get_exclude(exclude, limit)
        elif include:
            return self._get_include(include)
        else:
            return self._get_all()

    def get_by_id(self, expression_id: str) -> Optional[UserExpression]:
        expr = (
            self.session.query(UserExpression)
            .filter(
                UserExpression.user_id == self.user_id,
                UserExpression.expression_id == expression_id,
            )
            .first()
        )

        return expr

    def post(self, user_expression: UserExpression) -> None:
        self._commit(user_expression)

    def put(self, user_expression: UserExpression) -> None:
        user_expression.updated = get_current_utc_time()
        try:
            self._commit(user_expression)
        except StaleDataError:
            raise UserExpressionNotFoundException

    def _put(self, user_expression: UserExpression) -> None:
        user_expression.updated = get_current_utc_time()
        self._commit(user_expression)

    def _commit(self, user_expression: UserExpression) -> None:
        self.session.add(user_expression)
        self.session.commit()

    def search(self, pattern: str) -> List[UserExpression]:
        return (
            self.session.query(UserExpression)
            .join(Expression)
            .filter(
                UserExpression.user_id == self.user_id,
                Expression.expression.match(pattern),
            )
            .order_by(UserExpression.added.desc())
            .all()
        )

    def count(self) -> int:
        return (
            self.session.query(UserExpression)
            .filter(UserExpression.user_id == self.user_id)
            .count()
        )

    def _get_include(self, include: List[str]) -> List[UserExpression]:
        return (
            self.session.query(UserExpression)
            .filter(
                UserExpression.user_id == self.user_id,
                UserExpression.expression_id.in_(include),
            )
            .all()
        )

    def _get_exclude(
        self, exclude: List[str], limit: Optional[int] = None
    ) -> List[UserExpression]:
        return (
            self.session.query(UserExpression)
            .filter(
                UserExpression.user_id == self.user_id,
                UserExpression.practice_count == 0,
                UserExpression.expression_id.not_in(exclude),
            )
            .order_by(UserExpression.added.desc())
            .limit(limit)
            .all()
        )

    def _get_all(self) -> List[UserExpression]:
        return (
            self.session.query(UserExpression)
            .filter(UserExpression.user_id == self.user_id)
            .order_by(UserExpression.added.desc())
            .all()
        )
