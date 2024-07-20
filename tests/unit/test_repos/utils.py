from typing import List
from extensions import db
import json


import psycopg2
from flask import Flask


from unittest import TestCase


class BaseRepoTestUtils(TestCase):
    HOST = "localhost"
    PORT = "5432"
    DB = "test_ll_db"
    USER = "test_ll_user"
    PWD = "test_ll_user_password"

    APP = Flask("test")
    APP.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = f"postgresql://{USER}:{PWD}@{HOST}:{PORT}/{DB}"
    # APP.config['SQLALCHEMY_ECHO'] = True
    db.init_app(APP)

    def run(self, result=None):
        with self.APP.app_context():
            super().run(result)

    def _get_test_db_dsn(self):
        return {
            "host": self.HOST,
            "port": self.PORT,
            "database": self.DB,
            "user": self.USER,
            "password": self.PWD,
        }

    def _execute_sql(self, sql):
        with psycopg2.connect(**self._get_test_db_dsn()) as con:  # type: ignore
            with con.cursor() as cur:
                cur.execute(sql)

    def _clean_users(self):
        sql = "DELETE FROM users"
        self._execute_sql(sql)

    def _clean_expressions(self):
        sql = "DELETE FROM expressions"
        self._execute_sql(sql)

    def _clean_user_expressions(self):
        sql = "DELETE FROM user_expression"
        self._execute_sql(sql)

    def _clean_tags(self):
        sql = "DELETE FROM tags"
        self._execute_sql(sql)

    def _clean_tags_expressions(self):
        sql = "DELETE FROM tag_expression"
        self._execute_sql(sql)

    def _clean_expression_context(self):
        sql = "DELETE FROM expression_context"
        self._execute_sql(sql)

    def _seed_db_expression_records(self, exprs: List[dict]):
        sql = """
            INSERT INTO expressions (
                id,
                expression,
                definition,
                translations,
                example,
                added,
                updated,
                properties
            ) VALUES 
        """
        for expr in exprs:
            properties = expr.get("properties") or {}
            sql += f"""(
                '{expr['id']}',
                '{expr['expression']}',
                '{expr['definition']}',
                '{expr['translation']}',
                '{expr['example']}',
                '{expr['added']}',
                '{expr['updated']}',
                '{properties}'
            ),"""

        sql = sql[:-1] + ";"

        self._execute_sql(sql)

    def _seed_expression_context(self, context):
        sql = f"""
        INSERT INTO expression_context (
            id, expression_id, sentence, translation, template, added, updated
        ) VALUES (
            '{context["id"]}',
            '{context["expression_id"]}',
            '{context["sentence"]}',
            '{json.dumps(context["translation"])}',
            '{json.dumps(context["template"])}',
            '{context["added"]}',
            '{context["updated"]}'
        )
    """
        self._execute_sql(sql)

    def _assert_expression(self, expected_expression, actual_expression):
        self.assertEqual(expected_expression["id"], str(actual_expression.id))
        self.assertEqual(
            expected_expression["expression"], actual_expression.expression
        )
        self.assertEqual(
            expected_expression["definition"], actual_expression.definition
        )
        self.assertEqual(
            expected_expression["example"], actual_expression.example
        )
        self.assertEqual(
            expected_expression["translation"],
            json.dumps(actual_expression.translations, ensure_ascii=False),
        )
        self.assertEqual(
            expected_expression["added"],
            actual_expression.added.strftime("%Y-%m-%d %H:%M:%S"),
        )
        self.assertEqual(
            expected_expression["updated"],
            actual_expression.updated.strftime("%Y-%m-%d %H:%M:%S"),
        )

        if properties := expected_expression.get("properties"):
            self.assertEqual(
                json.loads(properties), actual_expression.properties
            )
