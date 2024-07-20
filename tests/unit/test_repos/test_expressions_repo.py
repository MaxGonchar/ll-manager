from tests.unit.test_repos.utils import BaseRepoTestUtils
from repository.expressions_repo import ExpressionsRepo


class ExpressionsRepoTestHelper(BaseRepoTestUtils):
    def setUp(self):
        self.expr_1 = {
            "id": "4d7993aa-d897-4647-994b-e0625c88f349",
            "expression": "preceding",
            "definition": "coming before something in order, position, or time",
            "translation": '{"uk": "попередній"}',
            "example": "Aboba expresses its opinion)",
            "added": "2016-06-22 19:10:26",
            "updated": "2016-06-22 19:10:25",
            "properties": '{"grammar": {"verb_pattern": {"text": "test grammar"}}}',
        }
        self.expr_2 = {
            "id": "24d96f68-46e1-4fb3-b300-81cd89cea435",
            "expression": "despair",
            "definition": "the complete loss or absence of hope",
            "translation": '{"uk": "відчай"}',
            "example": "in despair, I hit the bottle",
            "added": "2016-06-22 19:10:24",
            "updated": "2016-06-22 19:10:25",
        }
        self.expr_3 = {
            "id": "d5c26549-74f7-4930-9c2c-16d10d46e55e",
            "expression": "annual",
            "definition": "occurring once every year",
            "translation": '{"uk": "щорічний"}',
            "example": "the sponsored walk became an annual event",
            "added": "2016-06-22 19:10:25",
            "updated": "2016-06-22 19:10:25",
        }

        self.exprs = [self.expr_1, self.expr_2, self.expr_3]

        self._clean_expressions()

        self._seed_db_expression_records(self.exprs)

        self.subject = ExpressionsRepo()


class GetTests(ExpressionsRepoTestHelper):
    def test_get(self):
        expected = [self.expr_1, self.expr_3, self.expr_2]
        actual = self.subject.get()

        self.assertEqual(len(expected), len(actual))

        for expected_expr, actual_expr in zip(expected, actual):
            self._assert_expression(expected_expr, actual_expr)


class SearchTests(ExpressionsRepoTestHelper):
    def test_search(self):
        pattern = "annual"

        expected = [self.expr_3]
        actual = self.subject.search(pattern)

        self.assertEqual(len(expected), len(actual))
        self._assert_expression(expected[0], actual[0])

    def test_search_not_found_returns_empty_list(self):
        pattern = "qwe"

        self.assertEqual([], self.subject.search(pattern))


class GetByIDTests(ExpressionsRepoTestHelper):
    def test_get(self):
        expr_id = "4d7993aa-d897-4647-994b-e0625c88f349"

        actual = self.subject.get_by_id(expr_id)

        self._assert_expression(self.expr_1, actual)

    def test_get_no_expression_returns_none(self):
        expr_id = "50bbc8ec-b8c7-4b37-9511-bb5ea799c227"

        self.assertIsNone(self.subject.get_by_id(expr_id))
