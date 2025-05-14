import os
from unittest import TestCase
from unittest.mock import Mock, patch

from exercises.writing_training import WritingTraining
from models.models import Writings
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
    def test_submit_writing(self):
        # submit a writing with two expressions one correct and one incorrect
        pass
