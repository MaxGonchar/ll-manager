from exercises.common import ChallengeDict, get_challenge_object, ChallengeSolutionDict, get_challenge_solution_object, is_answer_correct
from repository.training_expressions_repo import TrainingRepoABC


class DailyTraining:
    def __init__(self, repo: TrainingRepoABC):
        self.repo = repo

    def get_challenge(self) -> ChallengeDict | None:
        if next_expressions := self.repo.get_next(1):
            return get_challenge_object(next_expressions[0].expression)

    def submit_challenge(self, expression_id: str, answer: str, hint: bool = False) -> ChallengeSolutionDict:
        pass

    def get_learn_list_expressions(self):
        pass

    def add_item_to_learn_list(self):
        pass

    def remove_item_from_learn_list(self):
        pass

    def update_settings(self):
        pass

    def refresh_learn_list(self):
        pass

    def count_learn_list_items(self):
        pass

    def is_expression_in_learn_list(self):
        pass
