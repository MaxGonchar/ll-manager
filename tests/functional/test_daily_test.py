from unittest.mock import ANY
from datetime import datetime
from decimal import Decimal

import psycopg2
from psycopg2.extras import DictCursor

from tests.functional.utils import FunctionalTestsHelper


class DailyTestTest(FunctionalTestsHelper):
    def setUp(self):
        super().setUp()

        with open(
            "tests/functional/data/setup_test_daily_training.sql", "r"
        ) as file:
            sql = file.read()

        self._setup_test_db(sql)

    def test_daily_training_get(self):
        user_id = "04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef"
        session = {
            "user": "daily_training@test.mail",
            "user_id": user_id,
        }
        self._set_session(**session)
        context = self._get_test_template_context(
            "GET",
            "exercises/daily_training_challenge.html",
            "/exercise/daily-training",
        )

        expected_challenge = {
            "question": "coming before something in order, position, or time",
            "tip": "preceding",
            "answer": "preceding",
            "expression_id": "4d7993aa-d897-4647-994b-e0625c88f349",
        }
        self.assertEqual(expected_challenge, context["challenge"])

    def test_daily_training_get_nothing_to_test(self):
        user_id = "7b211e90-1262-4462-aba8-c765dc045359"
        session = {
            "user": "nothing_to_test@test.mail",
            "user_id": user_id,
        }
        self._set_session(**session)
        self._get_test_template_context(
            "GET",
            "user/index.html",
            "/exercise/daily-training",
            follow_redirects=True,
        )

    def test_submit_successful_test(self):
        today = datetime.utcnow().date()
        user_id = "04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef"
        session = {
            "user": "daily_training@test.mail",
            "user_id": user_id,
        }
        self._set_session(**session)
        expr_id = "4d7993aa-d897-4647-994b-e0625c88f349"
        form = {
            "expression_id": expr_id,
            "hint": "False",
            "answer": "preceding",
        }

        context = self._get_test_template_context(
            "POST",
            "exercises/daily_training_solution.html",
            "/exercise/daily-training",
            data=form,
        )

        expected_solution = {
            "correctAnswer": "preceding",
            "usersAnswer": "preceding",
            "definition": "coming before something in order, position, or time",
            "translation": "попередній",
            "example": None,
        }

        self.assertEqual(expected_solution, context["solution"])

        # Press "Next"
        context = self._get_test_template_context(
            "GET",
            "exercises/daily_training_challenge.html",
            "/exercise/daily-training",
        )
        expected_challenge = {
            "question": "the complete loss or absence of hope",
            "tip": "despair",
            "answer": "despair",
            "expression_id": "24d96f68-46e1-4fb3-b300-81cd89cea435",
        }
        self.assertEqual(expected_challenge, context["challenge"])

        expected_exprs_learn_list = [
            {
                "expressionId": "24d96f68-46e1-4fb3-b300-81cd89cea435",
                "knowledgeLevel": 0,
                "position": 0,
                "practiceCount": 0,
                "lastPracticeTime": None,
            },
            {
                "expressionId": "4d7993aa-d897-4647-994b-e0625c88f349",
                "knowledgeLevel": 1,
                "position": 1,
                "practiceCount": 1,
                "lastPracticeTime": today,
            },
            {
                "expressionId": "d5c26549-74f7-4930-9c2c-16d10d46e55e",
                "knowledgeLevel": 0,
                "position": 0,
                "practiceCount": 0,
                "lastPracticeTime": None,
            },
        ]

        practice_data = self._get_practice_data(expr_id, user_id)
        self.assertEqual(today, practice_data["last_practice_time"].date())  # type: ignore
        self.assertEqual(1, practice_data["knowledge_level"])  # type: ignore
        self.assertEqual(1, practice_data["practice_count"])  # type: ignore

        self._assert_learn_list(expected_exprs_learn_list, self._get_user_exprs_learn_list(user_id))  # type: ignore

    def test_submit_failed_test(self):
        today = datetime.utcnow().date()
        user_id = "e0105858-97ef-4a0a-a9d8-c80b89a800a3"
        session = {
            "user": "failed_test@test.mail",
            "user_id": user_id,
        }
        self._set_session(**session)
        expr_id = "4d7993aa-d897-4647-994b-e0625c88f349"
        form = {
            "expression_id": expr_id,
            "hint": "False",
            "answer": "aboba",
        }

        context = self._get_test_template_context(
            "POST",
            "exercises/daily_training_solution.html",
            "/exercise/daily-training",
            data=form,
        )
        expected_solution = {
            "correctAnswer": "preceding",
            "usersAnswer": "aboba",
            "definition": "coming before something in order, position, or time",
            "translation": "попередній",
            "example": None,
        }

        self.assertEqual(expected_solution, context["solution"])

        # Press "Next"
        context = self._get_test_template_context(
            "GET",
            "exercises/daily_training_challenge.html",
            "/exercise/daily-training",
        )

        expected_challenge = {
            "question": "the complete loss or absence of hope",
            "tip": "despair",
            "answer": "despair",
            "expression_id": "24d96f68-46e1-4fb3-b300-81cd89cea435",
        }
        self.assertEqual(expected_challenge, context["challenge"])

        expected_exprs_learn_list = [
            {
                "expressionId": "24d96f68-46e1-4fb3-b300-81cd89cea435",
                "knowledgeLevel": 0,
                "position": 0,
                "practiceCount": 0,
                "lastPracticeTime": None,
            },
            {
                "expressionId": "4d7993aa-d897-4647-994b-e0625c88f349",
                "knowledgeLevel": 0,
                "position": 1,
                "practiceCount": 1,
                "lastPracticeTime": today,
            },
            {
                "expressionId": "d5c26549-74f7-4930-9c2c-16d10d46e55e",
                "knowledgeLevel": 0,
                "position": 0,
                "practiceCount": 0,
                "lastPracticeTime": None,
            },
        ]

        practice_data = self._get_practice_data(expr_id, user_id)
        self.assertEqual(today, practice_data["last_practice_time"].date())  # type: ignore
        self.assertEqual(Decimal("0.66667"), practice_data["knowledge_level"])  # type: ignore
        self.assertEqual(3, practice_data["practice_count"])  # type: ignore

        self._assert_learn_list(
            expected_exprs_learn_list, self._get_user_exprs_learn_list(user_id)
        )

    def test_submit_after_hint(self):
        user_id = "04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef"
        session = {
            "user": "daily_training@test.mail",
            "user_id": user_id,
        }
        self._set_session(**session)
        expr_id = "4d7993aa-d897-4647-994b-e0625c88f349"
        form = {
            "expression_id": expr_id,
            "hint": "true",
            "answer": "preceding",
        }

        context = self._get_test_template_context(
            "POST",
            "exercises/daily_training_solution.html",
            "/exercise/daily-training",
            data=form,
        )
        expected_solution = {
            "correctAnswer": "preceding",
            "usersAnswer": "preceding",
            "definition": "coming before something in order, position, or time",
            "translation": "попередній",
            "example": None,
        }

        self.assertEqual(expected_solution, context["solution"])

        # Press "Next"
        context = self._get_test_template_context(
            "GET",
            "exercises/daily_training_challenge.html",
            "/exercise/daily-training",
        )

        expected_challenge = {
            "question": "coming before something in order, position, or time",
            "tip": "preceding",
            "answer": "preceding",
            "expression_id": "4d7993aa-d897-4647-994b-e0625c88f349",
        }
        self.assertEqual(expected_challenge, context["challenge"])

        expected_exprs_learn_list = [
            {
                "expressionId": "4d7993aa-d897-4647-994b-e0625c88f349",
                "knowledgeLevel": 0,
                "position": 0,
                "practiceCount": 0,
            },
            {
                "expressionId": "24d96f68-46e1-4fb3-b300-81cd89cea435",
                "knowledgeLevel": 0,
                "position": 0,
                "practiceCount": 0,
            },
            {
                "expressionId": "d5c26549-74f7-4930-9c2c-16d10d46e55e",
                "knowledgeLevel": 0,
                "position": 0,
                "practiceCount": 0,
            },
        ]

        practice_data = self._get_practice_data(expr_id, user_id)
        self.assertEqual(datetime(2023, 4, 17).date(), practice_data["last_practice_time"].date())  # type: ignore
        self.assertEqual(0, practice_data["knowledge_level"])  # type: ignore
        self.assertEqual(0, practice_data["practice_count"])  # type: ignore
        self.assertEqual(expected_exprs_learn_list, self._get_user_exprs_learn_list(user_id))  # type: ignore

    def _get_practice_data(self, expr_id, user_id):
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

    def _get_user_exprs_learn_list(self, user_id):
        sql = """
            SELECT properties
            FROM users
            WHERE id=%(user_id)s
        """
        with psycopg2.connect(**self._get_test_db_dsn()) as con:  # type: ignore
            with con.cursor() as cur:
                cur.execute(sql, {"user_id": user_id})
                data = cur.fetchone()
        props = data[0]  # type: ignore

        return props["challenges"]["dailyTraining"]["learning_list"]

    def _assert_learn_list(self, expected, actual):
        self.assertEqual(
            len(expected),
            len(actual),
            "expected and actual learn lists have different size",
        )

        for expected_item, actual_item in zip(expected, actual):
            self.assertEqual(
                expected_item["expressionId"], actual_item["expressionId"]
            )
            self.assertEqual(
                expected_item["knowledgeLevel"], actual_item["knowledgeLevel"]
            )
            self.assertEqual(
                expected_item["position"], actual_item["position"]
            )
            self.assertEqual(
                expected_item["practiceCount"], actual_item["practiceCount"]
            )

            if expected_item["lastPracticeTime"] is None:
                self.assertIsNone(actual_item["lastPracticeTime"])
            else:
                expected_time = expected_item["lastPracticeTime"].strftime(
                    "%Y-%m-%d"
                )
                actual_time = actual_item["lastPracticeTime"].split()[0]

                self.assertEqual(expected_time, actual_time)


