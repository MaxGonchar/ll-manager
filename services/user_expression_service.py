from typing import List, Optional, TypedDict
from uuid import uuid4

from repository.user_expressions_repo import UserExpressionsRepo
from models.models import Expression, UserExpression
from repository.users_repo import UsersRepo
from repository.tags_repo import TagsRepo
from helpers.time_helpers import get_current_utc_time
from exercises.daily_training_v2 import DailyTraining
from services.exceptions import (
    UserNotFoundException,
    TagNotFoundException,
    UserExpressionNotFoundException,
    InvalidPostUserExpressionDataException,
)


class UserExpressionListItem(TypedDict):
    expressionId: str
    expression: str
    knowledgeLevel: float
    practiceCount: int
    lastPracticeTime: str
    isInLearnList: bool


class UserExpressionType(TypedDict):
    expression: str
    definition: str
    translation: Optional[str]
    tags: List[str]


class UserExpressionService:
    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        self.repo = UserExpressionsRepo(user_id)

    def get_expression_by_id(self, expr_id: str) -> UserExpressionType:
        if not (expr := self.repo.get_by_id(expr_id)):
            raise UserExpressionNotFoundException
        return self._format(expr)

    def get_all(self) -> List[UserExpressionListItem]:
        return self._format_list(self.repo.get())

    def search(self, pattern: str) -> List[UserExpressionListItem]:
        return self._format_list(self.repo.search(pattern))

    def post_expression(
        self,
        expression: str,
        definition: str,
        translation: str,
        example: str,
        tag_names: List[str],
        properties: dict = {},
    ) -> None:

        if not (user := UsersRepo().get_by_id(self.user_id)):
            raise UserNotFoundException

        tags = []
        for tag_name in tag_names:
            if not (tag := TagsRepo().get_by_name(tag_name)):
                raise TagNotFoundException
            tags.append(tag)

        if not tags:
            raise InvalidPostUserExpressionDataException(
                "Expression to be posted has to have at least one tag"
            )

        expr_id = str(uuid4())
        current_utc_time = get_current_utc_time()

        expr = Expression(
            id=expr_id,
            expression=expression,
            definition=definition,
            translations={user.properties["nativeLang"]: translation},
            example=example,
            added=current_utc_time,
            updated=current_utc_time,
            tags=tags,
            properties=properties,
        )

        user_expr = UserExpression(
            expression=expr,
            user=user,
            active=1,
            added=current_utc_time,
            updated=current_utc_time,
        )

        self.repo.post(user_expr)

        DailyTraining(self.user_id).refresh_learning_list()

    def count_user_expressions(self) -> int:
        return self.repo.count()

    def _format_list(
        self,
        us_exprs: List[UserExpression],
    ) -> List[UserExpressionListItem]:
        dt = DailyTraining(self.user_id)
        return [
            {
                "expressionId": str(expr.expression_id),
                "expression": expr.expression.expression,
                "knowledgeLevel": expr.knowledge_level,
                "practiceCount": expr.practice_count,
                "lastPracticeTime": expr.last_practice_time,
                "isInLearnList": dt.is_expression_in_learn_list(
                    str(expr.expression_id)
                ),
            }
            for expr in us_exprs
        ]

    @staticmethod
    def _format(usr_expr: UserExpression) -> UserExpressionType:
        return {
            "expression": usr_expr.expression.expression,
            "definition": usr_expr.expression.definition,
            "translation": usr_expr.expression.translation(
                usr_expr.user.native_lang
            )
            or "no translation",
            "tags": [tag.tag for tag in usr_expr.expression.tags],
            "examples": [item.sentence for item in usr_expr.expression.context]
        }
