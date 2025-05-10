from tests.unit.test_repos.utils import BaseRepoTestUtils
from repository.writings_repo import WritingsRepo
from models.models import Writings


def get_writing_dict(user_id):
    return {
            "id": "4d7993aa-d897-4647-994b-e0625c88f349",
            "user_id": user_id,
            "properties": {"some": "value"},
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
                    ]
                },
                {
                    "id": 2,
                    "text": "Another sentence here",
                    "comment": [
                        {
                            "problem": "Some problem here",
                            "explanation": "Some explanation here",
                            "solution": "Some solution here",
                        }
                    ]
                }
            ],
            "expressions": [
                {
                    "id": "68788dbb-e16b-4b44-a8c5-b1338fd4aac9",
                    "expression": "Some phrase here",
                    "definition": "Some meaning here",
                    "status": "not_checked"
                },
                {
                    "id": "68788dbb-e16b-4b44-a8c5-b1338fd4aac8",
                    "expression": "Some phrase here",
                    "definition": "Some definition here",
                    "comment": "Some comment here",
                    "status": "failed"
                },
            ],
            "added": "2016-06-22 19:10:26",
            "updated": "2016-06-22 19:10:25",
        }


class GetTests(BaseRepoTestUtils):
    def setUp(self):
        self._clean_writings()
        self._clean_users()

        self.user_id = self._seed_user()

        self.writing = get_writing_dict(self.user_id)

        self._seed_writings(self.writing)
        self.subject = WritingsRepo(self.user_id)

    def test_success(self):
        writing = self.subject.get(self.writing["id"])
        self._assert_writing(self.writing, writing)
    
    def test_not_found_returns_none(self):
        writing = self.subject.get("4d7993aa-d897-4647-994b-e0625c88f348")
        self.assertIsNone(writing)


class AddTests(BaseRepoTestUtils):
    def setUp(self):
        self._clean_writings()
        self._clean_users()

        self.user_id = self._seed_user()
        self.subject = WritingsRepo(self.user_id)
    
    def test_success(self):
        writing = get_writing_dict(self.user_id)
        self.subject.add(Writings(**writing))

        actual = self.subject.get(writing["id"])
        expected = {
            "id": writing["id"],
            "user_id": writing["user_id"],
            "properties": writing["properties"],
            "writings": writing["writings"],
            "expressions": writing["expressions"],
            "added": writing["added"],
            "updated": writing["updated"],
        }
        self._assert_writing(expected, actual)


class DeleteTests(BaseRepoTestUtils):
    def setUp(self):
        self._clean_writings()
        self._clean_users()

        self.user_id = self._seed_user()
        self.writing_id = "4d7993aa-d897-4647-994b-e0625c88f349"

        self.writing = get_writing_dict(self.user_id)
        self.writing["id"] = self.writing_id

        self._seed_writings(self.writing)
        self.subject = WritingsRepo(self.user_id)

    def test_success(self):
        self.subject.delete(self.writing_id)

        actual = self.subject.get(self.writing_id)
        expected = None
        self.assertEqual(actual, expected)

