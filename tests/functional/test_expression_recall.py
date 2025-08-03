from datetime import datetime
from decimal import Decimal

import psycopg2
from psycopg2.extras import DictCursor

from tests.functional.utils import FunctionalTestsHelper


class ExpressionRecallChallengeGetTests(FunctionalTestsHelper):
    def setUp(self):
        super().setUp()

        with open(
            "tests/functional/data/setup_test_expression_recall.sql", "r"
        ) as file:
            sql = file.read()

        self._setup_test_db(sql)

    def test_get_challenge(self):
        user_id = "04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef"
        session = {
            "user": "expression_recall_1@test.mail",
            "user_id": user_id,
        }
        self._set_session(**session)

        context = self._get_test_template_context(
            "GET",
            "exercises/expression_recall_challenge.html",
            "/exercise/expression_recall",
        )

        expected_challenge = {
            "question": "the complete loss or absence of hope",
            "tip": "despair",
            "answer": "despair",
            "expression_id": "24d96f68-46e1-4fb3-b300-81cd89cea435",
            "knowledgeLevel": Decimal("0.50000"),
            "practiceCount": 9,
        }
        self.assertEqual(expected_challenge, context["challenge"])

    def test_get_challenge_nothing_to_recall(self):
        user_id = "ad1a54e9-baa2-4dfc-8b9d-2a884306fa21"
        session = {
            "user": "expression_recall_2@test.mail",
            "user_id": user_id,
        }
        self._set_session(**session)

        self._get_test_template_context(
            "GET",
            "user/index.html",
            "/exercise/expression_recall",
            follow_redirects=True,
        )


