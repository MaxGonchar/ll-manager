import os
from unittest import TestCase
from unittest.mock import Mock, call, patch

from exercises.daily_writing import DailyWriting
from tests.unit.fixtures import (
    get_training_expression_data,
    get_user_expression,
    get_expression,
    get_user,
)
from services.assistant import (
    ExpressionDetectionRequest,
    ExpressionDetectionResponse,
    ExpressionUsageResponse,
    GeneralJudgementResponse,
    Problem,
)


class BaseDailyWritingTest(TestCase):
    def setUp(self) -> None:
        self.user_id = "464ed801-72ee-41c1-9e11-4ac08ff84ea4"
        # os.environ["VENICE_MODEL"] = "test_model"
        # os.environ["VENICE_API_KEY"] = "test_api_key"

        self.mock_repo = Mock()
        self.mock_assistant = Mock()
        self.subject = DailyWriting(
            user_id=self.user_id,
            training_repo=self.mock_repo,
            assistant=self.mock_assistant,
        )


class TestDailyWritingGetChallenge(BaseDailyWritingTest):
    def test_get_challenge(self):
        self.mock_repo.return_value.get_next.return_value = [
            get_training_expression_data(
                get_user_expression(
                    user_id=self.user_id,
                    user=get_user(self.user_id),
                    expression=get_expression(
                        "expr_id-1", "expr1", "definition1"
                    ),
                    kl=0.5,
                    pc=1,
                ),
                kl=0.5,
                pc=1,
            ),
            get_training_expression_data(
                get_user_expression(
                    user_id=self.user_id,
                    user=get_user(self.user_id),
                    expression=get_expression(
                        "expr_id-2", "expr2", "definition2"
                    ),
                    kl=0.7,
                    pc=2,
                ),
                kl=0.7,
                pc=2,
            ),
            get_training_expression_data(
                get_user_expression(
                    user_id=self.user_id,
                    user=get_user(self.user_id),
                    expression=get_expression(
                        "expr_id-3", "expr3", "definition3"
                    ),
                    kl=0.9,
                    pc=3,
                ),
                kl=0.9,
                pc=3,
            ),
        ]

        actual = self.subject.get_challenge()
        expected = {
            "expressions": [
                {
                    "id": "expr_id-1",
                    "expression": "expr1",
                    "definition": "definition1",
                    "status": "not_checked",
                    "comment": None,
                },
                {
                    "id": "expr_id-2",
                    "expression": "expr2",
                    "definition": "definition2",
                    "status": "not_checked",
                    "comment": None,
                },
                {
                    "id": "expr_id-3",
                    "expression": "expr3",
                    "definition": "definition3",
                    "status": "not_checked",
                    "comment": None,
                },
            ],
            "lastWriting": None,
        }

        self.assertEqual(expected, actual)
        self.mock_repo.return_value.get_next.assert_called_once_with(10)


