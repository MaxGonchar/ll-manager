from decimal import Decimal
from unittest.mock import patch
import json
from copy import deepcopy

import psycopg2
from psycopg2.extras import DictCursor

from dao.user_expressions_dao import UserExpressionsDAO
from repository.exceptions import UserExpressionNotFoundException
from tests.unit.fixtures import get_expression, get_user, get_user_expression
from tests.unit.fixtures import (
    get_tag,
)
from tests.unit.test_repos.utils import BaseRepoTestUtils


class UserExpressionsDAOTestHelper(BaseRepoTestUtils):
    def setUp(self):
        self.user_id_1 = "04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef"
        self.user_properties_1 = {
            "nativeLang": "uk",
            "challenges": {
                "dailyTraining": {
                    "learnListSize": 50,
                    "practiceCountThreshold": 50,
                    "knowledgeLevelThreshold": 0.9,
                    "learning_list": [
                        {
                            "expressionId": "4d7993aa-d897-4647-994b-e0625c88f349",
                            "position": 0,
                            "practiceCount": 0,
                            "knowledgeLevel": "0",
                        },
                        {
                            "expressionId": "24d96f68-46e1-4fb3-b300-81cd89cea435",
                            "position": 0,
                            "practiceCount": 0,
                            "knowledgeLevel": "0",
                        },
                        {
                            "expressionId": "d5c26549-74f7-4930-9c2c-16d10d46e55e",
                            "position": 0,
                            "practiceCount": 0,
                            "knowledgeLevel": "0",
                        },
                    ],
                }
            },
        }
        self.user_1 = {
            "id": self.user_id_1,
            "properties": self.user_properties_1,
        }

        self.user_id_2 = "1bf5c95f-ebe5-4a14-9744-8ad2f3932ef0"
        self.user_properties_2 = {"nativeLang": "uk"}
        self.user_2 = {
            "id": self.user_id_2,
            "properties": self.user_properties_2,
        }

        self.user_id_3 = "14eca254-560b-495f-9410-a1a393641a4e"
        self.user_properties_3 = {"nativeLang": "uk"}
        self.user_3 = {
            "id": self.user_id_3,
            "properties": self.user_properties_3,
        }

        self.expr_1 = {
            "id": "4d7993aa-d897-4647-994b-e0625c88f349",
            "expression": "preceding",
            "definition": "coming before something in order, position, or time",
            "translation": '{"uk": "попередній"}',
            "example": "Aboba expresses its opinion)",
            "added": "2016-06-22 19:10:25",
            "updated": "2016-06-22 19:10:25",
        }
        self.expr_2 = {
            "id": "24d96f68-46e1-4fb3-b300-81cd89cea435",
            "expression": "despair",
            "definition": "the complete loss or absence of hope",
            "translation": '{"uk": "відчай"}',
            "example": "in despair, I hit the bottle",
            "added": "2016-06-22 19:10:26",
            "updated": "2016-06-22 19:10:25",
        }
        self.expr_3 = {
            "id": "d5c26549-74f7-4930-9c2c-16d10d46e55e",
            "expression": "annual",
            "definition": "occurring once every year",
            "translation": '{"uk": "щорічний"}',
            "example": "the sponsored walk became an annual event",
            "added": "2016-06-22 19:10:27",
            "updated": "2016-06-22 19:10:25",
        }
        self.expr_4 = {
            "id": "4eb806c0-a8cd-4ac9-8387-1b79cb97b138",
            "expression": "show of hands",
            "definition": "a vote carried out among a group by the raising of hands",
            "translation": '{"uk": "підняття рук"}',
            "example": "By a show of hands, how many of you would prefer to have the test on Friday?",
            "added": "2016-06-22 19:10:28",
            "updated": "2016-06-22 19:10:25",
        }

        self.us_expr_1 = {
            "user_id": self.user_id_1,
            "expression_id": self.expr_1["id"],
            "added": "2023-04-09 10:10:25",
            "updated": "2023-04-16 10:10:25",
            "properties": "{}",
            "last_practice_time": None,
            "knowledge_level": 0,
            "practice_count": 0,
            "active": 1,
        }
        self.us_expr_2 = {
            "user_id": self.user_id_1,
            "expression_id": self.expr_2["id"],
            "added": "2023-04-10 10:10:25",
            "updated": "2023-04-16 10:10:25",
            "properties": "{}",
            "last_practice_time": None,
            "knowledge_level": 0,
            "practice_count": 0,
            "active": 1,
        }
        self.us_expr_3 = {
            "user_id": self.user_id_1,
            "expression_id": self.expr_3["id"],
            "added": "2023-04-11 10:10:25",
            "updated": "2023-04-16 10:10:25",
            "properties": "{}",
            "last_practice_time": None,
            "knowledge_level": 0,
            "practice_count": 0,
            "active": 1,
        }
        self.us_expr_4 = {
            "user_id": self.user_id_1,
            "expression_id": "4eb806c0-a8cd-4ac9-8387-1b79cb97b138",
            "added": "2023-04-12 10:10:25",
            "updated": "2023-04-16 10:10:25",
            "properties": "{}",
            "last_practice_time": None,
            "knowledge_level": 0,
            "practice_count": 0,
            "active": 1,
        }
        self.us_expr_5 = {
            "user_id": self.user_id_2,
            "expression_id": self.expr_3["id"],
            "added": "2023-04-11 10:10:25",
            "updated": "2023-04-16 10:10:25",
            "properties": "{}",
            "last_practice_time": None,
            "knowledge_level": 0,
            "practice_count": 0,
            "active": 1,
        }
        self.us_expr_6 = {
            "user_id": self.user_id_2,
            "expression_id": "4eb806c0-a8cd-4ac9-8387-1b79cb97b138",
            "added": "2023-04-12 10:10:25",
            "updated": "2023-04-16 10:10:25",
            "properties": "{}",
            "last_practice_time": None,
            "knowledge_level": 0,
            "practice_count": 0,
            "active": 1,
        }
        self.us_expr_7 = {
            "user_id": self.user_id_3,
            "expression_id": self.expr_1["id"],
            "added": "2023-04-09 10:10:25",
            "updated": "2023-04-16 10:10:25",
            "properties": "{}",
            "last_practice_time": "2023-04-16 10:10:25",
            "knowledge_level": 0,
            "practice_count": 0,
            "active": 1,
        }
        self.us_expr_8 = {
            "user_id": self.user_id_3,
            "expression_id": self.expr_2["id"],
            "added": "2023-04-10 10:10:25",
            "updated": "2023-04-16 10:10:25",
            "properties": "{}",
            "last_practice_time": "2023-04-15 10:10:25",
            "knowledge_level": 0,
            "practice_count": 0,
            "active": 1,
        }
        self.us_expr_9 = {
            "user_id": self.user_id_3,
            "expression_id": self.expr_3["id"],
            "added": "2023-04-11 10:10:25",
            "updated": "2023-04-16 10:10:25",
            "properties": "{}",
            "last_practice_time": None,
            "knowledge_level": 0,
            "practice_count": 0,
            "active": 1,
        }
        self.us_expr_10 = {
            "user_id": self.user_id_3,
            "expression_id": self.expr_4["id"],
            "added": "2023-04-12 10:10:25",
            "updated": "2023-04-16 10:10:25",
            "properties": "{}",
            "last_practice_time": "2023-04-14 10:10:25",
            "knowledge_level": 0,
            "practice_count": 1,
            "active": 1,
        }

        self._clear_db()
        self._seed_db_user_record()
        self._seed_db_expression_records(
            [self.expr_1, self.expr_2, self.expr_3, self.expr_4]
        )
        self._seed_db_user_expression_records()

        self.subject = UserExpressionsDAO(self.user_id_1)

    def _clear_db(self):
        self._clean_user_expressions()
        self._clean_expressions()
        self._clean_users()

    def _seed_db_user_record(self):
        sql = f"""
            INSERT INTO users (
                id,
                first,
                last,
                email,
                role,
                password_hash,
                properties,
                added,
                updated,
                last_login
            )
            VALUES (
                '{self.user_id_1}',
                'First',
                'Last',
                'daily_training@test.mail',
                'self-educated',
                'c1a4b7e252281a7649d17a0f9f1d5180d5b5b1783dca84e121bbfcadda4ecc12',
                '{json.dumps(self.user_properties_1)}',
                '2023-04-16 09:10:25',
                '2023-04-16 09:10:25',
                '2023-04-16 09:10:25'
            ), (
                '{self.user_id_2}',
                'First',
                'Last',
                'expression_recall_1@test.mail',
                'self-educated',
                'test-hash',
                '{json.dumps(self.user_properties_2)}',
                '2023-04-16 09:10:25',
                '2023-04-16 09:10:25',
                '2023-04-16 09:10:25'
            ), (
                '{self.user_id_3}',
                'First',
                'Last',
                'expression_recall_2@test.mail',
                'self-educated',
                'test-hash',
                '{json.dumps(self.user_properties_3)}',
                '2023-04-16 09:10:25',
                '2023-04-16 09:10:25',
                '2023-04-16 09:10:25'
            )
        """
        self._execute_sql(sql)

    def _seed_db_user_expression_records(self):
        us_exprs = [
            self.us_expr_1,
            self.us_expr_2,
            self.us_expr_3,
            self.us_expr_4,
            self.us_expr_5,
            self.us_expr_6,
            self.us_expr_7,
            self.us_expr_8,
            self.us_expr_9,
            self.us_expr_10,
        ]

        for us_expr in us_exprs:
            sql = f"""
                INSERT INTO user_expression 
                ({', '.join([k for k, v in us_expr.items() if v is not None])})
                VALUES
                ({', '.join([f"'{str(v)}'" for v in us_expr.values() if v is not None])})
            """
            self._execute_sql(sql)

    def _deep_assert_user_expression(
        self,
        actual,
        expected_user_expression,
        expected_expression,
        expected_user,
    ):
        self._assert_user_expression(expected_user_expression, actual)
        self._assert_expression(expected_expression, actual.expression)
        self._assert_user(expected_user, actual.user)

    def _assert_user_expression(self, expected_user_expression, actual):
        self.assertEqual(
            expected_user_expression["user_id"], str(actual.user_id)
        )
        self.assertEqual(
            expected_user_expression["expression_id"],
            str(actual.expression_id),
        )
        self.assertEqual(expected_user_expression["active"], actual.active)
        self.assertEqual(
            expected_user_expression["knowledge_level"], actual.knowledge_level
        )
        self.assertEqual(
            expected_user_expression["practice_count"], actual.practice_count
        )
        self.assertEqual(
            expected_user_expression["added"],
            actual.added.strftime("%Y-%m-%d %H:%M:%S"),
        )
        self.assertEqual(
            expected_user_expression["updated"],
            actual.updated.strftime("%Y-%m-%d %H:%M:%S"),
        )

        if expected_user_expression["last_practice_time"] is None:
            self.assertIsNone(actual.last_practice_time)
        else:
            self.assertEqual(
                expected_user_expression["last_practice_time"],
                actual.last_practice_time.strftime("%Y-%m-%d %H:%M:%S"),
            )

    def _assert_user(self, expected_user, actual_user):
        self.assertEqual(expected_user["id"], str(actual_user.id))
        self.assertEqual(expected_user["properties"], actual_user.properties)


