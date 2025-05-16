import os
from unittest import TestCase
from unittest.mock import Mock, patch, call

from exercises.writing_training import WritingTraining
from models.models import Writings
from services.assistant import (
    ExpressionDetectionResponse,
    ExpressionUsageResponse,
    GeneralJudgementResponse,
    Problem,
)
from tests.unit.fixtures import (
    get_writings,
    get_user_expression,
    get_user,
    get_expression,
)


class BaseWritingTrainingTest(TestCase):
    def setUp(self):
        self.user_id = "464ed801-72ee-41c1-9e11-4ac08ff84ea4"
        os.environ["VENICE_MODEL"] = "test_model"
        os.environ["VENICE_API_KEY"] = "test_api_key"

        self.mock_writing_repo = Mock()
        self.mock_user_expression_repo = Mock()
        self.mock_assistant = Mock()
        self.subject = WritingTraining(
            self.user_id,
            self.mock_writing_repo,
            self.mock_user_expression_repo,
            self.mock_assistant,
        )

    def tearDown(self):
        os.environ.pop("VENICE_MODEL", None)
        os.environ.pop("VENICE_API_KEY", None)

    # def reset_all_mock(self):
    #     self.mock_dialogue_repo.reset_mock()
    #     self.mock_user_expression_repo.reset_mock()
    #     self.mock_assistant.reset_mock()

    def _assert_writings(self, actual: Writings, expected: Writings):
        self.assertEqual(actual.id, expected.id)
        self.assertEqual(actual.user_id, expected.user_id)
        self.assertEqual(actual.properties, expected.properties)
        self.assertEqual(actual.writings, expected.writings)
        self.assertEqual(actual.expressions, expected.expressions)
        self.assertEqual(actual.added, expected.added)
        self.assertEqual(actual.updated, expected.updated)


class GetWritingsTests(BaseWritingTrainingTest):
    def setUp(self):
        self.writing_id = "dbb4797f-bf2c-45ed-b768-e85b9e17b60c"
        super().setUp()

    def test_get_when_from_db(self):
        db_writings = get_writings(
            id_=self.writing_id,
            user_id=self.user_id,
        )
        self.mock_writing_repo.return_value.get.return_value = db_writings

        actual = self.subject.get_writings()

        expected = {
            "writings": [
                {
                    "id": 1,
                    "text": "Some sentence here",
                    "comment": [
                        {
                            "problem": "Some problem here",
                            "explanation": "Some explanation here",
                            "solution": "Some solution here",
                        }
                    ],
                },
            ],
            "expressions": [
                {
                    "id": "68788dbb-e16b-4b44-a8c5-b1338fd4aac9",
                    "expression": "Some phrase here",
                    "definition": "Some meaning here",
                    "status": "not_checked",
                },
            ],
        }

        self.assertEqual(expected, actual)
        self.mock_writing_repo.return_value.get.assert_called_once()

    @patch("exercises.writing_training.get_current_utc_time")
    @patch("exercises.writing_training.uuid4")
    def test_get_when_not_in_db(self, mock_uuid, mock_get_current_time):
        mock_writings_id = "dbb4797f-bf2c-45ed-b768-e85b9e17b60c"
        mock_uuid.return_value = mock_writings_id

        mock_time = "2025-04-12 10:10:25"
        mock_get_current_time.return_value = mock_time

        self.mock_writing_repo.return_value.get.return_value = None

        mock_expr_id_1 = "73f2a1a3-ee24-4f56-aa13-702bb5235fa9"
        mock_expr_1 = "mock_expr_1"
        mock_definition_1 = "mock_definition_1"
        mock_expr_id_2 = "89b3e0f2-4db1-4de8-8c48-4aeac3477978"
        mock_expr_2 = "mock_expr_2"
        mock_definition_2 = "mock_definition_2"
        self.mock_user_expression_repo.return_value.get_trained_expressions.return_value = [
            get_user_expression(
                user_id=self.user_id,
                user=get_user(self.user_id),
                expression=get_expression(
                    expression_id=mock_expr_id_1,
                    expression=mock_expr_1,
                    definition=mock_definition_1,
                ),
            ),
            get_user_expression(
                user_id=self.user_id,
                user=get_user(self.user_id),
                expression=get_expression(
                    expression_id=mock_expr_id_2,
                    expression=mock_expr_2,
                    definition=mock_definition_2,
                ),
            ),
        ]

        actual = self.subject.get_writings()

        expected = {
            "writings": [],
            "expressions": [
                {
                    "id": mock_expr_id_1,
                    "expression": mock_expr_1,
                    "definition": mock_definition_1,
                    "status": "not_checked",
                },
                {
                    "id": mock_expr_id_2,
                    "expression": mock_expr_2,
                    "definition": mock_definition_2,
                    "status": "not_checked",
                },
            ],
        }

        self.assertEqual(expected, actual)

        self.mock_writing_repo.return_value.get.assert_called_once()
        self.mock_user_expression_repo.return_value.get_trained_expressions.assert_called_once_with(
            limit=10, excludes=[]
        )

        actual_created_writing = (
            self.mock_writing_repo.return_value.add.call_args[0][0]
        )
        expected_created_writing = get_writings(
            id_=mock_writings_id,
            user_id=self.user_id,
            properties={"maxExpressionsToTrain": 10, "maxWritingsToStore": 10},
            writings=[],
            expressions=[
                {
                    "id": mock_expr_id_1,
                    "expression": mock_expr_1,
                    "definition": mock_definition_1,
                    "status": "not_checked",
                },
                {
                    "id": mock_expr_id_2,
                    "expression": mock_expr_2,
                    "definition": mock_definition_2,
                    "status": "not_checked",
                },
            ],
            added=mock_time,
            updated=mock_time,
        )

        self._assert_writings(actual_created_writing, expected_created_writing)


