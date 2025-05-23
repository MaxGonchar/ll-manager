import json

import psycopg2
from psycopg2.extras import DictCursor

from tests.unit.test_repos.utils import BaseRepoTestUtils
from dao.user_dao import UsersDAO
from repository.exceptions import UserAlreadyExistsException
from tests.unit.fixtures import get_user


class UsersRepoTestsHelper(BaseRepoTestUtils):
    def setUp(self):
        self.user_id = "32084fc2-2b2a-41ce-ac9a-27d8d6de813d"
        self.first = "First"
        self.last = "Last"
        self.email = "get_user_by_id@test.mail"
        self.role = "self-educated"
        self.password_hash = (
            "c1a4b7e252281a7649d17a0f9f1d5180d5b5b1783dca84e121bbfcadda4ecc12"
        )
        self.added = "2023-04-16 09:10:25"
        self.updated = "2023-04-16 09:10:25"
        self.last_login = "2023-04-16 09:10:25"
        self.properties = {
            "nativeLang": "uk",
            "challenges": {
                "dailyTraining": {
                    "learnListSize": 50,
                    "practiceCountThreshold": 50,
                    "knowledgeLevelThreshold": 0.9,
                    "learning_list": [],
                }
            },
        }

        self._clean_users()
        self._seed_db_user_record()

        self.subject = UsersDAO()

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
                '{self.user_id}',
                '{self.first}',
                '{self.last}',
                '{self.email}',
                '{self.role}',
                '{self.password_hash}',
                '{json.dumps(self.properties)}',
                '{self.added}',
                '{self.updated}',
                '{self.last_login}'
            )
        """
        self._execute_sql(sql)

    def _assert_user(self, actual):
        self.assertEqual(self.user_id, str(actual.id))  # type: ignore
        self.assertEqual(self.first, actual.first)  # type: ignore
        self.assertEqual(self.last, actual.last)  # type: ignore
        self.assertEqual(self.email, actual.email)  # type: ignore
        self.assertEqual(self.role, actual.role)  # type: ignore
        self.assertEqual(self.password_hash, actual.password_hash)  # type: ignore
        self.assertEqual(self.properties, actual.properties)  # type: ignore
        self.assertEqual(self.added, actual.added.strftime("%Y-%m-%d %H:%M:%S"))  # type: ignore
        self.assertEqual(self.updated, actual.updated.strftime("%Y-%m-%d %H:%M:%S"))  # type: ignore
        self.assertEqual(
            self.last_login, actual.last_login.strftime("%Y-%m-%d %H:%M:%S")  # type: ignore
        )


class GetByIdTests(UsersRepoTestsHelper):
    def test_get_by_id(self):
        actual = self.subject.get_by_id(self.user_id)
        self._assert_user(actual)

    def test_get_by_id_notfound_returns_none(self):
        self.assertIsNone(
            self.subject.get_by_id("7edc227d-818d-406e-826e-d3d9fd44aa70")
        )


class GetByEmailTests(UsersRepoTestsHelper):
    def test_get_by_email_success(self):
        actual = self.subject.get_by_email(self.email)
        self._assert_user(actual)

    def test_get_by_email_notfound_returns_none(self):
        self.assertIsNone(UsersDAO().get_by_email("wrong@test.email"))


class PostTests(UsersRepoTestsHelper):
    def test_post_user(self):
        expected_user = {
            "user_id": "edcc5c3d-db82-46a1-aaa6-6ea06d4443c5",
            "email": "test@user.mail",
            "psw_hash": "dasddasdasd",
            "first": "first",
            "last": "last",
        }

        self.subject.post(
            get_user(
                expected_user["user_id"],
                email=expected_user["email"],
                password_hash=expected_user["psw_hash"],
                first=expected_user["first"],
                last=expected_user["last"],
            )
        )

        actual = self._get_user_by_id(expected_user["user_id"])

        self._assert_user(expected_user, actual)

    def test_post_user_no_first_no_last(self):
        expected_user = {
            "user_id": "edcc5c3d-db82-46a1-aaa6-6ea06d4443c5",
            "email": "test@user.mail",
            "psw_hash": "dasddasdasd",
            "first": None,
            "last": None,
        }

        self.subject.post(
            get_user(
                expected_user["user_id"],
                email=expected_user["email"],
                password_hash=expected_user["psw_hash"],
            )
        )

        actual = self._get_user_by_id(expected_user["user_id"])

        self._assert_user(expected_user, actual)

    def test_post_user_with_not_unique_email_rises_exception(self):
        with self.assertRaises(UserAlreadyExistsException):
            self.subject.post(
                get_user(
                    "edcc5c3d-db82-46a1-aaa6-6ea06d4443c5",
                    "first",
                    "last",
                    self.email,
                )
            )

    def _assert_user(self, expected, actual):
        self.assertEqual(expected["email"], actual["email"])
        self.assertEqual(expected["psw_hash"], actual["password_hash"])
        self.assertEqual(expected["first"], actual["first"])
        self.assertEqual(expected["last"], actual["last"])

    def _get_user_by_id(self, user_id: str):
        sql = "SELECT * FROM users WHERE id=%(user_id)s"

        with psycopg2.connect(**self._get_test_db_dsn()) as con:  # type: ignore
            with con.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(sql, {"user_id": user_id})
                data = cur.fetchone()
        con.close()

        return data