class GetAllTests(UserExpressionsDAOTestHelper):
    def test_get_all_items(self):
        actual = self.subject.get()

        self.assertEqual(4, len(actual))

        expected = [
            [self.us_expr_4, self.expr_4],
            [self.us_expr_3, self.expr_3],
            [self.us_expr_2, self.expr_2],
            [self.us_expr_1, self.expr_1],
        ]

        for actual_us_expr, expected_us_exp in zip(actual, expected):
            self._deep_assert_user_expression(
                actual_us_expr,
                expected_us_exp[0],
                expected_us_exp[1],
                self.user_1,
            )

    def test_get_particular_set_of_items(self):
        include = [
            self.us_expr_1["expression_id"],
            self.us_expr_2["expression_id"],
        ]

        actual = self.subject.get(include=include)

        self.assertEqual(2, len(actual))

        expected = [
            [self.us_expr_2, self.expr_2],
            [self.us_expr_1, self.expr_1],
        ]

        for actual_us_expr, expected_us_exp in zip(actual, expected):
            self._deep_assert_user_expression(
                actual_us_expr,
                expected_us_exp[0],
                expected_us_exp[1],
                self.user_1,
            )

    def test_get_particular_set_of_items_with_nonexisting_item(self):
        include = [
            self.us_expr_1["expression_id"],
            self.us_expr_2["expression_id"],
            "ecd4b70a-835c-48ed-81b5-2e6684b7f1dd",
        ]

        actual = self.subject.get(include=include)

        self.assertEqual(2, len(actual))

        expected = [
            [self.us_expr_2, self.expr_2],
            [self.us_expr_1, self.expr_1],
        ]

        for actual_us_expr, expected_us_exp in zip(actual, expected):
            self._deep_assert_user_expression(
                actual_us_expr,
                expected_us_exp[0],
                expected_us_exp[1],
                self.user_1,
            )

    def test_get_particular_set_of_items_got_nothing(self):
        include = ["ecd4b70a-835c-48ed-81b5-2e6684b7f1dd"]

        actual = self.subject.get(include=include)

        self.assertEqual([], actual)

    def test_get_all_excluding_particular_set_of_items_with_limit(self):
        actual = self.subject.get(exclude=[self.expr_1["id"]], limit=2)

        self.assertEqual(2, len(actual))

        expected = [
            [self.us_expr_4, self.expr_4],
            [self.us_expr_3, self.expr_3],
        ]

        for actual_us_expr, expected_us_exp in zip(actual, expected):
            self._deep_assert_user_expression(
                actual_us_expr,
                expected_us_exp[0],
                expected_us_exp[1],
                self.user_1,
            )

    def test_get_with_include_and_exclude_raise_exception(self):
        with self.assertRaises(TypeError):
            self.subject.get(include=["1"], exclude=["2"])