class DailyTrainingExpressionsTests(FunctionalTestsHelper):
    def setUp(self):
        super().setUp()

        with open(
            "tests/functional/data/setup_test_daily_training.sql", "r"
        ) as file:
            sql = file.read()

        self._setup_test_db(sql)

    def test_get_daily_training_expressions(self):
        user_id = "ca5e9524-30fc-4948-b167-63b6fe720220"
        session = {
            "user": "get_training_expressions@test.mail",
            "user_id": user_id,
        }
        self._set_session(**session)

        context = self._get_test_template_context(
            "GET",
            "exercises/daily_training_expressions.html",
            "/exercise/daily-training-expressions",
        )

        expected_expressions = [
            "24d96f68-46e1-4fb3-b300-81cd89cea435",
            "4d7993aa-d897-4647-994b-e0625c88f349",
            "d5c26549-74f7-4930-9c2c-16d10d46e55e",
        ]

        actual_expressions = [
            expr["expression_id"] for expr in context["exprs"]
        ]

        self.assertEqual(expected_expressions, actual_expressions)

    def test_get_daily_training_expressions_no_expressions(self):
        user_id = "9a18dfdd-57b3-41d0-b2f2-682ce8bce316"
        session = {
            "user": "get_training_expressions_no@test.mail",
            "user_id": user_id,
        }
        self._set_session(**session)

        context = self._get_test_template_context(
            "GET",
            "exercises/daily_training_expressions.html",
            "/exercise/daily-training-expressions",
        )

        self.assertEqual([], context["exprs"])


