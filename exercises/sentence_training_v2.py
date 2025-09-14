from typing import List, Optional, TypedDict
import random

from models.models import UserExpression, ExpressionContext
from exercises.exceptions import (
    ContextNotFoundException,
    ExpressionNotFoundException,
)
from exercises.common import is_answer_correct
from repository.training_expressions_repo import TrainingRepoABC


class SentenceTrainingChallenge(TypedDict):
    expressionId: str
    contextId: str
    sentence: str
    translation: str
    template: str
    values: List[str]
    practiceCount: int
    knowledgeLevel: float


class SentenceTrainingChallengeSolution(TypedDict):
    correctAnswer: str
    usersAnswer: str
    translation: Optional[str]


class SentenceTraining:
    
    def __init__(self, user_id: str, repo: type[TrainingRepoABC]):
        self.repo: TrainingRepoABC = repo(user_id)
        # self.context_repo = ExpressionContextRepo

    def get_expressions_number_can_be_trained_in_sentence(self):
        return self.repo.count_learn_list_items()

    def get_challenge(self) -> Optional[SentenceTrainingChallenge]:
        user_expr = self.repo.get_next(1)

        print(user_expr[0]["expression"].expression.expression)

        data = random.choice(user_expr[0]["expression"].expression.context)

        return {
            "expressionId": data.expression_id,
            "contextId": data.id,
            "sentence": data.sentence,
            "translation": data.translation["uk"],
            "template": data.template["tpl"],
            "values": data.template["values"],
            "practiceCount": user_expr[0]["practiceCount"],
            "knowledgeLevel": user_expr[0]["knowledgeLevel"],
        }

    def submit_challenge(
        self, expression_id: str, context_id: str, answer: str, hint: bool
    ) -> SentenceTrainingChallengeSolution:
        user_exprs = self.repo.get_by_ids([expression_id])

        if not user_exprs:
            raise ExpressionNotFoundException

        user_expr = user_exprs[0]

        context = self._get_context(user_expr, context_id)

        if context is None:
            raise ContextNotFoundException

        correct = context.sentence

        if not hint:
            self.repo.update_expressions([{
                "user_expression": user_expr,
                "is_trained_successfully": is_answer_correct(correct, answer)
            }])

        return {
            "correctAnswer": correct,
            "usersAnswer": answer,
            "translation": context.translation["uk"],
        }

    def _get_context(self, user_expr: UserExpression, context_id: str) -> Optional[ExpressionContext]:
        for context in user_expr.expression.context:
            if str(context.id) == context_id:
                return context
        return None
        