class GetByIDTests(UserExpressionsDAOTestHelper):
    def test_get_by_id(self):
        actual = self.subject.get_by_id(self.expr_1["id"])

        self._deep_assert_user_expression(
            actual, self.us_expr_1, self.expr_1, self.user_1
        )

    def test_get_by_nonexisting_id(self):
        actual = self.subject.get_by_id("affa50c3-8f6c-480a-8c05-64fdd42ebe91")

        self.assertIsNone(actual)


class PutTests(UserExpressionsDAOTestHelper):
    @patch("dao.user_expressions_dao.get_current_utc_time")
    def test_put(self, mock_current_time):
        last_practice_time = "2023-05-19 09:34:15"
        knowledge_level = 99.9
        practice_count = 2

        expected_user_expression = deepcopy(self.us_expr_1)
        expected_user_expression["last_practice_time"] = last_practice_time
        expected_user_expression["knowledge_level"] = knowledge_level  # type: ignore
        expected_user_expression["practice_count"] = practice_count  # type: ignore
        expected_user_expression["updated"] = last_practice_time

        mock_current_time.return_value = last_practice_time

        us_expr = self.subject.get_by_id(self.expr_1["id"])

        us_expr.last_practice_time = last_practice_time  # type: ignore
        us_expr.knowledge_level = knowledge_level  # type: ignore
        us_expr.practice_count = practice_count  # type: ignore

        self.subject.put(us_expr)

        actual_user_expression = self._query_user_expression(
            self.expr_1["id"], self.user_id_1
        )

        self.assertEqual(
            expected_user_expression["user_id"],
            actual_user_expression["user_id"],
        )
        self.assertEqual(
            expected_user_expression["expression_id"],
            actual_user_expression["expression_id"],
        )
        self.assertEqual(
            expected_user_expression["active"],
            actual_user_expression["active"],
        )
        self.assertEqual(
            expected_user_expression["last_practice_time"],
            actual_user_expression["last_practice_time"].strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        )
        self.assertEqual(
            expected_user_expression["knowledge_level"],
            float(actual_user_expression["knowledge_level"]),
        )
        self.assertEqual(
            expected_user_expression["practice_count"],
            actual_user_expression["practice_count"],
        )
        self.assertEqual(
            expected_user_expression["added"],
            actual_user_expression["added"].strftime("%Y-%m-%d %H:%M:%S"),
        )
        self.assertEqual(
            expected_user_expression["updated"],
            actual_user_expression["updated"].strftime("%Y-%m-%d %H:%M:%S"),
        )

    @patch("dao.user_expressions_dao.get_current_utc_time")
    def test_put_when_item_was_deleted_from_db_rises_exception(
        self, mock_current_time
    ):
        mock_current_time.return_value = "2023-05-19 09:34:15"

        us_expr = self.subject.get_by_id(self.expr_1["id"])

        self._delete_user_expression(self.expr_1["id"], self.user_id_1)

        with self.assertRaises(UserExpressionNotFoundException):
            self.subject.put(us_expr)

    def _delete_user_expression(self, expr_id, user_id):
        sql = """
            DELETE FROM user_expression
            WHERE expression_id=%(expression_id)s AND user_id=%(user_id)s
        """
        params = {"expression_id": expr_id, "user_id": user_id}
        with psycopg2.connect(**self._get_test_db_dsn()) as con:  # type: ignore
            with con.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(sql, params)

    def _query_user_expression(self, expr_id, user_id):
        sql = """
            SELECT * FROM user_expression
            WHERE expression_id=%(expression_id)s AND user_id=%(user_id)s
        """
        params = {"expression_id": expr_id, "user_id": user_id}
        with psycopg2.connect(**self._get_test_db_dsn()) as con:  # type: ignore
            with con.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(sql, params)
                data = cur.fetchone()
        con.close()
        return data


