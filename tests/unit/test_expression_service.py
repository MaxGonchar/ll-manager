from unittest import TestCase
from unittest.mock import patch

from services.expression_service import ExpressionService
from services.exceptions import ExpressionNotFoundException
from tests.unit.fixtures import get_expression, get_tag


class GetExpressionsTests(TestCase):
    def setUp(self):
        self.expr_id_1 = "6a96663a-2344-40e8-b5c8-182a023ac404"
        self.expr_id_2 = "67368827-35cb-4da0-859e-1aa8a7f54d54"
        self.expr_id_3 = "51c6dafe-742c-4334-b137-33024cc23861"

        self.expr_1 = "test expression 1"
        self.expr_2 = "test expression 2"
        self.expr_3 = "test expression 3"

        repo_patcher = patch("services.expression_service.ExpressionsRepo")
        self.mock = repo_patcher.start().return_value.get
        self.addCleanup(repo_patcher.stop)

        self.subject = ExpressionService()

    def test_get(self):
        self.mock.return_value = [
            get_expression(self.expr_id_1, self.expr_1),
            get_expression(self.expr_id_2, self.expr_2),
            get_expression(self.expr_id_3, self.expr_3),
        ]

        expected = [
            {"id": self.expr_id_1, "expression": self.expr_1},
            {"id": self.expr_id_2, "expression": self.expr_2},
            {"id": self.expr_id_3, "expression": self.expr_3},
        ]

        actual = self.subject.get_expressions()

        self.assertEqual(expected, actual)

        self.mock.assert_called_once_with()

    def test_get_no_expressions(self):
        self.mock.return_value = []

        actual = self.subject.get_expressions()

        self.assertEqual([], actual)

        self.mock.assert_called_once_with()


class SearchTests(TestCase):
    def setUp(self):
        repo_patcher = patch("services.expression_service.ExpressionsRepo")
        self.mock = repo_patcher.start().return_value.search
        self.addCleanup(repo_patcher.stop)

        self.subject = ExpressionService()

    def test_search(self):
        expr_id_1 = "6a96663a-2344-40e8-b5c8-182a023ac404"
        expr_1 = "test expression 1"
        pattern = "expression"

        self.mock.return_value = [get_expression(expr_id_1, expr_1)]

        expected = [{"id": expr_id_1, "expression": expr_1}]

        actual = self.subject.search(pattern)

        self.assertEqual(expected, actual)

        self.mock.assert_called_once_with(pattern)

    def test_search_nothing_found(self):
        pattern = "expression"

        self.mock.return_value = []

        actual = self.subject.search(pattern)

        self.assertEqual([], actual)

        self.mock.assert_called_once_with(pattern)


class GetByIDTests(TestCase):
    def setUp(self):
        repo_patcher = patch("services.expression_service.ExpressionsRepo")
        self.mock = repo_patcher.start().return_value.get_by_id
        self.addCleanup(repo_patcher.stop)

        self.subject = ExpressionService()

    def test_expression_with_no_grammar_in_props(self):
        expr_id = "test-expr_id"
        expr = "test expression"
        self.mock.return_value = get_expression(
            expr_id,
            expr,
            tags=[
                get_tag("1", "tag-1"),
                get_tag("2", "tag-2"),
                get_tag("3", "tag-3"),
                get_tag("4", "tag-4"),
                get_tag("5", "tag-5"),
            ],
        )

        actual = self.subject.get_expression_by_id(expr_id)
        expected = {
            "definition": "test definition",
            "example": "example of usage of test expression",
            "expression": "test expression",
            "grammar": None,
            "grammar_tag": None,
            "id": "test-expr_id",
            "tag_1": "tag-1",
            "tag_2": "tag-2",
            "tag_3": "tag-3",
            "tag_4": "tag-4",
            "tag_5": "tag-5",
            "translation": "тестовий вираз",
        }

        self.assertEqual(expected, actual)

        self.mock.assert_called_once_with(expr_id)

    def test_expression_with_less_than_5_tags(self):
        expr_id = "test-expr_id"
        expr = "test expression"
        self.mock.return_value = get_expression(
            expr_id,
            expr,
            tags=[
                get_tag("1", "tag-1"),
                get_tag("2", "tag-2"),
            ],
        )

        actual = self.subject.get_expression_by_id(expr_id)
        expected = {
            "definition": "test definition",
            "example": "example of usage of test expression",
            "expression": "test expression",
            "grammar": None,
            "grammar_tag": None,
            "id": "test-expr_id",
            "tag_1": "tag-1",
            "tag_2": "tag-2",
            "tag_3": None,
            "tag_4": None,
            "tag_5": None,
            "translation": "тестовий вираз",
        }

        self.assertEqual(expected, actual)

        self.mock.assert_called_once_with(expr_id)

    def test_expression_with_grammar_in_props(self):
        expr_id = "test-expr_id"
        expr = "test expression"
        self.mock.return_value = get_expression(
            expr_id,
            expr,
            tags=[
                get_tag("1", "tag-1"),
                get_tag("2", "tag-2"),
            ],
            properties={"grammar": {"verb_pattern": {"text": "test grammar"}}},
        )

        actual = self.subject.get_expression_by_id(expr_id)
        expected = {
            "definition": "test definition",
            "example": "example of usage of test expression",
            "expression": "test expression",
            "grammar": "test grammar",
            "grammar_tag": "verb pattern",
            "id": "test-expr_id",
            "tag_1": "tag-1",
            "tag_2": "tag-2",
            "tag_3": None,
            "tag_4": None,
            "tag_5": None,
            "translation": "тестовий вираз",
        }

        self.assertEqual(expected, actual)

        self.mock.assert_called_once_with(expr_id)

    def test_expression_not_found_raises_exception(self):
        expr_id = "test-expr_id"
        self.mock.return_value = None

        with self.assertRaises(ExpressionNotFoundException):
            self.subject.get_expression_by_id(expr_id)

        self.mock.assert_called_once_with(expr_id)