class DailyTrainingAddExpressionTests(FunctionalTestsHelper):
    def setUp(self):
        super().setUp()

        with open(
            "tests/functional/data/setup_test_daily_training.sql", "r"
        ) as file:
            sql = file.read()

        self._setup_test_db(sql)

    def test_add_expression(self):
        user_id = "ba2c3934-daa2-48b0-bda5-8e34b412dec7"
        session = {
            "user": "test_add_expression@test.mail",
            "user_id": user_id,
        }
        self._set_session(**session)

        self._get_test_template_context(
            "GET",
            "expressions/list.html",
            "/user/expressions/d5c26549-74f7-4930-9c2c-16d10d46e55e/add-to-daily-training",
            follow_redirects=True,
        )

        context = self._get_test_template_context(
            "GET",
            "exercises/daily_training_expressions.html",
            "/exercise/daily-training-expressions",
        )

        actual_expressions = [
            expr["expression_id"] for expr in context["exprs"]
        ]
        expected_expressions = [
            "24d96f68-46e1-4fb3-b300-81cd89cea435",
            "4d7993aa-d897-4647-994b-e0625c88f349",
            "d5c26549-74f7-4930-9c2c-16d10d46e55e",
        ]

        self.assertEqual(expected_expressions, actual_expressions)

    def test_add_expression_to_empty_llist(self):
        user_id = "416b0b33-43e2-4f3c-80bb-0a4bacce9d6f"
        session = {
            "user": "tadd_expression_to_empty_llist@test.mail",
            "user_id": user_id,
        }
        self._set_session(**session)

        self._get_test_template_context(
            "GET",
            "expressions/list.html",
            "/user/expressions/d5c26549-74f7-4930-9c2c-16d10d46e55e/add-to-daily-training",
            follow_redirects=True,
        )

        context = self._get_test_template_context(
            "GET",
            "exercises/daily_training_expressions.html",
            "/exercise/daily-training-expressions",
        )

        actual_expressions = [
            expr["expression_id"] for expr in context["exprs"]
        ]
        expected_expressions = ["d5c26549-74f7-4930-9c2c-16d10d46e55e"]

        self.assertEqual(expected_expressions, actual_expressions)

    def test_add_item_to_learn_list_when_llist_has_already_max_size_is_ok(
        self,
    ):
        user_id = "ec451b4d-65d9-41dd-9ca3-60cc58a5381b"
        expr_id = "d5c26549-74f7-4930-9c2c-16d10d46e55e"
        session = {
            "user": "tadd_expression_to_max_llist@test.mail",
            "user_id": user_id,
        }

        self._set_session(**session)

        self._get_test_template_context(
            "GET",
            "expressions/list.html",
            f"/user/expressions/{expr_id}/add-to-daily-training",
            follow_redirects=True,
        )
        context = self._get_test_template_context(
            "GET",
            "exercises/daily_training_expressions.html",
            "/exercise/daily-training-expressions",
        )
        actual_expressions = [
            expr["expression_id"] for expr in context["exprs"]
        ]
        expected_expressions = [
            "24d96f68-46e1-4fb3-b300-81cd89cea435",
            "4d7993aa-d897-4647-994b-e0625c88f349",
            "d5c26549-74f7-4930-9c2c-16d10d46e55e",
        ]

        self.assertEqual(expected_expressions, actual_expressions)


