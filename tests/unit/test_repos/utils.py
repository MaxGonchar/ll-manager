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

    def _clean_dialogues(self):
        sql = "DELETE FROM dialogues"
        self._execute_sql(sql)

    def _clean_writings(self):
        sql = "DELETE FROM writings"
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

    def _seed_dialogues(self, dialogues):
        sql = f"""
            INSERT INTO dialogues (
                id,
                user_id,
                title,
                description,
                properties,
                settings,
                dialogues,
                expressions,
                added,
                updated
            ) VALUES (
                '{dialogues["id"]}',
                '{dialogues["user_id"]}',
                '{dialogues["title"]}',
                '{dialogues["description"]}',
                '{json.dumps(dialogues["properties"])}',
                '{json.dumps(dialogues["settings"])}',
                '{json.dumps(dialogues["dialogues"])}',
                '{json.dumps(dialogues["expressions"])}',
                '{dialogues["added"]}',
                '{dialogues["updated"]}'
            )
    """
        self._execute_sql(sql)

    def _seed_writings(self, writings):
        sql = f"""
            INSERT INTO writings (
                id,
                user_id,
                properties,
                writings,
                expressions,
                added,
                updated
            ) VALUES (
                '{writings["id"]}',
                '{writings["user_id"]}',
                '{json.dumps(writings["properties"])}',
                '{json.dumps(writings["writings"])}',
                '{json.dumps(writings["expressions"])}',
                '{writings["added"]}',
                '{writings["updated"]}'
            )
    """
        self._execute_sql(sql)

    def _seed_user(self, user: dict | None = None) -> str:
        base_id = "d5c26549-74f7-4930-9c2c-16d10d46e55e"
        base_user = {
            "id": base_id,
            "first": "First",
            "last": "Last",
            "email": "test@test.mail",
            "role": "self-educated",
            "password_hash": "c1a4b7e252281a7649d17a0f9f1d5180d5b5b1783dca84e121bbfcadda4ecc12",
            "properties": "{}",
            "added": "2023-04-16 09:10:25",
            "updated": "2023-04-16 09:10:25",
            "last_login": "2023-04-16 09:10:25",
        }
        user = user or base_user
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
                '{user["id"]}',
                '{user["first"]}',
                '{user["last"]}',
                '{user["email"]}',
                '{user["role"]}',
                '{user["password_hash"]}',
                '{user["properties"]}',
                '{user["added"]}',
                '{user["updated"]}',
                '{user["last_login"]}'
            )
        """
        self._execute_sql(sql)
        return user["id"] if user else base_id

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

    def _assert_dialogue(self, expected, actual):
        self.assertEqual(expected["id"], str(actual.id), "id")
        self.assertEqual(expected["title"], actual.title, "title")
        self.assertEqual(
            expected["description"], actual.description, "description"
        )
        self.assertEqual(
            expected["properties"], actual.properties, "properties"
        )
        self.assertEqual(expected["user_id"], str(actual.user_id), "user_id")
        self.assertEqual(expected["settings"], actual.settings, "settings")
        self.assertEqual(expected["dialogues"], actual.dialogues, "dialogues")
        self.assertEqual(
            expected["expressions"], actual.expressions, "expressions"
        )
        self.assertEqual(expected["added"], str(actual.added), "added")
        self.assertEqual(expected["updated"], str(actual.updated), "updated")

    def _assert_writing(self, expected, actual):
        self.assertEqual(expected["id"], str(actual.id), "id")
        self.assertEqual(expected["user_id"], str(actual.user_id), "user_id")
        self.assertEqual(
            expected["properties"], actual.properties, "properties"
        )
        self.assertEqual(expected["writings"], actual.writings, "writings")
        self.assertEqual(
            expected["expressions"], actual.expressions, "expressions"
        )
        self.assertEqual(expected["added"], str(actual.added), "added")
        self.assertEqual(expected["updated"], str(actual.updated), "updated")
