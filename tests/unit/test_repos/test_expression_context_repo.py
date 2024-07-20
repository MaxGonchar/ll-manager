import json

import psycopg2
from psycopg2.extras import DictCursor

from tests.unit.test_repos.utils import BaseRepoTestUtils
from tests.unit.fixtures import get_expression_context, get_expression
from repository.expression_context_repo import ExpressionContextRepo
from models.models import ExpressionContext


class ExpressionContextTestHelper(BaseRepoTestUtils):
    def setUp(self):
        self._clean_expressions()
        self._clean_expression_context()

        self.expr_1 = {
            "id": "4d7993aa-d897-4647-994b-e0625c88f349",
            "expression": "test",
            "definition": "test definition",
            "translation": '{"uk": "тест"}',
            "example": "Aboba tests",
            "added": "2016-06-22 19:10:25",
            "updated": "2016-06-22 19:10:25",
        }
        self.expr_2 = {
            "id": "4fb4259d-c140-4068-8a88-246372e6bd75",
            "expression": "test",
            "definition": "test definition",
            "translation": '{"uk": "тест"}',
            "example": "Aboba tests",
            "added": "2016-06-22 19:10:25",
            "updated": "2016-06-22 19:10:25",
        }
        self.expr_3 = {
            "id": "b07c9cf8-8659-47af-aa6d-14c880ff5512",
            "expression": "test",
            "definition": "test definition",
            "translation": '{"uk": "тест"}',
            "example": "Aboba tests",
            "added": "2016-06-22 19:10:25",
            "updated": "2016-06-22 19:10:25",
        }

        self._seed_db_expression_records(
            [self.expr_1, self.expr_2, self.expr_3]
        )


class PostTests(ExpressionContextTestHelper):
    def test_post(self):
        context_id = "d4edccb5-c74b-468c-885e-ffe65ef8fb3c"
        sentence = "test sentence"
        template = {
            "tpl": "{} sentence",
            "values": ["test"],
        }
        translation = {"uk": "Тестове речення"}
        expression = get_expression(
            expression_id=self.expr_1["id"],
            expression=self.expr_1["expression"],
        )
        context = get_expression_context(
            id_=context_id,
            expression_id=expression.id,
            sentence=sentence,
            template=template,
            translation=translation,
        )

        ExpressionContextRepo(expression.id).post(context)

        actual = self._get_db_data(self.expr_1["id"])

        self.assertEqual(self.expr_1["id"], actual["expression_id"])
        self.assertEqual(context_id, actual["context_id"])
        self.assertEqual(sentence, actual["sentence"])
        self.assertEqual(translation, actual["translation"])
        self.assertEqual(template, actual["template"])

    def _get_db_data(self, expr_id):
        sql = """
            SELECT
                e.id AS Expression_id,
                ec.id AS context_id,
                ec.sentence,
                ec.translation,
                ec.template
            FROM expressions e
            JOIN expression_context ec ON e.id=ec.expression_id
            WHERE e.id=%(expression_id)s
        """
        with psycopg2.connect(**self._get_test_db_dsn()) as con:  # type: ignore
            with con.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(sql, {"expression_id": expr_id})
                data = cur.fetchone()
        con.close()

        return data


class GetTests(ExpressionContextTestHelper):
    def setUp(self):
        super().setUp()

        self.context_1 = {
            "id": "4dbefd5f-e9a8-4b16-b2cc-03ea9ae767ad",
            "expression_id": self.expr_1["id"],
            "sentence": "test sentence 1",
            "translation": {"uk": "тестове речення 1"},
            "template": {"tpl": "{} sentence 1", "values": ["test"]},
            "added": "2016-06-22 19:10:25",
            "updated": "2016-06-22 19:10:25",
        }
        self.context_2 = {
            "id": "e2b0af2a-0453-422e-a2ee-1809901d9145",
            "expression_id": self.expr_1["id"],
            "sentence": "test sentence 2",
            "translation": {"uk": "тестове речення 2"},
            "template": {"tpl": "{} sentence 2", "values": ["test"]},
            "added": "2016-06-22 19:10:26",
            "updated": "2016-06-22 19:10:26",
        }

        self._seed_expression_context(self.context_1)
        self._seed_expression_context(self.context_2)

    def _assert_expression_context(
        self, expected: ExpressionContext, actual: ExpressionContext
    ):
        self.assertEqual(expected.id, str(actual.id))
        self.assertEqual(expected.expression_id, str(actual.expression_id))
        self.assertEqual(expected.sentence, actual.sentence)
        self.assertEqual(expected.translation, actual.translation)
        self.assertEqual(expected.template, actual.template)

    def test_get(self):
        expected = [
            get_expression_context(
                self.context_1["id"],
                self.context_1["expression_id"],
                self.context_1["sentence"],
                self.context_1["template"],
                self.context_1["translation"],
                self.context_1["added"],
                self.context_1["updated"],
            ),
            get_expression_context(
                self.context_2["id"],
                self.context_2["expression_id"],
                self.context_2["sentence"],
                self.context_2["template"],
                self.context_2["translation"],
                self.context_2["added"],
                self.context_2["updated"],
            ),
        ]

        actual = ExpressionContextRepo(self.expr_1["id"]).get()

        for exp, act in zip(expected, actual):
            self._assert_expression_context(exp, act)

    def test_get_no_expression_returns_empty_list(self):
        # TODO: raise an exception for not existing expression
        actual = ExpressionContextRepo(
            "9cc5ac45-fedd-4730-a6f6-de4953363ed8"
        ).get()

        self.assertEqual([], actual)

    def test_get_expression_without_context_returns_empty_list(self):
        actual = ExpressionContextRepo(
            "4fb4259d-c140-4068-8a88-246372e6bd75"
        ).get()

        self.assertEqual([], actual)
