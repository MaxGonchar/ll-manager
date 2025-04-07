import os
from unittest import TestCase
from unittest.mock import patch

from exercises.dialogue_training import DialogueTraining
from tests.unit.fixtures import (
    get_dialogue,
    get_user_expression,
    get_expression,
)


class GetTests(TestCase):
    def setUp(self):
        self.user_id = "464ed801-72ee-41c1-9e11-4ac08ff84ea4"
        self.dialogues = [
            get_dialogue(
                id_="4d7993aa-d897-4647-994b-e0625c88f349",
                user_id=self.user_id,
                title="Dialogue 1",
                description="Dialogue 1 description",
                settings={"setting": "value"},
                dialogues=[{"dialogue": "dialogue 1"}],
                expressions=[{"expression": "expression 1"}],
                added="2016-06-22 19:10:26",
                updated="2016-06-22 19:10:25",
            ),
            get_dialogue(
                id_="24d96f68-46e1-4fb3-b300-81cd89cea435",
                user_id=self.user_id,
                title="Dialogue 2",
                description="Dialogue 2 description",
                settings={"setting": "value"},
                dialogues=[{"dialogue": "dialogue 2"}],
                expressions=[{"expression": "expression 2"}],
                added="2016-06-22 19:10:24",
                updated="2016-06-22 19:10:25",
            ),
        ]
        dialogue_repo_patcher = patch(
            "exercises.dialogue_training.DialogueTrainingRepo"
        )
        self.mock_dialogue_repo = dialogue_repo_patcher.start()
        self.addCleanup(dialogue_repo_patcher.stop)

        user_expression_repo_patcher = patch(
            "exercises.dialogue_training.UserExpressionsRepo"
        )
        self.mock_user_expression_repo = user_expression_repo_patcher.start()
        self.addCleanup(user_expression_repo_patcher.stop)

        os.environ["VENICE_MODEL"] = "test_model"
        os.environ["VENICE_API_KEY"] = "test_api_key"

        self.subject = DialogueTraining(self.user_id)

    def tearDown(self):
        os.environ.pop("VENICE_MODEL", None)
        os.environ.pop("VENICE_API_KEY", None)

    def test_get_all(self):
        self.mock_dialogue_repo.return_value.get.return_value = self.dialogues
        expected = [
            {
                "id": "4d7993aa-d897-4647-994b-e0625c88f349",
                "title": "Dialogue 1",
                "description": "Dialogue 1 description",
            },
            {
                "id": "24d96f68-46e1-4fb3-b300-81cd89cea435",
                "title": "Dialogue 2",
                "description": "Dialogue 2 description",
            },
        ]
        actual = self.subject.get_dialogues()

        self.assertEqual(expected, actual)

        self.mock_dialogue_repo.return_value.get.assert_called_once_with()

    def test_get_one(self):
        self.mock_dialogue_repo.return_value.get.return_value = self.dialogues[
            0
        ]
        expected = {
            "id": "4d7993aa-d897-4647-994b-e0625c88f349",
            "title": "Dialogue 1",
            "description": "Dialogue 1 description",
            "settings": {"setting": "value"},
            "dialogue": [{"dialogue": "dialogue 1"}],
            "expressions": [{"expression": "expression 1"}],
        }
        actual = self.subject.get_dialogue(
            "4d7993aa-d897-4647-994b-e0625c88f349"
        )

        self.assertEqual(expected, actual)

        self.mock_dialogue_repo.return_value.get.assert_called_once_with(
            "4d7993aa-d897-4647-994b-e0625c88f349"
        )


class CreateDialogueTests(TestCase):
    def setUp(self):
        self.user_id = "464ed801-72ee-41c1-9e11-4ac08ff84ea4"
        dialogue_repo_patcher = patch(
            "exercises.dialogue_training.DialogueTrainingRepo"
        )
        self.mock_dialogue_repo = dialogue_repo_patcher.start()
        self.addCleanup(dialogue_repo_patcher.stop)

        user_expression_repo_patcher = patch(
            "exercises.dialogue_training.UserExpressionsRepo"
        )
        self.mock_user_expression_repo = user_expression_repo_patcher.start()
        self.addCleanup(user_expression_repo_patcher.stop)

        self.dialogue_id = "4d7993aa-d897-4647-994b-e0625c88f349"
        uuid_patcher = patch(
            "exercises.dialogue_training.uuid4",
            return_value=self.dialogue_id,
        )
        uuid_patcher.start()
        self.addCleanup(uuid_patcher.stop)

        os.environ["VENICE_MODEL"] = "test_model"
        os.environ["VENICE_API_KEY"] = "test_api_key"

        self.subject = DialogueTraining(self.user_id)

    def tearDown(self):
        os.environ.pop("VENICE_MODEL", None)
        os.environ.pop("VENICE_API_KEY", None)

    def test_create_dialogue(self):
        expression_id_1 = "ab856dd3-7a68-4693-a0bc-e14a1799c19b"
        expression_id_2 = "ab856dd3-7a68-4693-a0bc-e14a1799c19c"
        expression_1 = get_expression(
            expression_id=expression_id_1,
            expression="expression 1",
            definition="definition 1",
        )
        expression_2 = get_expression(
            expression_id=expression_id_2,
            expression="expression 2",
            definition="definition 2",
        )
        user_expression_1 = get_user_expression(
            user_id=self.user_id,
            user=None,
            expression=expression_1,
        )
        user_expression_2 = get_user_expression(
            user_id=self.user_id,
            user=None,
            expression=expression_2,
        )
        self.mock_user_expression_repo.return_value.get_oldest_trained_expressions.return_value = [
            user_expression_1,
            user_expression_2,
        ]

        actual = self.subject.create_dialogue(
            "Dialogue 1", "Dialogue 1 description"
        )

        self.assertEqual(self.dialogue_id, actual)

        self.mock_user_expression_repo.return_value.get_oldest_trained_expressions.assert_called_once_with(
            10
        )

        actual_dialogue = (
            self.mock_dialogue_repo.return_value.create.call_args.args[0]
        )
        self.assertEqual(self.dialogue_id, actual_dialogue.id)
        self.assertEqual(self.user_id, actual_dialogue.user_id)
        self.assertEqual("Dialogue 1", actual_dialogue.title)
        self.assertEqual("Dialogue 1 description", actual_dialogue.description)
        self.assertEqual(
            {"maxExpressionsToTrain": 10}, actual_dialogue.settings
        )
        self.assertEqual(
            [
                {
                    "id": 1,
                    "role": "assistant",
                    "text": "Hello! What are we going to talk about?",
                }
            ],
            actual_dialogue.dialogues,
        )
        self.assertEqual(
            [
                {
                    "definition": "definition 1",
                    "expression": "expression 1",
                    "id": "ab856dd3-7a68-4693-a0bc-e14a1799c19b",
                    "status": "not_checked",
                },
                {
                    "definition": "definition 2",
                    "expression": "expression 2",
                    "id": "ab856dd3-7a68-4693-a0bc-e14a1799c19c",
                    "status": "not_checked",
                },
            ],
            actual_dialogue.expressions,
        )