class SubmitChallengeTest(BaseDailyWritingTest):
    def setUp(self):
        super().setUp()
        self.user_expr_1 = get_user_expression(
            user_id=self.user_id,
            user=get_user(self.user_id),
            expression=get_expression("expr_id-1", "expr1", "definition1"),
            kl=0.5,
            pc=1,
        )
        self.user_expr_2 = get_user_expression(
            user_id=self.user_id,
            user=get_user(self.user_id),
            expression=get_expression("expr_id-2", "expr2", "definition2"),
            kl=0.7,
            pc=2,
        )
        self.user_expr_3 = get_user_expression(
            user_id=self.user_id,
            user=get_user(self.user_id),
            expression=get_expression("expr_id-3", "expr3", "definition3"),
            kl=0.9,
            pc=3,
        )
        self.user_expr_4 = get_user_expression(
            user_id=self.user_id,
            user=get_user(self.user_id),
            expression=get_expression("expr_id-4", "expr4", "definition4"),
            kl=0.9,
            pc=3,
        )

    def test_submit_challenge(self):
        text = "This is a test writing with expr1 and expr2."
        expressions_to_train_ids = ["expr_id-1", "expr_id-2", "expr_id-3"]

        self.mock_repo.return_value.get_by_ids.return_value = [
            self.user_expr_1,
            self.user_expr_2,
            self.user_expr_3,
        ]

        self.mock_repo.return_value.get_next.return_value = [
            get_training_expression_data(self.user_expr_2, kl=0.9, pc=3),
            get_training_expression_data(self.user_expr_3, kl=0.9, pc=3),
            get_training_expression_data(self.user_expr_4, kl=0.9, pc=3),
        ]

        self.mock_assistant.return_value.get_general_judgement.return_value = (
            GeneralJudgementResponse(
                problems=[
                    Problem(
                        problem="problem_part1",
                        explanation="explanation1",
                        solution="solution1",
                    ),
                    Problem(
                        problem="problem_part2",
                        explanation="explanation2",
                        solution="solution2",
                    ),
                ]
            )
        )
        self.mock_assistant.return_value.detect_phrases_usage.return_value = (
            ExpressionDetectionResponse(expressions=["expr_id-1", "expr_id-2"])
        )
        self.mock_assistant.return_value.get_expression_usage_judgement.side_effect = [
            ExpressionUsageResponse(
                id="expr_id-1",
                is_correct=True,
                comment="Correct usage of expr1.",
            ),
            ExpressionUsageResponse(
                id="expr_id-2",
                is_correct=False,
                comment="Incorrect usage of expr2.",
            ),
        ]

        actual = self.subject.submit_writing(text, expressions_to_train_ids)
        expected = {
            "expressions": [
                {
                    "comment": "Incorrect usage of expr2.",
                    "definition": "definition2",
                    "expression": "expr2",
                    "id": "expr_id-2",
                    "status": "failed",
                },
                {
                    "comment": None,
                    "definition": "definition3",
                    "expression": "expr3",
                    "id": "expr_id-3",
                    "status": "not_checked",
                },
                {
                    "comment": None,
                    "definition": "definition4",
                    "expression": "expr4",
                    "id": "expr_id-4",
                    "status": "not_checked",
                },
            ],
            "lastWriting": {
                "comment": [
                    {
                        "explanation": "explanation1",
                        "problem": "problem_part1",
                        "solution": "solution1",
                    },
                    {
                        "explanation": "explanation2",
                        "problem": "problem_part2",
                        "solution": "solution2",
                    },
                ],
                "userText": "This is a test writing with expr1 and expr2.",
            },
        }

        self.maxDiff = None
        self.assertEqual(expected, actual)

        self.mock_repo.return_value.get_by_ids.assert_called_once_with(
            expressions_to_train_ids
        )
        self.mock_assistant.return_value.get_general_judgement.assert_called_once_with(
            text
        )
        self.mock_assistant.return_value.detect_phrases_usage.assert_called_once_with(
            text,
            [
                {"id": "expr_id-1", "expression": "expr1"},
                {"id": "expr_id-2", "expression": "expr2"},
                {"id": "expr_id-3", "expression": "expr3"},
            ],
        )
        self.mock_assistant.return_value.get_expression_usage_judgement.has_calls(
            [
                call(
                    text,
                    {
                        "id": "expr_id-1",
                        "expression": "expr1",
                        "meaning": "definition1",
                    },
                ),
                call(
                    text,
                    {
                        "id": "expr_id-2",
                        "expression": "expr2",
                        "meaning": "definition2",
                    },
                ),
            ]
        )

        self.mock_repo.return_value.update_expressions.assert_called_once_with(
            [
                {
                    "user_expression": self.user_expr_1,
                    "is_trained_successfully": True,
                },
                {
                    "user_expression": self.user_expr_2,
                    "is_trained_successfully": False,
                },
            ]
        )
        self.mock_repo.return_value.get_next.assert_called_once_with(10)
