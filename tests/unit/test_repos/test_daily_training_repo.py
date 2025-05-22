from dao.daily_training_dao import DailyTrainingRepoDAO
from repository.exceptions import UserNotFoundException
from tests.unit.test_repos.utils import BaseRepoTestUtils

import psycopg2

import json


class DailyTrainingRepoInitTests(BaseRepoTestUtils):
    def setUp(self) -> None:
        self._clean_users()

    def test_init_user_not_found_rise_exception(self):
        with self.assertRaises(UserNotFoundException):
            DailyTrainingRepoDAO("b5f55871-4a7d-4c27-aaa5-e3542d8554a7")


class GetTests(BaseRepoTestUtils):
    def setUp(self):
        self._clean_users()

        self.user_id = "04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef"
        self.user_properties = {
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
                            "knowledgeLevel": 0,
                        },
                        {
                            "expressionId": "24d96f68-46e1-4fb3-b300-81cd89cea435",
                            "position": 0,
                            "practiceCount": 0,
                            "knowledgeLevel": 0,
                        },
                        {
                            "expressionId": "d5c26549-74f7-4930-9c2c-16d10d46e55e",
                            "position": 0,
                            "practiceCount": 0,
                            "knowledgeLevel": 0,
                        },
                    ],
                }
            },
        }

        self._seed_db_user_record()
        self.subject = DailyTrainingRepoDAO(self.user_id)

    def test_get(self):
        actual = self.subject.get()

        self.assertEqual(
            self.user_properties["challenges"]["dailyTraining"], actual
        )

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
                'First',
                'Last',
                'daily_training@test.mail',
                'self-educated',
                'c1a4b7e252281a7649d17a0f9f1d5180d5b5b1783dca84e121bbfcadda4ecc12',
                '{json.dumps(self.user_properties)}',
                '2023-04-16 09:10:25',
                '2023-04-16 09:10:25',
                '2023-04-16 09:10:25'
            )
        """
        self._execute_sql(sql)


class PutTests(BaseRepoTestUtils):
    def setUp(self):
        self._clean_users()

        self.user_id = "04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef"
        self.properties = {
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

        self._seed_db_user_record()
        self.subject = DailyTrainingRepoDAO(self.user_id)

    def test_post(self):
        new_props = {
            "nativeLang": "uk",
            "challenges": {
                "dailyTraining": {
                    "learnListSize": 60,
                    "practiceCountThreshold": 50,
                    "knowledgeLevelThreshold": 0.95,
                    "learning_list": [
                        {
                            "expressionId": "ee8e74ca-8f1a-4e5b-9a86-54d6c35f4fcd",
                            "position": 0,
                            "practiceCount": 0,
                            "knowledgeLevel": 0,
                        },
                        {
                            "expressionId": "4d7993aa-d897-4647-994b-e0625c88f349",
                            "position": 0,
                            "practiceCount": 0,
                            "knowledgeLevel": 0,
                        },
                        {
                            "expressionId": "24d96f68-46e1-4fb3-b300-81cd89cea435",
                            "position": 2,
                            "practiceCount": 2,
                            "knowledgeLevel": 0.5,
                        },
                    ],
                }
            },
        }
        self.subject.put(new_props["challenges"]["dailyTraining"])

        updated_properties = self._get_db_user_properties()

        self.assertEqual(new_props, updated_properties)

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
                'First',
                'Last',
                'daily_training@test.mail',
                'self-educated',
                'c1a4b7e252281a7649d17a0f9f1d5180d5b5b1783dca84e121bbfcadda4ecc12',
                '{json.dumps(self.properties)}',
                '2023-04-16 09:10:25',
                '2023-04-16 09:10:25',
                '2023-04-16 09:10:25'
            )
        """
        self._execute_sql(sql)

    def _get_db_user_properties(self):
        sql = """
            SELECT properties
            FROM users
            WHERE id=%(user_id)s
        """
        with psycopg2.connect(**self._get_test_db_dsn()) as con:  # type: ignore
            with con.cursor() as cur:
                cur.execute(sql, {"user_id": self.user_id})
                data = cur.fetchone()
        con.close()

        return data[0]
