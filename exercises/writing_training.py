from typing import TypedDict
from uuid import uuid4

from repository.writings_repo import WritingsRepo
from repository.user_expressions_repo import UserExpressionsRepo
from helpers.time_helpers import get_current_utc_time
from models.models import Writings
from services.assistant import VeniceAssistant


class WritingChallenge(TypedDict):
    writings: list[dict]
    expressions: list[dict]


DEFAULT_PROPERTIES = {
    "maxExpressionsToTrain": 10,
    "maxWritingsToStore": 10,
}


class WritingTraining:
    def __init__(
            self,
            user_id: str,
            writings_repo: WritingsRepo = WritingsRepo,
            user_expr_repo: UserExpressionsRepo = UserExpressionsRepo,
            assistant: VeniceAssistant = VeniceAssistant,
        ):
        self.user_id = user_id
        self.writings_repo = writings_repo(self.user_id)
        self.user_expr_repo = user_expr_repo(self.user_id)
        self.assistant = assistant()

    # for now we store only one writing training per user
    def get_writings(self) -> WritingChallenge:
        writings = self.writings_repo.get() or self._create_writings()
        return self._generate_writing_challenge(writings)

    def _create_writings(self) -> Writings:
        id_ = str(uuid4())
        writings = Writings(
            id=id_,
            user_id = self.user_id,
            properties=DEFAULT_PROPERTIES,
            writings=[],
            expressions=[],
            added=get_current_utc_time(),
            updated=get_current_utc_time()
        )
        writings = self._enrich_expressions(writings)
        self.writings_repo.add(writings)
        return writings
    
    def _enrich_expressions(self, writings: Writings) -> Writings:
        if (
            dif := int(writings.properties["maxExpressionsToTrain"])
            - len(writings.expressions)
        ) > 0:
            existing_expression_ids = [
                expression["id"] for expression in writings.expressions
            ]
            user_expressions_to_add = (
                self.user_expr_repo.get_trained_expressions(
                    limit=dif, excludes=existing_expression_ids
                )
            )
            writings.add_expressions(
                [
                    user_expression.expression
                    for user_expression in user_expressions_to_add
                ]
            )
            return writings

        return writings
    
    def _generate_writing_challenge(writings: Writings) -> WritingChallenge:
        return {
            "writings": writings.writings,
            "expressions": writings.expressions
        }