class SearchTests(UserExpressionsDAOTestHelper):
    def test_search(self):
        query = "hand"

        actual = self.subject.search(query)
        expected = [[self.us_expr_4, self.expr_4]]

        for actual_us_expr, expected_us_exp in zip(actual, expected):
            self._deep_assert_user_expression(
                actual_us_expr,
                expected_us_exp[0],
                expected_us_exp[1],
                self.user_1,
            )


class CountTests(UserExpressionsDAOTestHelper):
    def test_count(self):
        self.assertEqual(4, self.subject.count())


class PostTests(BaseRepoTestUtils):
    def setUp(self):
        self._clean_expressions()
        self._clean_tags()
        self._clean_user_expressions()
        self._clean_users()

    def test_post(self):
        user_id = "142e3b76-9e13-4ea2-979e-9eedbd3f8139"
        tag_id = "049cab60-c19f-499e-8e2d-6f9a84fb4b4b"
        expr_id = "3be753b8-360b-4a0c-8205-881131b9aa9a"
        expr = "test-expression"
        expression_properties = {"test": "properties"}

        user = get_user(user_id)
        tag = get_tag(tag_id)
        expression = get_expression(
            expr_id, expr, properties=expression_properties
        )
        expression.tags = [tag]
        user_expr = get_user_expression(user_id, user, expression)

        UserExpressionsDAO(user_id).post(user_expr)

        actual = self._get_db_data(expr_id)

        self.assertEqual(user_id, actual["user_id"])
        self.assertEqual(expr, actual["expression"])
        self.assertEqual(expression_properties, actual["expr_props"])
        self.assertEqual(tag_id, actual["tag_id"])

    def _get_db_data(self, expr_id):
        sql = """
            SELECT
                u.id AS user_id,
                e.expression AS expression,
                e.properties AS expr_props,
                t.id AS tag_id
            FROM users u
            JOIN user_expression ue ON u.id=ue.user_id
            JOIN expressions e on ue.expression_id=e.id
            JOIN tag_expression te ON e.id=te.expression_id
            JOIN tags t ON te.tag_id=t.id
            WHERE e.id=%(expression_id)s
        """
        with psycopg2.connect(**self._get_test_db_dsn()) as con:  # type: ignore
            with con.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(sql, {"expression_id": expr_id})
                data = cur.fetchone()
        con.close()

        return data


