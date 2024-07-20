from typing import TypedDict, List
from uuid import uuid4
from models.models import ExpressionContext
from repository.expression_context_repo import ExpressionContextRepo
from helpers.time_helpers import get_current_utc_time


class TemplateType(TypedDict):
    tpl: str
    values: List[str]


class ExpressionContextType(TypedDict):
    id: str
    sentence: str
    translation: str
    template: TemplateType


class ExpressionContextService:
    def __init__(self, expression_id: str) -> None:
        self.expression_id = expression_id
        self.repo = ExpressionContextRepo(expression_id)

    def post_context(
        self, sentence: str, translation: str, template: TemplateType
    ) -> None:
        added = get_current_utc_time()
        self.repo.post(
            ExpressionContext(
                id=str(uuid4()),
                expression_id=self.expression_id,
                sentence=sentence,
                translation={"uk": translation},
                template=template,
                added=added,
                updated=added,
            )
        )

    def get_context(self) -> List[ExpressionContext]:
        context = self.repo.get()
        return [self._format_context(item) for item in context]

    @staticmethod
    def _format_context(context: ExpressionContext) -> ExpressionContextType:
        return {
            "id": context.id,
            "sentence": context.sentence,
            "template": context.template,
            "translation": context.translation["uk"],
        }
