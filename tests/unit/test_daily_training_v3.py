from unittest import TestCase
from unittest.mock import Mock

from repository.training_expressions_repo import DailyTrainingRepo
from exercises.daily_training_v3 import DailyTraining
from tests.unit.fixtures import get_expression, get_user_expression, get_user


class GetChallengeTests(TestCase):
    def setUp(self):
        self.user_id = "test-user-id"
        self.expression_id = "test-expression-id"
        self.expression = "test expression"
        self.definition = "test definition"

        self.repo = Mock(spec=DailyTrainingRepo)
        self.subject = DailyTraining(self.repo)

    def test_get_challenge(self):
        self.repo.get_next.return_value = [
            get_user_expression(
                user_id=self.user_id,
                user=get_user(self.user_id),
                expression=get_expression(
                    expression_id=self.expression_id,
                    expression=self.expression,
                    definition=self.definition,)
            )
        ]
        expected = {
            "answer": self.expression,
            "expression_id": self.expression_id,
            "question": self.definition,
            "tip": self.expression,
        }
        actual = self.subject.get_challenge()
        self.assertEqual(expected, actual)
        self.repo.get_next.assert_called_once_with(1)


    def test_get_challenge_no_expressions(self):
        self.repo.get_next.return_value = []
        actual = self.subject.get_challenge()
        self.assertIsNone(actual)
        self.repo.get_next.assert_called_once_with(1)
