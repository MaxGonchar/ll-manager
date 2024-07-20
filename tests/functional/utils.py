from unittest import TestCase
from contextlib import contextmanager
import os
from typing import TypedDict

from flask import template_rendered
import psycopg2

from main import app


class TestSession(TypedDict):
    user_id: str
    user: str
    role: str


@contextmanager
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


class FunctionalTestsHelper(TestCase):
    def setUp(self):
        self.maxDiff = None

        self.host = "localhost"
        self.port = "5432"
        self.db_name = "test_ll_db"
        self.db_user = "test_ll_user"
        self.db_psw = "test_ll_user_password"

        self.app = app
        self.client = app.test_client()

        self._set_up_test_configs()

        self.test_session: TestSession = {
            "user_id": "2de2dc8b-ca69-4553-98dc-09e3f2998d12",
            "user": "test_user",
            "role": "test_role",
        }

    def _set_up_test_configs(self):
        self.app.config["WTF_CSRF_ENABLED"] = False

    def _set_session(self, **kwargs):
        with self.client.session_transaction() as test_session:
            for k, v in kwargs.items():
                test_session[k] = v

    def _get_test_db_dsn(self):
        return {
            "host": self.host,
            "port": self.port,
            "database": self.db_name,
            "user": self.db_user,
            "password": self.db_psw,
        }

    def _setup_test_db(self, sql):
        with psycopg2.connect(**self._get_test_db_dsn()) as con:  # type: ignore
            with con.cursor() as cur:
                cur.execute(sql)
        con.close()

    def _get_test_template_context(
        self, method, template_name, route, **kwargs
    ):
        method_mapping = {"GET": self.client.get, "POST": self.client.post}
        with captured_templates(self.app) as templates:
            response = method_mapping[method](route, **kwargs)

        self.assertEqual(200, response.status_code)
        template, context = templates[0]
        self.assertEqual(1, len(templates))
        self.assertEqual(template_name, template.name)

        return context
