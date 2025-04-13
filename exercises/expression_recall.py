from typing import List, Optional
from repository.user_expressions_repo import UserExpressionsRepo
from exercises.common import (
    ChallengeDict,
    get_challenge_object,
    is_answer_correct,
    ChallengeSolutionDict,
    calculate_knowledge_level,
    get_challenge_solution_object,
    ExerciseExpressionsListItem,
    get_exercise_expressions_list_item,
)
from exercises.exceptions import ExpressionNotFoundException
from models.models import UserExpression
from helpers.time_helpers import get_current_utc_time


class ExpressionRecall:
    def __init__(self, user_id: str) -> None:
        self.repo = UserExpressionsRepo(user_id)

    def get_challenge(self) -> Optional[ChallengeDict]:
        """return an expression with the latest 'last_practice_time'"""

        if not (user_exprs := self.repo.get_trained_expressions(limit=1)):
            return

        user_expr = user_exprs[0]

        return get_challenge_object(user_expr.expression)

    def submit_challenge(
        self, expr_id: str, answer: str, hint: bool = False
    ) -> ChallengeSolutionDict:
        """validate a user answer, calculate knowledge level, practice count
        returns challenge solution object"""

        user_expr = self.repo.get_by_id(expr_id)

        if user_expr is None:
            raise ExpressionNotFoundException

        correct = user_expr.expression

        if not hint:
            if is_answer_correct(correct.expression, answer):
                self._register_challenge(user_expr, True)
            else:
                self._register_challenge(user_expr, False)

        return get_challenge_solution_object(correct, answer)

    def get_expressions_needed_recalling(
        self,
    ) -> List[ExerciseExpressionsListItem]:
        """returns list of expressions that are needed to be recalled,
        sorted by last practice time in ascending order"""

        user_exprs = self.repo.get_trained_expressions()
        return [
            get_exercise_expressions_list_item(
                user_expr.expression_id,
                user_expr.expression.expression,
                user_expr.knowledge_level,
                user_expr.practice_count,
                user_expr.last_practice_time,
            )
            for user_expr in user_exprs
        ]

    def get_number_of_expressions_needed_recalling(self) -> int:
        """returns a number of expressions that are needed to be recalled"""

        return self.repo.count_trained_expressions()

    def _register_challenge(
        self, user_expr: UserExpression, successful: bool
    ) -> None:
        user_expr.knowledge_level = calculate_knowledge_level(
            user_expr.knowledge_level, user_expr.practice_count, successful
        )
        user_expr.practice_count += 1
        user_expr.last_practice_time = get_current_utc_time()
        self.repo.put(user_expr)
