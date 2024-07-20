from tests.functional.utils import FunctionalTestsHelper

import psycopg2

from flask import session


class SignOnTest(FunctionalTestsHelper):
    def test_sign_on_get(self):
        self._get_test_template_context(
            "GET", "login/sign_on.html", "/login/sign-on"
        )

    def test_sign_on_succeed(self):
        email = "test_new@email.com"
        payload = {
            "first": "test",
            "last": "test",
            "email": email,
            "password": "qwe123",
            "password_repeat": "qwe123",
        }

        with self.client:
            context = self._get_test_template_context(
                "POST",
                "user/index.html",
                "/login/sign-on",
                data=payload,
                follow_redirects=True,
            )

            self.assertEqual(email, session["user"])
            self.assertIn("user_id", session)

            user_id = session["user_id"]

        user = self._get_user(user_id)

        expected_properties = {
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

        self.assertEqual(expected_properties, user[6])

    def test_sign_on_failed_password_repeat_not_match(self):
        email = "test_new@email.com"
        payload = {
            "first": "test",
            "last": "test",
            "email": email,
            "password": "qwe123",
            "password_repeat": "123",
        }

        with self.client:
            self._get_test_template_context(
                "POST",
                "login/sign_on.html",
                "/login/sign-on",
                data=payload,
                follow_redirects=True,
            )

            self.assertEqual(0, len(session))

    def test_sign_on_failed_when_user_email_not_unique(self):
        payload = {
            "first": "test",
            "last": "test",
            "email": "test@test.com",
            "password": "qwe123",
            "password_repeat": "qwe123",
        }

        with self.client:
            self._get_test_template_context(
                "POST",
                "login/sign_on.html",
                "/login/sign-on",
                data=payload,
                follow_redirects=True,
            )

            self.assertEqual(0, len(session))

    def _get_user(self, user_id):
        sql = """
            SELECT * FROM users WHERE id=%(user_id)s
        """
        with psycopg2.connect(**self._get_test_db_dsn()) as con:  # type: ignore
            with con.cursor() as cur:
                cur.execute(sql, {"user_id": user_id})
                data = cur.fetchone()

        return data  # type: ignore


class LogInTest(FunctionalTestsHelper):
    def setUp(self):
        super().setUp()
        with open("tests/functional/data/setup_test_sign_on.sql", "r") as file:
            sql = file.read()
        self._setup_test_db(sql)

    def test_log_in_get(self):
        self._get_test_template_context("GET", "login/login.html", "/login")

    def test_log_in_success(self):
        email = "test@test.com"
        user_id = "4d7993aa-d897-4647-994b-e0625c88f349"
        payload = {
            "email": email,
            "password": "qwe123!@#",
        }

        with self.client:
            self._get_test_template_context(
                "POST",
                "user/index.html",
                "/login",
                data=payload,
                follow_redirects=True,
            )

            self.assertEqual(user_id, session["user_id"])
            self.assertEqual(email, session["user"])

    def test_log_in_wrong_psw(self):
        email = "test_new@email.com"
        payload = {
            "email": email,
            "password": "wrong_psw",
        }

        with self.client:
            self._get_test_template_context(
                "POST",
                "login/login.html",
                "/login",
                data=payload,
                follow_redirects=True,
            )

            self.assertEqual(0, len(session))

    def test_log_in_wrong_email(self):
        email = "wrong@email.com"
        payload = {
            "email": email,
            "password": "qwe123!@#",
        }

        with self.client:
            self._get_test_template_context(
                "POST",
                "login/login.html",
                "/login",
                data=payload,
                follow_redirects=True,
            )

            self.assertEqual(0, len(session))


class LogOutTest(FunctionalTestsHelper):
    def setUp(self):
        super().setUp()
        self._set_session(**self.test_session)

    def test_logout(self):
        with self.client:
            self._get_test_template_context(
                "GET",
                "login/login.html",
                "/login/logout",
                follow_redirects=True,
            )
            self.assertEqual(0, len(session))
