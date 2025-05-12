import os
from unittest import TestCase
from unittest.mock import Mock

from exercises.writing_training import WritingTraining
from models.models import Writings
from tests.unit.fixtures import get_writings


class BaseDialogueTrainingTest(TestCase):
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

    def reset_all_mock(self):
        self.mock_dialogue_repo.reset_mock()
        self.mock_user_expression_repo.reset_mock()
        self.mock_assistant.reset_mock()


class GetWritingsTests(BaseDialogueTrainingTest):
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

    def test_get_when_not_in_db(self):
        pass