class CountTrainedExpressionsTests(UserExpressionsDAOTestHelper):
    def test_count_trained_expressions(self):
        self.assertEqual(
            3, UserExpressionsDAO(self.user_id_3).count_trained_expressions()
        )


class GetTrainedExpressionsTests(UserExpressionsDAOTestHelper):
    def test_get_all_trained_expressions(self):
        subject = UserExpressionsDAO(self.user_id_3)

        actual = subject.get_trained_expressions()

        expected = [
            [self.us_expr_10, self.expr_4],
            [self.us_expr_8, self.expr_2],
            [self.us_expr_7, self.expr_1],
        ]

        self.assertEqual(len(expected), len(actual))

        for actual_us_expr, expected_us_exp in zip(actual, expected):
            self._deep_assert_user_expression(
                actual_us_expr,
                expected_us_exp[0],
                expected_us_exp[1],
                self.user_3,
            )

    def test_get_all_trained_expressions_with_limit(self):
        subject = UserExpressionsDAO(self.user_id_3)

        actual = subject.get_trained_expressions(limit=2)

        expected = [
            [self.us_expr_10, self.expr_4],
            [self.us_expr_8, self.expr_2],
        ]

        self.assertEqual(len(expected), len(actual))

        for actual_us_expr, expected_us_exp in zip(actual, expected):
            self._deep_assert_user_expression(
                actual_us_expr,
                expected_us_exp[0],
                expected_us_exp[1],
                self.user_3,
            )

    def test_get_all_trained_expressions_with_excludes(self):
        subject = UserExpressionsDAO(self.user_id_3)

        actual = subject.get_trained_expressions(
            excludes=[self.us_expr_8["expression_id"]]
        )

        expected = [
            [self.us_expr_10, self.expr_4],
            [self.us_expr_7, self.expr_1],
        ]

        self.assertEqual(len(expected), len(actual))

        for actual_us_expr, expected_us_exp in zip(actual, expected):
            self._deep_assert_user_expression(
                actual_us_expr,
                expected_us_exp[0],
                expected_us_exp[1],
                self.user_3,
            )

    def test_get_all_trained_expressions_with_limit_and_exclude(self):
        subject = UserExpressionsDAO(self.user_id_3)

        actual = subject.get_trained_expressions(
            limit=1, excludes=[self.us_expr_8["expression_id"]]
        )

        expected = [
            [self.us_expr_10, self.expr_4],
        ]

        self.assertEqual(len(expected), len(actual))

        for actual_us_expr, expected_us_exp in zip(actual, expected):
            self._deep_assert_user_expression(
                actual_us_expr,
                expected_us_exp[0],
                expected_us_exp[1],
                self.user_3,
            )

    def test_get_all_trained_expressions_no_trained_expressions(self):
        subject = UserExpressionsDAO(self.user_id_2)

        actual = subject.get_trained_expressions()

        self.assertEqual([], actual)


