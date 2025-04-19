from unittest.mock import patch

import psycopg2
from psycopg2.extras import DictCursor

from tests.functional.utils import FunctionalTestsHelper


class AddUserExpressionTest(FunctionalTestsHelper):
    def setUp(self):
        super().setUp()

        with open(
            "tests/functional/data/setup_test_user_expression_post.sql", "r"
        ) as file:
            sql = file.read()

        self._setup_test_db(sql)

        self.user_id = "04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef"
        session = {
            "user": "daily_training@test.mail",
            "user_id": self.user_id,
        }
        self._set_session(**session)

    def test_post_expression_get(self):
        expression = "test expression"
        body = {"action": "add", "query": expression}

        context = self._get_test_template_context(
            "POST",
            "expressions/post.html",
            "/user/expressions",
            data=body,
            follow_redirects=True,
        )

        self.assertEqual(expression, context["form"].expression.data)
        self.assertEqual(
            ["", "adjective", "grammar", "noun"], context["form"].tag_1.choices
        )
        self.assertEqual(
            ["", "verb pattern"], context["form"].grammar_tag.choices
        )

    @patch("services.user_expression_service.uuid4")
    def test_post_expression_post(self, mock_uuid):
        expr_id = "eccda880-b9fa-40a8-93b7-d0098d1e4e69"
        mock_uuid.return_value = expr_id

        expression = "test expression"
        definition = "definition of test expression"
        translation = "тестовий вираз"
        example = "usage of test expression"
        tag = "noun"

        body = {
            "expression": "test expression",
            "definition": "definition of test expression",
            "translation": "тестовий вираз",
            "example": "usage of test expression",
            "tag_1": "noun",
            "tag_2": "",
            "tag_3": "",
            "tag_4": "",
            "tag_5": "",
            "grammar_tag": "",
        }

        context = self._get_test_template_context(
            "POST",
            "expressions/list.html",
            "/user/expressions/post/test expression",
            data=body,
            follow_redirects=True,
        )

        expected_expressions = [
            "eccda880-b9fa-40a8-93b7-d0098d1e4e69",
            "4d7993aa-d897-4647-994b-e0625c88f349",
            "542d93d5-6a38-4ce6-95ba-de942ad3b309",
        ]

        context_expressions = [
            str(item["expressionId"]) for item in context["exprs"]
        ]
        self.assertEqual(expected_expressions, context_expressions)

        actual_expressions = self._get_expression(expr_id)
        self.assertEqual(
            1, len(actual_expressions), "Only one expression should be found"
        )

        actual_expression = actual_expressions[0]
        self.assertEqual(expression, actual_expression["expression"])  # type: ignore
        self.assertEqual(definition, actual_expression["definition"])  # type: ignore
        self.assertEqual({"uk": translation}, actual_expression["translations"])  # type: ignore
        self.assertEqual(example, actual_expression["example"])  # type: ignore
        self.assertEqual(tag, actual_expression["tag"])  # type: ignore
        self.assertEqual({}, actual_expression["properties"])  # type: ignore

        expected_llist = [
            ("eccda880-b9fa-40a8-93b7-d0098d1e4e69", 0, 0),
            ("4d7993aa-d897-4647-994b-e0625c88f349", 0, 1),
            ("542d93d5-6a38-4ce6-95ba-de942ad3b309", 1, 2),
        ]

        actual_llist = [
            (item["expressionId"], item["position"], item["practiceCount"])
            for item in self._get_user_llist(self.user_id)
        ]

        self.assertEqual(expected_llist, actual_llist)

    @patch("services.user_expression_service.uuid4")
    def test_post_expression_post_with_grammar_tag(self, mock_uuid):
        expr_id = "eccda880-b9fa-40a8-93b7-d0098d1e4e69"
        mock_uuid.return_value = expr_id

        expression = "test expression"
        definition = "definition of test expression"
        translation = "тестовий вираз"
        example = "usage of test expression"
        tag_1 = "noun"
        tag_2 = "grammar"

        body = {
            "expression": "test expression",
            "definition": "definition of test expression",
            "translation": "тестовий вираз",
            "example": "usage of test expression",
            "tag_1": tag_1,
            "tag_2": tag_2,
            "tag_3": "",
            "tag_4": "",
            "tag_5": "",
            "grammar_tag": "verb pattern",
            "grammar": "test grammar",
        }

        context = self._get_test_template_context(
            "POST",
            "expressions/list.html",
            "/user/expressions/post/test expression",
            data=body,
            follow_redirects=True,
        )

        expected_expressions = [
            "eccda880-b9fa-40a8-93b7-d0098d1e4e69",
            "4d7993aa-d897-4647-994b-e0625c88f349",
            "542d93d5-6a38-4ce6-95ba-de942ad3b309",
        ]
        expected_expression_properties = {
            "grammar": {"verb_pattern": {"text": "test grammar"}}
        }

        context_expressions = [
            str(item["expressionId"]) for item in context["exprs"]
        ]
        self.assertEqual(expected_expressions, context_expressions)

        actual_expressions = self._get_expression(expr_id)
        self.assertEqual(
            2, len(actual_expressions), "Two expression should be found"
        )

        actual_expression = actual_expressions[0]
        self.assertEqual(expression, actual_expression["expression"])  # type: ignore
        self.assertEqual(definition, actual_expression["definition"])  # type: ignore
        self.assertEqual({"uk": translation}, actual_expression["translations"])  # type: ignore
        self.assertEqual(example, actual_expression["example"])  # type: ignore
        self.assertEqual(expected_expression_properties, actual_expression["properties"])  # type: ignore

        self.assertEqual(
            {tag_1, tag_2},
            {actual_expressions[0]["tag"], actual_expressions[1]["tag"]},
        )

        expected_llist = [
            ("eccda880-b9fa-40a8-93b7-d0098d1e4e69", 0, 0),
            ("4d7993aa-d897-4647-994b-e0625c88f349", 0, 1),
            ("542d93d5-6a38-4ce6-95ba-de942ad3b309", 1, 2),
        ]

        actual_llist = [
            (item["expressionId"], item["position"], item["practiceCount"])
            for item in self._get_user_llist(self.user_id)
        ]

        self.assertEqual(expected_llist, actual_llist)

    def test_post_expression_post_with_grammar_tag_with_no_grammar_content(
        self,
    ):
        expression = "test expression"
        definition = "definition of test expression"
        translation = "тестовий вираз"
        example = "usage of test expression"
        tag_1 = "noun"
        tag_2 = "grammar"

        body = {
            "expression": expression,
            "definition": definition,
            "translation": translation,
            "example": example,
            "tag_1": tag_1,
            "tag_2": tag_2,
            "tag_3": "",
            "tag_4": "",
            "tag_5": "",
            "grammar_tag": "verb pattern",
        }

        context = self._get_test_template_context(
            "POST",
            "expressions/post.html",
            "/user/expressions/post/test expression",
            data=body,
            follow_redirects=True,
        )

        self.assertEqual(
            "If expression has tag 'grammar', 'grammar' field can be empty",
            str(context["form"].grammar.errors[0]),
        )

        self.assertEqual([], self._get_expression(expression=expression))

    def test_post_expression_post_with_grammar_tag_with_no_grammar_tag_tag(
        self,
    ):
        expression = "test expression"
        definition = "definition of test expression"
        translation = "тестовий вираз"
        example = "usage of test expression"
        tag_1 = "noun"
        tag_2 = "grammar"

        body = {
            "expression": expression,
            "definition": definition,
            "translation": translation,
            "example": example,
            "tag_1": tag_1,
            "tag_2": tag_2,
            "tag_3": "",
            "tag_4": "",
            "tag_5": "",
            "grammar": "test_grammar",
            "grammar_tag": "",
        }

        context = self._get_test_template_context(
            "POST",
            "expressions/post.html",
            "/user/expressions/post/test expression",
            data=body,
            follow_redirects=True,
        )

        self.assertEqual(
            "If expression has tag 'grammar', 'grammar_tag' field can be empty",
            str(context["form"].grammar_tag.errors[0]),
        )

        self.assertEqual([], self._get_expression(expression=expression))

    def _get_expression(self, expr_id=None, expression=None):
        sql = """
            SELECT
                e.expression,
                e.definition,
                e.translations,
                e.example,
                e.properties,
                t.tag
            FROM
                expressions e
                JOIN tag_expression te ON e.id=te.expression_id
                JOIN tags t ON te.tag_id=t.id
            WHERE
        """

        if expr_id:
            sql += "e.id=%(expr_id)s"

        if expression:
            sql += "e.expression=%(expression)s"

        # sql += "ORDER BY "

        with psycopg2.connect(**self._get_test_db_dsn()) as con:  # type: ignore
            with con.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(
                    sql, {"expr_id": expr_id, "expression": expression}
                )
                data = cur.fetchall()

        return data

    def _get_user_llist(self, user_id):
        sql = """SELECT properties FROM users WHERE id=%(user_id)s"""
        with psycopg2.connect(**self._get_test_db_dsn()) as con:  # type: ignore
            with con.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(sql, {"user_id": user_id})
                data = cur.fetchone()[0]

        return data["challenges"]["dailyTraining"]["learning_list"]
