from exercises.common import (
    ChallengeDict,
    get_challenge_object,
    ChallengeSolutionDict,
    get_challenge_solution_object,
    is_answer_correct,
    ExerciseExpressionsListItem,
    get_exercise_expressions_list_item,
)
from repository.training_expressions_repo import (
    TrainingRepoABC,
    UpdateTrainedExpression,
)


class DailyTraining:
    def __init__(self, repo: TrainingRepoABC):
        self.repo: TrainingRepoABC = repo
        print("DailyTraining v3 initialized")

    def get_challenge(self) -> ChallengeDict | None:
        if next_expressions := self.repo.get_next(1):
            return get_challenge_object(next_expressions[0].expression)

    def submit_challenge(
        self, expression_id: str, answer: str, hint: bool = False
    ) -> ChallengeSolutionDict:
        challenge_expression = self.repo.get_by_id(expression_id)
        correct = challenge_expression.expression

        if not hint:
            update_user_expression_data: UpdateTrainedExpression = {
                "user_expression": challenge_expression,
                "is_trained_successfully": is_answer_correct(
                    correct.expression, answer
                ),
            }

            self.repo.update_expressions([update_user_expression_data])

        return get_challenge_solution_object(correct, answer)

    def get_learn_list_expressions(self) -> list[ExerciseExpressionsListItem]:
        expressions = self.repo.get_list()
        expressions.sort(key=lambda item: item["practice_count"], reverse=True)
        return expressions

    def add_item_to_learn_list(self, expression_id: str) -> None:
        self.repo.add(expression_id)

    def remove_item_from_learn_list(self, expression_id: str) -> None:
        self.repo.delete(expression_id)

    def update_settings(self, settings: dict) -> None:
        self.repo.update_settings(settings)

    def refresh_learn_list(self):
        self.repo.refresh()

    def count_learn_list_items(self) -> int:
        return self.repo.count_learn_list_items()

    def is_expression_in_learn_list(self, expression_id: str) -> bool:
        return self.repo.is_expression_in_learn_list(expression_id)