class SubmitWritingTests(BaseWritingTrainingTest):
    @patch("exercises.writing_training.get_current_utc_time")
    def test_submit_writing(self, mock_get_current_time):
        mock_time = "2025-04-13 10:10:25"
        mock_get_current_time.return_value = mock_time

        mock_writings = get_writings(
            id_="dbb4797f-bf2c-45ed-b768-e85b9e17b60c",
            user_id=self.user_id,
            properties={"maxExpressionsToTrain": 10, "maxWritingsToStore": 10},
            expressions=[
                {
                    "id": "1",
                    "expression": "mock_expr_1",
                    "definition": "mock_definition_1",
                    "status": "not_checked",
                },
                {
                    "id": "2",
                    "expression": "mock_expr_2",
                    "definition": "mock_definition_2",
                    "status": "not_checked",
                },
            ],
        )
        self.mock_writing_repo.return_value.get.return_value = mock_writings

        mock_general_judgement = GeneralJudgementResponse(
            problems=[
                Problem(
                    problem="the problem",
                    explanation="the explanation",
                    solution="the solution",
                ),
                Problem(
                    problem="the problem 2",
                    explanation="the explanation 2",
                    solution="the solution 2",
                ),
            ]
        )
        self.mock_assistant.return_value.get_general_judgement.return_value = (
            mock_general_judgement
        )

        mock_detected_expression_ids = ExpressionDetectionResponse(
            expressions=["1", "2"]
        )
        self.mock_assistant.return_value.detect_phrases_usage.return_value = (
            mock_detected_expression_ids
        )

        mock_expressions_usage_judgement = [
            ExpressionUsageResponse(
                id="1", is_correct=False, comment="expression-1 judgement"
            ),
            ExpressionUsageResponse(
                id="2", is_correct=True, comment="expression-2 judgement"
            ),
        ]
        self.mock_assistant.return_value.get_expression_usage_judgement.side_effect = (
            mock_expressions_usage_judgement
        )

        mock_user_expressions = [
            get_user_expression(
                user_id=self.user_id,
                user=None,
                expression=get_expression(
                    expression_id="1",
                    expression="expression 1",
                    definition="definition 1",
                ),
                kl=0.5,
                pc=1,
            ),
            get_user_expression(
                user_id=self.user_id,
                user=None,
                expression=get_expression(
                    expression_id="2",
                    expression="expression 2",
                    definition="definition 2",
                ),
                kl=0.5,
                pc=1,
            ),
        ]
        self.mock_user_expression_repo.return_value.get.return_value = (
            mock_user_expressions
        )

        mock_user_expressions_to_add = [
            get_user_expression(
                user_id=self.user_id,
                user=None,
                expression=get_expression(
                    expression_id="4",
                    expression="expression 4",
                    definition="definition 4",
                ),
            ),
        ]
        self.mock_user_expression_repo.return_value.get_trained_expressions.return_value = (
            mock_user_expressions_to_add
        )

        actual = self.subject.submit_writing("Some test writings to submit")
        expected = {
            "writings": [
                {
                    "id": 1,
                    "text": "Some sentence here",
                    "comment": [
                        {
                            "problem": "Some problem here",
                            "explanation": "Some explanation here",
                            "solution": "Some solution here",
                        }
                    ],
                },
                {
                    "id": 2,
                    "text": "Some test writings to submit",
                    "comment": [
                        {
                            "problem": "the problem",
                            "explanation": "the explanation",
                            "solution": "the solution",
                        },
                        {
                            "problem": "the problem 2",
                            "explanation": "the explanation 2",
                            "solution": "the solution 2",
                        },
                    ],
                },
            ],
            "expressions": [
                {
                    "id": "1",
                    "expression": "mock_expr_1",
                    "definition": "mock_definition_1",
                    "status": "failed",
                    "comment": "expression-1 judgement",
                },
                {
                    "id": "4",
                    "expression": "expression 4",
                    "definition": "definition 4",
                    "status": "not_checked",
                },
            ],
        }

        self.assertEqual(expected, actual)

        self.mock_writing_repo.return_value.get.assert_called_once()
        self.mock_assistant.return_value.get_general_judgement.assert_called_once_with(
            "Some test writings to submit"
        )
        self.mock_assistant.return_value.detect_phrases_usage.assert_called_once_with(
            "Some test writings to submit",
            [
                {"id": "1", "expression": "mock_expr_1"},
                {"id": "2", "expression": "mock_expr_2"},
            ],
        )
        self.mock_assistant.return_value.get_expression_usage_judgement.assert_has_calls(
            [
                call(
                    "Some test writings to submit",
                    {
                        "id": "1",
                        "expression": "mock_expr_1",
                        "meaning": "mock_definition_1",
                    },
                ),
                call(
                    "Some test writings to submit",
                    {
                        "id": "2",
                        "expression": "mock_expr_2",
                        "meaning": "mock_definition_2",
                    },
                ),
            ]
        )
        self.mock_user_expression_repo.return_value.get.assert_called_once_with(
            include=["1", "2"]
        )

        put_expressions = (
            self.mock_user_expression_repo.return_value.put.call_args_list
        )
        self.assertEqual(2, len(put_expressions))
        self.assertEqual("1", put_expressions[0].args[0].expression.id)
        self.assertEqual(0.25, put_expressions[0].args[0].knowledge_level)
        self.assertEqual(2, put_expressions[0].args[0].practice_count)
        self.assertEqual(
            mock_time, put_expressions[0].args[0].last_practice_time
        )
        self.assertEqual("2", put_expressions[1].args[0].expression.id)
        self.assertEqual(0.75, put_expressions[1].args[0].knowledge_level)
        self.assertEqual(2, put_expressions[1].args[0].practice_count)
        self.assertEqual(
            mock_time, put_expressions[1].args[0].last_practice_time
        )

        self.mock_user_expression_repo.return_value.get_trained_expressions.assert_called_once_with(
            limit=9, excludes=["1"]
        )

        actual_updated_writings = (
            self.mock_writing_repo.return_value.add.call_args.args[0]
        )
        expected_updated_writings = get_writings(
            id_="dbb4797f-bf2c-45ed-b768-e85b9e17b60c",
            user_id=self.user_id,
            expressions=[
                {
                    "comment": "expression-1 judgement",
                    "definition": "mock_definition_1",
                    "expression": "mock_expr_1",
                    "id": "1",
                    "status": "failed",
                },
                {
                    "definition": "definition 4",
                    "expression": "expression 4",
                    "id": "4",
                    "status": "not_checked",
                },
            ],
            writings=[
                {
                    "id": 1,
                    "text": "Some sentence here",
                    "comment": [
                        {
                            "problem": "Some problem here",
                            "explanation": "Some explanation here",
                            "solution": "Some solution here",
                        }
                    ],
                },
                {
                    "id": 2,
                    "text": "Some test writings to submit",
                    "comment": [
                        {
                            "problem": "the problem",
                            "explanation": "the explanation",
                            "solution": "the solution",
                        },
                        {
                            "problem": "the problem 2",
                            "explanation": "the explanation 2",
                            "solution": "the solution 2",
                        },
                    ],
                },
            ],
            updated=mock_time,
        )

        self._assert_writings(
            expected_updated_writings, actual_updated_writings
        )
