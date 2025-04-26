from typing import List, Optional, cast
from typing_extensions import TypedDict
from repository.expressions_repo import ExpressionsRepo
from repository.tags_repo import TagsRepo
from models.models import Expression
from itertools import zip_longest
from services.exceptions import (
    ExpressionNotFoundException,
    TagNotFoundException,
    InvalidUpdateExpressionDataException,
)
from helpers.time_helpers import get_current_utc_time
from constants import GrammarTag


class ExpressionsListItemType(TypedDict):
    id: str
    expression: str


class ExpressionType(TypedDict):
    id: str
    expression: str
    definition: str
    translation: str
    example: str

    grammar: Optional[str]
    grammar_tag: Optional[str]

    tag_1: str
    tag_2: Optional[str]
    tag_3: Optional[str]
    tag_4: Optional[str]
    tag_5: Optional[str]


class ExpressionService:
    def __init__(self):
        self.expressions_repo: ExpressionsRepo = ExpressionsRepo()
        self.tags_repo: TagsRepo = TagsRepo()

    def get_expression_by_id(self, expression_id: str) -> ExpressionType:
        expr = self.expressions_repo.get_by_id(expression_id)

        if not expr:
            raise ExpressionNotFoundException

        return self._format_expression(expr)

    def get_expression(self, expression_id) -> Expression:
        expr = self.expressions_repo.get_by_id(expression_id)

        if not expr:
            raise ExpressionNotFoundException

        return expr

    def get_expressions(self):
        exprs = self.expressions_repo.get()
        return [
            {
                "id": str(expr.id),
                "expression": expr.expression,
            }
            for expr in exprs
        ]

    def search(self, pattern: str) -> List[ExpressionsListItemType]:
        return self._format_expressions_list(
            self.expressions_repo.search(pattern)
        )

    def update_expression(
        self,
        expression_id: str,
        expression: str,
        definition: str,
        translation: str,
        example: str,
        tag_names: List[str],
        properties: dict = {},
    ) -> None:

        tags = []
        for tag_name in tag_names:
            if not (tag := self.tags_repo.get_by_name(tag_name)):
                raise TagNotFoundException
            tags.append(tag)

        if not tags:
            raise InvalidUpdateExpressionDataException(
                "Expression to be posted has to have at least one tag"
            )

        expr_to_update = self.expressions_repo.get_by_id(expression_id)

        expr_to_update.expression = expression
        expr_to_update.definition = definition
        expr_to_update.example = example
        expr_to_update.translations = {"uk": translation}
        expr_to_update.properties = properties
        expr_to_update.tags = tags
        expr_to_update.updated = get_current_utc_time()

        self.expressions_repo.update(expr_to_update)

    def _format_expressions_list(
        self, exprs: List[Expression]
    ) -> List[ExpressionsListItemType]:
        return [self._format_expressions_list_item(expr) for expr in exprs]

    @staticmethod
    def _format_expressions_list_item(
        expr: Expression,
    ) -> ExpressionsListItemType:
        return {
            "id": str(expr.id),
            "expression": expr.expression,
        }

    @staticmethod
    def _format_expression(expr: Expression) -> ExpressionType:
        grammar = None
        grammar_tag = None

        if expr.properties.get("grammar"):
            grammar_tag, grammar = list(
                expr.properties.get("grammar").items()
            )[0]
            grammar = grammar["text"]
            grammar_tag = GrammarTag.new_from_key(grammar_tag).display  # type: ignore

        rez = {
            "id": expr.id,
            "expression": expr.expression,
            "definition": expr.definition,
            "example": expr.example,
            "translation": expr.translation("uk"),
            "grammar": grammar,
            "grammar_tag": grammar_tag,
        }

        tags = {}
        tag_fields = ("tag_1", "tag_2", "tag_3", "tag_4", "tag_5")
        tags = expr.tags[
            : len(tag_fields)
        ]  # TODO: restrict expression to have no more than 5 tags

        for field, tag in zip_longest(tag_fields, tags):
            rez[field] = tag.tag if tag else None

        rez = cast(ExpressionType, rez)

        return rez
