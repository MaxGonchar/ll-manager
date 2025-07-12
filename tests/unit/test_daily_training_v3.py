from unittest import TestCase
from unittest.mock import Mock

from repository.training_expressions_repo import DailyTrainingRepo
from exercises.daily_training_v3 import DailyTraining
from tests.unit.fixtures import get_expression, get_user_expression, get_user


class DailyTrainingTestHelper(TestCase):
    def setUp(self):
        self.user_id = "test-user-id"
        self.expression_id = "test-expression-id"
        self.expression = "test expression"
        self.definition = "test definition"

        self.repo = Mock(spec=DailyTrainingRepo)


class GetChallengeTests(DailyTrainingTestHelper):
    def setUp(self):
        super().setUp()

        self.subject = DailyTraining(self.repo)

    def test_get_challenge(self):
        self.repo.get_next.return_value = [
            get_user_expression(
                user_id=self.user_id,
                user=get_user(self.user_id),
                expression=get_expression(
                    expression_id=self.expression_id,
                    expression=self.expression,
                    definition=self.definition,
                ),
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


class SubmitChallengeTests(DailyTrainingTestHelper):
    def setUp(self):
        super().setUp()

        self.subject = DailyTraining(self.repo)

        self.challenge_expression = get_user_expression(
            user_id=self.user_id,
            user=get_user(self.user_id),
            expression=get_expression(
                expression_id=self.expression_id,
                expression=self.expression,
                definition=self.definition,
            ),
        )
        self.repo.get_by_id.return_value = self.challenge_expression

        self.expected = {
            "correctAnswer": self.expression,
            "definition": self.definition,
            "example": "example of usage of test expression",
            "translation": "тестовий вираз",
            "usersAnswer": self.expression,
        }

    def test_submit_correct_answer_without_hint(self):

        actual = self.subject.submit_challenge(
            expression_id=self.expression_id,
            answer=self.expression,
            hint=False,
        )
        self.assertEqual(self.expected, actual)
        self.repo.update_expressions.assert_called_once_with(
            [
                {
                    "user_expression": self.challenge_expression,
                    "is_trained_successfully": True,
                }
            ]
        )

    def test_submit_incorrect_answer_without_hint(self):
        actual = self.subject.submit_challenge(
            expression_id=self.expression_id, answer="wrong answer", hint=False
        )
        expected = {**self.expected, "usersAnswer": "wrong answer"}

        self.assertEqual(expected, actual)
        self.repo.update_expressions.assert_called_once_with(
            [
                {
                    "user_expression": self.challenge_expression,
                    "is_trained_successfully": False,
                }
            ]
        )

    def test_submit_answer_with_hint(self):
        actual = self.subject.submit_challenge(
            expression_id=self.expression_id, answer="any answer", hint=True
        )
        expected = {**self.expected, "usersAnswer": "any answer"}

        self.assertEqual(expected, actual)
        self.repo.update_expressions.assert_not_called()
