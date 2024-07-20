from unittest import TestCase
from unittest.mock import patch

from services.expression_context_service import ExpressionContextService
from tests.unit.fixtures import get_expression_context


class PostTest(TestCase):
    def setUp(self):
        self.context_id = "9f0dd747-f80b-4b3e-a935-523bf07ca3f7"
        self.expression_id = "ea86576a-715f-4623-932d-6d7a9bf37712"
        self.added = "2023-04-12 10:10:25"

        post_patcher = patch(
            "services.expression_context_service.ExpressionContextRepo"
        )
        mock_repo = post_patcher.start()
        mock_repo.return_value.expression_id = self.expression_id
        self.mock_post = mock_repo.return_value.post
        self.addCleanup(post_patcher.stop)

        uuid_patcher = patch(
            "services.expression_context_service.uuid4",
            return_value=self.context_id,
        )
        uuid_patcher.start()
        self.addCleanup(uuid_patcher.stop)

        time_patcher = patch(
            "services.expression_context_service.get_current_utc_time",
            return_value=self.added,
        )
        time_patcher.start()
        self.addCleanup(time_patcher.stop)

        self.subject = ExpressionContextService(self.expression_id)

    def test_post(self):
        sentence = "test sentence"
        translation = "тестовий переклад"
        template = {"tpl": "{} sentence", "values": ["test"]}

        self.subject.post_context(sentence, translation, template)

        actual = self.mock_post.call_args.args[0]

        self.assertEqual(self.context_id, actual.id)
        self.assertEqual(self.expression_id, actual.expression_id)
        self.assertEqual(sentence, actual.sentence)
        self.assertEqual({"uk": translation}, actual.translation)
        self.assertEqual(template, actual.template)
        self.assertEqual(self.added, actual.added)
        self.assertEqual(self.added, actual.updated)


class GetTeats(TestCase):
    def setUp(self):
        self.expression_id = "464ed801-72ee-41c1-9e11-4ac08ff84ea4"

        post_patcher = patch(
            "services.expression_context_service.ExpressionContextRepo"
        )
        mock_repo = post_patcher.start()
        mock_repo.return_value.expression_id = self.expression_id
        self.mock_get = mock_repo.return_value.get
        self.addCleanup(post_patcher.stop)

        self.subject = ExpressionContextService(self.expression_id)

    def test_get(self):
        context_1 = {
            "id": "ea484e37-ef1f-406a-995e-fbd30dfd021a",
            "expression_id": self.expression_id,
            "sentence": "test sentence 1",
            "translation": {"uk": "тестове речення 1"},
            "template": {"tpl": "{} sentence 1", "values": ["test"]},
        }
        context_2 = {
            "id": "d3928402-a080-47a0-b017-7e7ebf43d187",
            "expression_id": self.expression_id,
            "sentence": "test sentence 2",
            "translation": {"uk": "тестове речення 2"},
            "template": {"tpl": "{} sentence 2", "values": ["test"]},
        }
        self.mock_get.return_value = [
            get_expression_context(
                id_=context_1["id"],
                expression_id=context_1["expression_id"],
                sentence=context_1["sentence"],
                template=context_1["template"],
                translation=context_1["translation"],
            ),
            get_expression_context(
                id_=context_2["id"],
                expression_id=context_2["expression_id"],
                sentence=context_2["sentence"],
                template=context_2["template"],
                translation=context_2["translation"],
            ),
        ]
        expected = [
            {
                "id": context_1["id"],
                "sentence": context_1["sentence"],
                "template": context_1["template"],
                "translation": context_1["translation"]["uk"],
            },
            {
                "id": context_2["id"],
                "sentence": context_2["sentence"],
                "template": context_2["template"],
                "translation": context_2["translation"]["uk"],
            },
        ]

        actual = self.subject.get_context()

        self.assertEqual(expected, actual)

        self.mock_get.assert_called_once_with()