class CountTrainedExpressionsHavingContextTests(UserExpressionsDAOTestHelper):
    def setUp(self):
        super().setUp()

        self._clean_expression_context()

        self.us_expr_7_context_1 = {
            "id": "4dbefd5f-e9a8-4b16-b2cc-03ea9ae767ad",
            "expression_id": self.us_expr_7["expression_id"],
            "sentence": "test sentence 1",
            "translation": {"uk": "тестове речення 1"},
            "template": {"tpl": "{} sentence 1", "values": ["test"]},
            "added": "2016-06-22 19:10:25",
            "updated": "2016-06-22 19:10:25",
        }
        self.us_expr_7_context_2 = {
            "id": "e2b0af2a-0453-422e-a2ee-1809901d9145",
            "expression_id": self.us_expr_7["expression_id"],
            "sentence": "test sentence 2",
            "translation": {"uk": "тестове речення 2"},
            "template": {"tpl": "{} sentence 2", "values": ["test"]},
            "added": "2016-06-22 19:10:26",
            "updated": "2016-06-22 19:10:26",
        }
        self.us_expr_8_context_1 = {
            "id": "b4d98798-3a6a-4f24-b81c-36f4a12339ba",
            "expression_id": self.us_expr_8["expression_id"],
            "sentence": "test sentence 3",
            "translation": {"uk": "тестове речення 2"},
            "template": {"tpl": "{} sentence 3", "values": ["test"]},
            "added": "2016-06-22 19:10:26",
            "updated": "2016-06-22 19:10:26",
        }

        self._seed_expression_context(self.us_expr_7_context_1)
        self._seed_expression_context(self.us_expr_7_context_2)
        self._seed_expression_context(self.us_expr_8_context_1)

    def test_count(self):
        self.assertEqual(
            2,
            UserExpressionsDAO(
                self.user_3["id"]
            ).count_trained_expressions_having_context(),
        )


class BulkUpdateTests(UserExpressionsDAOTestHelper):
    def test_update(self):
        subject = UserExpressionsDAO(self.user_id_1)

        user_expr_1 = subject.get_by_id(self.expr_1["id"])
        user_expr_2 = subject.get_by_id(self.expr_2["id"])

        user_expr_1.knowledge_level = 0.5
        user_expr_1.practice_count = 1
        user_expr_2.knowledge_level = 0.7
        user_expr_2.practice_count = 2
        user_expr_1.last_practice_time = "2023-05-19 09:34:15"
        user_expr_2.last_practice_time = "2023-05-19 09:34:16"

        subject.bulk_update([user_expr_1, user_expr_2])

        updated_user_expr_1 = subject.get_by_id(self.expr_1["id"])
        updated_user_expr_2 = subject.get_by_id(self.expr_2["id"])
        self.assertEqual(Decimal("0.5"), updated_user_expr_1.knowledge_level)
        self.assertEqual(1, updated_user_expr_1.practice_count)
        self.assertEqual(
            "2023-05-19 09:34:15",
            updated_user_expr_1.last_practice_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        )
        self.assertEqual(Decimal("0.7"), updated_user_expr_2.knowledge_level)
        self.assertEqual(2, updated_user_expr_2.practice_count)
        self.assertEqual(
            "2023-05-19 09:34:16",
            updated_user_expr_2.last_practice_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        )
