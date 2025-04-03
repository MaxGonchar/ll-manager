from tests.unit.test_repos.utils import BaseRepoTestUtils
from repository.dialogue_training_repo import DialogueTrainingRepo
from models.models import Dialogue


class GetTests(BaseRepoTestUtils):
    def setUp(self):
        self._clean_dialogues()
        self._clean_users()

        self.user_id = self._seed_user()

        self.dialogues = [
            {
                "id": "4d7993aa-d897-4647-994b-e0625c88f349",
                "user_id": self.user_id,
                "title": "Dialogue 1",
                "description": "Dialogue 1 description",
                "settings": {"setting": "value"},
                "dialogues": [{"dialogue": "dialogue 1"}],
                "expressions": [{"expression": "expression 1"}],
                "added": "2016-06-22 19:10:26",
                "updated": "2016-06-22 19:10:25",
            },
            {
                "id": "24d96f68-46e1-4fb3-b300-81cd89cea435",
                "user_id": self.user_id,
                "title": "Dialogue 2",
                "description": "Dialogue 2 description",
                "settings": {"setting": "value"},
                "dialogues": [{"dialogue": "dialogue 2"}],
                "expressions": [{"expression": "expression 2"}],
                "added": "2016-06-22 19:10:24",
                "updated": "2016-06-22 19:10:25",
            },
        ]

        self._seed_dialogues(self.dialogues[0])
        self._seed_dialogues(self.dialogues[1])

        self.subject = DialogueTrainingRepo(self.user_id)

    def _assert_dialogue_for_list(self, expected, actual):
        self.assertEqual(expected["id"], str(actual.id))
        self.assertEqual(expected["title"], actual.title)
        self.assertEqual(expected["description"], actual.description)

        with self.assertRaises(AttributeError):
            actual.user_id
            actual.settings
            actual.dialogues
            actual.expressions
            actual.added
            actual.updated

    def test_get_all(self):
        actual = self.subject.get()

        self.assertEqual(len(self.dialogues), len(actual))

        for expected_dialogue, actual_dialogue in zip(self.dialogues, actual):
            self._assert_dialogue_for_list(expected_dialogue, actual_dialogue)

    def test_get_one(self):
        actual = self.subject.get(self.dialogues[0]["id"])

        self._assert_dialogue(self.dialogues[0], actual)


class CreateDialogueTests(BaseRepoTestUtils):
    def setUp(self):
        self._clean_dialogues()
        self._clean_users()
        self.user_id = self._seed_user()
        self.subject = DialogueTrainingRepo(self.user_id)

    def test_create_dialogue(self):
        id_ = "4d7993aa-d897-4647-994b-e0625c88f349"
        dialogue = Dialogue(
            id=id_,
            user_id=self.user_id,
            title="Dialogue 1",
            description="Dialogue 1 description",
            settings={"test": "value"},
            added="2016-06-22 19:10:26",
            updated="2016-06-22 19:10:25",
        )
        self.subject.create(dialogue)

        actual = self.subject.get(id_)
        expected = {
            "id": id_,
            "title": "Dialogue 1",
            "description": "Dialogue 1 description",
            "user_id": self.user_id,
            "settings": {"test": "value"},
            "dialogues": [],
            "expressions": [],
            "added": "2016-06-22 19:10:26",
            "updated": "2016-06-22 19:10:25",
        }

        self._assert_dialogue(expected, actual)


class DeleteDialogueTests(BaseRepoTestUtils):
    def setUp(self):
        self._clean_dialogues()
        self._clean_users()

        self.user_id = self._seed_user()
        self.dialogue_id = "4d7993aa-d897-4647-994b-e0625c88f349"

        self.dialogue = {
            "id": self.dialogue_id,
            "user_id": self.user_id,
            "title": "Dialogue 1",
            "description": "Dialogue 1 description",
            "settings": {"setting": "value"},
            "dialogues": [{"dialogue": "dialogue 1"}],
            "expressions": [{"expression": "expression 1"}],
            "added": "2016-06-22 19:10:26",
            "updated": "2016-06-22 19:10:25",
        }

        self._seed_dialogues(self.dialogue)

        self.subject = DialogueTrainingRepo(self.user_id)

    def test_delete_dialogue(self):
        self.subject.delete(self.dialogue_id)

        self.assertIsNone(self.subject.get(self.dialogue_id))
