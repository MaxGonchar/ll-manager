from typing import List, Optional, TypedDict
import random

from helpers.time_helpers import get_current_utc_time
from models.models import UserExpression
from repository.expression_context_repo import ExpressionContextRepo
from repository.user_expressions_repo import UserExpressionsRepo
from exercises.exceptions import (
    ContextNotFoundException,
    ExpressionNotFoundException,
)
from exercises.common import calculate_knowledge_level, is_answer_correct


class SentenceTrainingChallenge(TypedDict):
    expressionId: str
    contextId: str
    sentence: str
    translation: str
    template: str
    values: List[str]


class SentenceTrainingChallengeSolution(TypedDict):
    correctAnswer: str
    usersAnswer: str


class SentenceTraining:
    def __init__(self, user_id: str) -> None:
        self.user_expr_repo: UserExpressionsRepo = UserExpressionsRepo(user_id)
        self.context_repo = ExpressionContextRepo

    def get_expressions_number_can_be_trained_in_sentence(self):
        return self.user_expr_repo.count_trained_expressions_having_context()

    def get_challenge(self) -> Optional[SentenceTrainingChallenge]:

        if not (
            user_expr := self.user_expr_repo.get_oldest_trained_expression_with_context()
        ):
            return

        data = random.choice(user_expr.expression.context)

        return {
            "expressionId": data.expression_id,
            "contextId": data.id,
            "sentence": data.sentence,
            "translation": data.translation["uk"],
            "template": data.template["tpl"],
            "values": data.template["values"],
        }

    def submit_challenge(
        self, expression_id: str, context_id: str, answer: str, hint: bool
    ) -> SentenceTrainingChallengeSolution:
        context = self.context_repo(expression_id).get_by_id(context_id)
        user_expr = self.user_expr_repo.get_by_id(expression_id)

        if user_expr is None:
            raise ExpressionNotFoundException

        if context is None:
            raise ContextNotFoundException

        correct = context.sentence

        if not hint:
            if is_answer_correct(correct, answer):
                self._register_challenge(user_expr, True)
            else:
                self._register_challenge(user_expr, False)

        return {"correctAnswer": correct, "usersAnswer": answer, "translation": context.translation["uk"]}

    def _register_challenge(
        self, user_expr: UserExpression, successful: bool
    ) -> None:
        user_expr.knowledge_level = calculate_knowledge_level(
            user_expr.knowledge_level, user_expr.practice_count, successful
        )
        user_expr.practice_count += 1
        user_expr.last_practice_time = get_current_utc_time()
        self.user_expr_repo.put(user_expr)