class ExpressionRecallChallengePostTests(FunctionalTestsHelper):
    def setUp(self):
        super().setUp()

        with open(
            "tests/functional/data/setup_test_expression_recall.sql", "r"
        ) as file:
            sql = file.read()

        self._setup_test_db(sql)

    def test_submit_successful_challenge(self):
        today = datetime.utcnow().date()
        user_id = "04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef"
        session = {
            "user": "expression_recall_1@test.mail",
            "user_id": user_id,
        }
        self._set_session(**session)

        expr_id = "24d96f68-46e1-4fb3-b300-81cd89cea435"
        form = {
            "expression_id": expr_id,
            "hint": "False",
            "answer": "despair",
        }

        context = self._get_test_template_context(
            "POST",
            "exercises/expression_recall_solution.html",
            "/exercise/expression_recall",
            data=form,
        )

        expected_solution = {
            "correctAnswer": "despair",
            "usersAnswer": "despair",
            "definition": "the complete loss or absence of hope",
            "translation": "відчай",
            "example": None,
        }
        self.assertEqual(expected_solution, context["solution"])

        practice_data = self._get_user_expression_practice_data(
            user_id, expr_id
        )

        self.assertEqual(today, practice_data["last_practice_time"].date())  # type: ignore
        self.assertEqual(Decimal("0.55"), practice_data["knowledge_level"])  # type: ignore
        self.assertEqual(10, practice_data["practice_count"])  # type: ignore

        # Press "Next"
        context = self._get_test_template_context(
            "GET",
            "exercises/expression_recall_challenge.html",
            "/exercise/expression_recall",
        )

        expected_challenge = {
            "question": "coming before something in order, position, or time",
            "tip": "preceding",
            "answer": "preceding",
            "expression_id": "4d7993aa-d897-4647-994b-e0625c88f349",
            "knowledgeLevel": Decimal("0.00000"),
            "practiceCount": 0,
        }
        self.assertEqual(expected_challenge, context["challenge"])

    def test_submit_failed_challenge(self):
        today = datetime.utcnow().date()
        user_id = "04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef"
        session = {
            "user": "expression_recall_1@test.mail",
            "user_id": user_id,
        }
        self._set_session(**session)

        expr_id = "24d96f68-46e1-4fb3-b300-81cd89cea435"
        form = {
            "expression_id": expr_id,
            "hint": "False",
            "answer": "aboba",
        }

        context = self._get_test_template_context(
            "POST",
            "exercises/expression_recall_solution.html",
            "/exercise/expression_recall",
            data=form,
        )

        expected_solution = {
            "correctAnswer": "despair",
            "usersAnswer": "aboba",
            "definition": "the complete loss or absence of hope",
            "translation": "відчай",
            "example": None,
        }
        self.assertEqual(expected_solution, context["solution"])

        practice_data = self._get_user_expression_practice_data(
            user_id, expr_id
        )

        self.assertEqual(today, practice_data["last_practice_time"].date())  # type: ignore
        self.assertEqual(Decimal("0.45"), practice_data["knowledge_level"])  # type: ignore
        self.assertEqual(10, practice_data["practice_count"])  # type: ignore

        # Press "Next"
        context = self._get_test_template_context(
            "GET",
            "exercises/expression_recall_challenge.html",
            "/exercise/expression_recall",
        )

        expected_challenge = {
            "question": "coming before something in order, position, or time",
            "tip": "preceding",
            "answer": "preceding",
            "expression_id": "4d7993aa-d897-4647-994b-e0625c88f349",
            "knowledgeLevel": Decimal("0.00000"),
            "practiceCount": 0,
        }
        self.assertEqual(expected_challenge, context["challenge"])

    def test_submit_challenge_with_hint(self):
        user_id = "04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef"
        session = {
            "user": "expression_recall_1@test.mail",
            "user_id": user_id,
        }
        self._set_session(**session)

        expr_id = "24d96f68-46e1-4fb3-b300-81cd89cea435"
        form = {
            "expression_id": expr_id,
            "hint": "true",
            "answer": "aboba",
        }

        context = self._get_test_template_context(
            "POST",
            "exercises/expression_recall_solution.html",
            "/exercise/expression_recall",
            data=form,
        )

        expected_solution = {
            "correctAnswer": "despair",
            "usersAnswer": "aboba",
            "definition": "the complete loss or absence of hope",
            "translation": "відчай",
            "example": None,
        }
        self.assertEqual(expected_solution, context["solution"])

        practice_data = self._get_user_expression_practice_data(
            user_id, expr_id
        )

        self.assertEqual(datetime(2023, 4, 14).date(), practice_data["last_practice_time"].date())  # type: ignore
        self.assertEqual(Decimal("0.5"), practice_data["knowledge_level"])  # type: ignore
        self.assertEqual(9, practice_data["practice_count"])  # type: ignore

        # Press "Next"
        context = self._get_test_template_context(
            "GET",
            "exercises/expression_recall_challenge.html",
            "/exercise/expression_recall",
        )

        expected_challenge = {
            "question": "the complete loss or absence of hope",
            "tip": "despair",
            "answer": "despair",
            "expression_id": "24d96f68-46e1-4fb3-b300-81cd89cea435",
            "knowledgeLevel": Decimal("0.50000"),
            "practiceCount": 9,
        }
        self.assertEqual(expected_challenge, context["challenge"])

    def _get_user_expression_practice_data(self, user_id, expr_id):
        sql = """
            SELECT
                last_practice_time,
                knowledge_level,
                practice_count
            FROM user_expression
            WHERE expression_id=%(expr_id)s and user_id=%(user_id)s
        """
        params = {"expr_id": expr_id, "user_id": user_id}

        with psycopg2.connect(**self._get_test_db_dsn()) as con:  # type: ignore
            with con.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(sql, params)
                data = cur.fetchone()

        return data


class ExpressionRecallExpressionsTests(FunctionalTestsHelper):
    def setUp(self):
        super().setUp()

        with open(
            "tests/functional/data/setup_test_expression_recall.sql", "r"
        ) as file:
            sql = file.read()

        self._setup_test_db(sql)

    def test_expression_recall_expressions(self):
        user_id = "04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef"
        session = {
            "user": "expression_recall_1@test.mail",
            "user_id": user_id,
        }
        self._set_session(**session)

        context = self._get_test_template_context(
            "GET",
            "exercises/expression_recall_expressions.html",
            "/exercise/expression_recall_expressions",
        )

        expected = [
            "24d96f68-46e1-4fb3-b300-81cd89cea435",
            "4d7993aa-d897-4647-994b-e0625c88f349",
        ]

        actual = [str(expr["expression_id"]) for expr in context["exprs"]]

        self.assertEqual(expected, actual)

    def test_expression_recall_expressions_no_expressions(self):
        user_id = "ad1a54e9-baa2-4dfc-8b9d-2a884306fa21"
        session = {
            "user": "expression_recall_2@test.mail",
            "user_id": user_id,
        }
        self._set_session(**session)

        context = self._get_test_template_context(
            "GET",
            "exercises/expression_recall_expressions.html",
            "/exercise/expression_recall_expressions",
        )

        self.assertEqual([], context["exprs"])
