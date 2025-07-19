from datetime import datetime
from unittest import TestCase
from unittest.mock import Mock

from repository.training_expressions_repo import DailyTrainingRepo
from exercises.daily_training_v3 import DailyTraining
from tests.unit.fixtures import (
    get_daily_training_expressions_list_item,
    get_expression,
    get_user_expression,
    get_user,
)


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


class GetLearnListExpressionsTests(DailyTrainingTestHelper):
    def setUp(self):
        super().setUp()

        self.subject = DailyTraining(self.repo)

    def test_with_data(self):
        self.repo.get_list.return_value = [
            get_daily_training_expressions_list_item(
                expression_id="expr_id_1",
                expression="expression_1",
                knowledge_level=0,
                practice_count=0,
                last_practice_time=None,
            ),
            get_daily_training_expressions_list_item(
                expression_id="expr_id_2",
                expression="expression_2",
                knowledge_level=0.9,
                practice_count=6,
                last_practice_time=datetime(2023, 10, 1, 12, 0, 0),
            ),
            get_daily_training_expressions_list_item(
                expression_id="expr_id_3",
                expression="expression_3",
                knowledge_level=0.5,
                practice_count=5,
                last_practice_time=datetime(2023, 10, 2, 12, 0, 0),
            ),
        ]

        expected = [
            {
                "expression_id": "expr_id_2",
                "expression": "expression_2",
                "knowledge_level": 0.9,
                "practice_count": 6,
                "last_practice_time": datetime(2023, 10, 1, 12, 0, 0),
            },
            {
                "expression_id": "expr_id_3",
                "expression": "expression_3",
                "knowledge_level": 0.5,
                "practice_count": 5,
                "last_practice_time": datetime(2023, 10, 2, 12, 0, 0),
            },
            {
                "expression_id": "expr_id_1",
                "expression": "expression_1",
                "knowledge_level": 0.0,
                "practice_count": 0,
                "last_practice_time": None,
            },
        ]

        actual = self.subject.get_learn_list_expressions()
        self.assertEqual(expected, actual)
        self.repo.get_list.assert_called_once_with()


class AddItemToLearnListTests(DailyTrainingTestHelper):
    def setUp(self):
        super().setUp()

        self.subject = DailyTraining(self.repo)

    def test_add_item(self):
        self.subject.add_item_to_learn_list(self.expression_id)

        self.repo.add.assert_called_once_with(self.expression_id)


class RemoveItemFromLearnListTests(DailyTrainingTestHelper):
    def setUp(self):
        super().setUp()

        self.subject = DailyTraining(self.repo)

    def test_remove_item(self):
        self.subject.remove_item_from_learn_list(self.expression_id)

        self.repo.delete.assert_called_once_with(self.expression_id)


class UpdateSettingsTests(DailyTrainingTestHelper):
    def setUp(self):
        super().setUp()

        self.subject = DailyTraining(self.repo)

    def test_update_settings(self):
        settings = {
            "learn_list_size": 10,
            "knowledge_level_threshold": 0.5,
            "practice_count_threshold": 3,
        }
        self.subject.update_settings(settings)

        self.repo.update_settings.assert_called_once_with(settings)


class RefreshLearnListTests(DailyTrainingTestHelper):
    def setUp(self):
        super().setUp()

        self.subject = DailyTraining(self.repo)

    def test_refresh_learn_list(self):
        self.subject.refresh_learn_list()

        self.repo.refresh.assert_called_once_with()


class CountLearnListItemsTests(DailyTrainingTestHelper):
    def setUp(self):
        super().setUp()

        self.subject = DailyTraining(self.repo)

    def test_count_learn_list_items(self):
        self.repo.count_learn_list_items.return_value = 5

        actual = self.subject.count_learn_list_items()
        self.assertEqual(5, actual)
        self.repo.count_learn_list_items.assert_called_once_with()


class IsExpressionInLearnListTests(DailyTrainingTestHelper):
    def setUp(self):
        super().setUp()

        self.subject = DailyTraining(self.repo)

    def test_is_expression_in_learn_list(self):
        self.repo.is_expression_in_learn_list.return_value = True

        actual = self.subject.is_expression_in_learn_list(self.expression_id)
        self.assertTrue(actual)
        self.repo.is_expression_in_learn_list.assert_called_once_with(
            self.expression_id
        )