class DailyTrainingRemoveExpressionTests(FunctionalTestsHelper):
    def setUp(self):
        super().setUp()

        with open(
            "tests/functional/data/setup_test_daily_training.sql", "r"
        ) as file:
            sql = file.read()

        self._setup_test_db(sql)

    def test_remove_expression(self):
        user_id = "f2f80eed-9c54-4318-b44f-0c73593c550b"
        session = {
            "user": "test_remove_expression@test.mail",
            "user_id": user_id,
        }
        self._set_session(**session)

        self._get_test_template_context(
            "GET",
            "exercises/daily_training_expressions.html",
            "exercise/d5c26549-74f7-4930-9c2c-16d10d46e55e/delete",
            follow_redirects=True,
        )

        context = self._get_test_template_context(
            "GET",
            "exercises/daily_training_expressions.html",
            "/exercise/daily-training-expressions",
        )

        actual_expressions = [
            expr["expression_id"] for expr in context["exprs"]
        ]
        expected_expressions = [
            "d5c26549-74f7-4930-9c2c-16d10d46e55e",
            "4d7993aa-d897-4647-994b-e0625c88f349",
        ]

        self.assertEqual(expected_expressions, actual_expressions)


class DailyTrainingUpdateSettingsTests(FunctionalTestsHelper):
    def setUp(self):
        super().setUp()

        with open(
            "tests/functional/data/setup_test_daily_training.sql", "r"
        ) as file:
            sql = file.read()

        self._setup_test_db(sql)

    def test_get_settings(self):
        user_id = "1c57cf5b-d6c4-4bc4-8d49-d2ff88753bbc"
        session = {
            "user": "test_get_settings@test.mail",
            "user_id": user_id,
        }
        self._set_session(**session)

        context = self._get_test_template_context(
            "GET",
            "exercises/daily_training_settings.html",
            "/exercise/settings",
        )

        self.assertEqual(3, context["form"].data["llist_size"])
        self.assertEqual(50, context["form"].data["practice_count_threshold"])
        self.assertEqual(90, context["form"].data["knowledge_level_threshold"])

    def test_update_settings(self):
        user_id = "1c57cf5b-d6c4-4bc4-8d49-d2ff88753bbc"
        session = {
            "user": "test_get_settings@test.mail",
            "user_id": user_id,
        }
        self._set_session(**session)

        form = {
            "llist_size": 5,
            "practice_count_threshold": 60,
            "knowledge_level_threshold": 85,
        }

        update_context = self._get_test_template_context(
            "POST",
            "exercises/daily_training_settings.html",
            "/exercise/settings",
            data=form,
            follow_redirects=True,
        )

        self.assertEqual(form, update_context["form"].data)

        get_context = self._get_test_template_context(
            "GET",
            "exercises/daily_training_expressions.html",
            "/exercise/daily-training-expressions",
        )

        expected_expression_ids = [
            ("d5c26549-74f7-4930-9c2c-16d10d46e55e", 0.5, 7),
            ("24d96f68-46e1-4fb3-b300-81cd89cea435", 0.4, 6),
            ("4d7993aa-d897-4647-994b-e0625c88f349", 0.3, 3),
            ("4eb806c0-a8cd-4ac9-8387-1b79cb97b138", 0.0, 0),
            ("a0a68135-bc73-4025-a754-966450fa6cac", 0.0, 0),
        ]

        actual_expressions = [
            (
                expr["expression_id"],
                expr["knowledge_level"],
                expr["practice_count"],
            )
            for expr in get_context["exprs"]
        ]

        self.assertEqual(expected_expression_ids, actual_expressions)
