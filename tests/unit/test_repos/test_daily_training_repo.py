from copy import deepcopy
from datetime import datetime
from unittest import TestCase
from unittest.mock import Mock, MagicMock, ANY

from repository.training_expressions_repo import DailyTrainingRepo
from dao.daily_training_dao import DailyTrainingDAO
from dao.user_expressions_dao import UserExpressionsDAO
from tests.unit.fixtures import (
    get_dt_data,
    get_expression,
    get_learn_list_item,
    get_user,
    get_user_expression,
    get_daily_training_expressions_list_item,
)
from repository.exceptions import UserExpressionNotFoundException


class DailyTrainingRepoTestsHelper(TestCase):
    def setUp(self):
        self.user_id = "test_user_id"
        self.mock_daily_training_dao = Mock(spec=DailyTrainingDAO)
        self.mock_user_expressions_dao = Mock(spec=UserExpressionsDAO)
        self.mock_session = MagicMock()

        self.expr_id_1 = "4d7993aa-d897-4647-994b-e0625c88f349"
        self.expr_id_2 = "24d96f68-46e1-4fb3-b300-81cd89cea435"
        self.expr_id_3 = "d5c26549-74f7-4930-9c2c-16d10d46e55e"
        self.expr_id_4 = "4d7993aa-d897-4647-994b-e0625c88f350"

        self.expression_1 = "test_expression_1"
        self.expression_2 = "test_expression_2"
        self.expression_3 = "test_expression_3"
        self.expression_4 = "test_expression_4"

        self.mock_daily_training_data = {
            "learnListSize": 50,
            "practiceCountThreshold": 50,
            "knowledgeLevelThreshold": 0.9,
            "learning_list": [
                {
                    "expressionId": self.expr_id_1,
                    "position": 0,
                    "practiceCount": 0,
                    "knowledgeLevel": 0,
                    "lastPracticeTime": None,
                },
                {
                    "expressionId": self.expr_id_2,
                    "position": 0,
                    "practiceCount": 0,
                    "knowledgeLevel": 0,
                    "lastPracticeTime": None,
                },
                {
                    "expressionId": self.expr_id_3,
                    "position": 0,
                    "practiceCount": 0,
                    "knowledgeLevel": 0,
                    "lastPracticeTime": None,
                },
            ],
        }

        self.user = get_user(user_id=self.user_id)
        self.user_expr_1 = get_user_expression(
            user_id=self.user_id,
            user=self.user,
            expression=get_expression(
                expression_id=self.expr_id_1, expression=self.expression_1
            ),
        )
        self.user_expr_2 = get_user_expression(
            user_id=self.user_id,
            user=self.user,
            expression=get_expression(
                expression_id=self.expr_id_2, expression=self.expression_2
            ),
        )
        self.user_expr_3 = get_user_expression(
            user_id=self.user_id,
            user=self.user,
            expression=get_expression(
                expression_id=self.expr_id_3, expression=self.expression_3
            ),
        )
        self.user_expr_4 = get_user_expression(
            user_id=self.user_id,
            user=self.user,
            expression=get_expression(
                expression_id=self.expr_id_4,
                expression=self.expression_4,
            ),
        )

        self.mock_daily_training_dao.return_value.get.return_value = (
            self.mock_daily_training_data
        )

        self.subject = DailyTrainingRepo(
            user_id=self.user_id,
            session=self.mock_session,
            daily_training_dao=self.mock_daily_training_dao,
            user_expressions_dao=self.mock_user_expressions_dao,
        )


class GetNextTests(DailyTrainingRepoTestsHelper):
    def test_get_one(self):
        self.mock_user_expressions_dao.return_value.get.return_value = [
            self.user_expr_1,
        ]

        actual = self.subject.get_next(1)

        self.assertEqual(self.expr_id_1, actual[0].expression_id)

        self.mock_daily_training_dao.return_value.get.assert_called_once_with()
        self.mock_user_expressions_dao.return_value.get.assert_called_once_with(
            include=[self.expr_id_1]
        )

    def test_get_few(self):
        self.mock_user_expressions_dao.return_value.get.return_value = [
            self.user_expr_1,
            self.user_expr_2,
        ]

        actual = self.subject.get_next(2)

        self.assertEqual(2, len(actual))
        self.assertEqual(self.expr_id_1, actual[0].expression_id)
        self.assertEqual(self.expr_id_2, actual[1].expression_id)

        self.mock_daily_training_dao.return_value.get.assert_called_once_with()
        self.mock_user_expressions_dao.return_value.get.assert_called_once_with(
            include=[self.expr_id_1, self.expr_id_2]
        )

    def test_get_more_than_in_the_training_list(self):
        self.mock_user_expressions_dao.return_value.get.return_value = [
            self.user_expr_1,
            self.user_expr_2,
            self.user_expr_3,
        ]

        actual = self.subject.get_next(4)

        self.assertEqual(3, len(actual))
        self.assertEqual(self.expr_id_1, actual[0].expression_id)
        self.assertEqual(self.expr_id_2, actual[1].expression_id)
        self.assertEqual(self.expr_id_3, actual[2].expression_id)

        self.mock_daily_training_dao.return_value.get.assert_called_once_with()
        self.mock_user_expressions_dao.return_value.get.assert_called_once_with(
            include=[self.expr_id_1, self.expr_id_2, self.expr_id_3]
        )

    def test_get_from_empty_list(self):
        training_data = deepcopy(self.mock_daily_training_data)
        training_data["learning_list"] = []
        mock_daily_training_dao = Mock()
        mock_daily_training_dao.return_value.get.return_value = training_data
        self.mock_user_expressions_dao.return_value.get.return_value = []

        subject = DailyTrainingRepo(
            user_id=self.user_id,
            session=self.mock_session,
            daily_training_dao=mock_daily_training_dao,
            user_expressions_dao=self.mock_user_expressions_dao,
        )

        actual = subject.get_next(1)
        self.assertEqual([], actual)

        self.mock_daily_training_dao.return_value.get.assert_called_once_with()
        self.mock_user_expressions_dao.return_value.get.assert_not_called()


class GetListTests(DailyTrainingRepoTestsHelper):
    def setUp(self):
        super().setUp()
        self.mock_daily_training_data = {
            "learnListSize": 50,
            "practiceCountThreshold": 50,
            "knowledgeLevelThreshold": 0.9,
            "learning_list": [
                {
                    "expressionId": self.expr_id_1,
                    "position": 1,
                    "practiceCount": 0,
                    "knowledgeLevel": 0,
                    "lastPracticeTime": None,
                },
                {
                    "expressionId": self.expr_id_2,
                    "position": 2,
                    "practiceCount": 6,
                    "knowledgeLevel": 0.9,
                    "lastPracticeTime": "2023-10-01 12:00:00",
                },
                {
                    "expressionId": self.expr_id_3,
                    "position": 3,
                    "practiceCount": 5,
                    "knowledgeLevel": 0.5,
                    "lastPracticeTime": "2023-10-02 12:00:00",
                },
            ],
        }

        self.mock_daily_training_dao = Mock(spec=DailyTrainingDAO)

    def test_get_list(self):
        self.mock_daily_training_dao.return_value.get.return_value = (
            self.mock_daily_training_data
        )
        self.mock_user_expressions_dao.return_value.get.return_value = [
            self.user_expr_1,
            self.user_expr_2,
            self.user_expr_3,
        ]
        subject = DailyTrainingRepo(
            user_id=self.user_id,
            session=self.mock_session,
            daily_training_dao=self.mock_daily_training_dao,
            user_expressions_dao=self.mock_user_expressions_dao,
        )

        actual = subject.get_list()

        expected = [
            get_daily_training_expressions_list_item(
                expression_id=self.expr_id_1,
                expression=self.expression_1,
                knowledge_level=0,
                practice_count=0,
                last_practice_time=None,
            ),
            get_daily_training_expressions_list_item(
                expression_id=self.expr_id_2,
                expression=self.expression_2,
                knowledge_level=0.9,
                practice_count=6,
                last_practice_time=datetime(2023, 10, 1, 12, 0, 0),
            ),
            get_daily_training_expressions_list_item(
                expression_id=self.expr_id_3,
                expression=self.expression_3,
                knowledge_level=0.5,
                practice_count=5,
                last_practice_time=datetime(2023, 10, 2, 12, 0, 0),
            ),
        ]

        self.assertEqual(len(expected), len(actual))

        for exp, act in zip(expected, actual):
            self._assert_daily_training_expressions_list_item(exp, act)

        self.mock_daily_training_dao.return_value.get.assert_called_once_with()
        self.mock_user_expressions_dao.return_value.get.assert_called_once_with(
            include=[self.expr_id_1, self.expr_id_2, self.expr_id_3]
        )

    def test_get_list_empty(self):
        training_data = deepcopy(self.mock_daily_training_data)
        training_data["learning_list"] = []
        self.mock_daily_training_dao.return_value.get.return_value = (
            training_data
        )
        self.mock_user_expressions_dao.return_value.get.return_value = []

        subject = DailyTrainingRepo(
            user_id=self.user_id,
            session=self.mock_session,
            daily_training_dao=self.mock_daily_training_dao,
            user_expressions_dao=self.mock_user_expressions_dao,
        )

        actual = subject.get_list()

        self.assertEqual([], actual)

        self.mock_daily_training_dao.return_value.get.assert_called_once_with()
        self.mock_user_expressions_dao.return_value.get.assert_not_called()

    def _assert_daily_training_expressions_list_item(self, expected, actual):
        self.assertEqual(expected["expression_id"], actual["expression_id"])
        self.assertEqual(expected["expression"], actual["expression"])
        self.assertEqual(
            expected["knowledge_level"], actual["knowledge_level"]
        )
        self.assertEqual(expected["practice_count"], actual["practice_count"])
        self.assertEqual(
            expected["last_practice_time"], actual["last_practice_time"]
        )


class AddTests(DailyTrainingRepoTestsHelper):
    def test_add_success(self):
        self.mock_user_expressions_dao.return_value.get.return_value = [
            self.user_expr_4,
        ]

        self.subject.add(self.expr_id_4)

        self.mock_daily_training_dao.return_value.get.assert_called_once_with()
        self.mock_user_expressions_dao.return_value.get.assert_called_once_with(
            include=[self.expr_id_4]
        )
        expected_daily_training_data = {
            **self.mock_daily_training_data,
            "learning_list": [
                {
                    "expressionId": self.expr_id_4,
                    "position": 0,
                    "practiceCount": 0,
                    "knowledgeLevel": 0,
                    "lastPracticeTime": None,
                },
                *self.mock_daily_training_data["learning_list"],
            ],
        }
        self.mock_daily_training_dao.return_value.put.assert_called_once_with(
            expected_daily_training_data, commit=False
        )
        self.mock_session.commit.assert_called_once()

    def test_add_user_expression_not_found(self):
        self.mock_user_expressions_dao.return_value.get.return_value = []

        with self.assertRaises(UserExpressionNotFoundException) as exception:
            self.subject.add(self.expr_id_4)

        self.assertEqual(
            f"User expression with id {self.expr_id_4} not found for user {self.user_id}",
            str(exception.exception),
        )

        self.mock_daily_training_dao.return_value.get.assert_called_once_with()
        self.mock_user_expressions_dao.return_value.get.assert_called_once_with(
            include=[self.expr_id_4]
        )
        self.mock_daily_training_dao.return_value.put.assert_not_called()
        self.mock_session.commit.assert_not_called()
        self.mock_session.rollback.assert_called_once()

    def test_add_item_already_exists(self):
        self.mock_user_expressions_dao.return_value.get.return_value = [
            self.user_expr_1,
        ]

        self.subject.add(self.expr_id_1)

        self.mock_daily_training_dao.return_value.get.assert_called_once_with()
        self.mock_user_expressions_dao.return_value.get.assert_not_called()
        self.mock_daily_training_dao.return_value.put.assert_not_called()
        self.mock_session.commit.assert_not_called()


class DeleteTests(DailyTrainingRepoTestsHelper):
    def test_delete(self):
        self.mock_user_expressions_dao.return_value.get.return_value = [
            self.user_expr_4,
        ]

        self.subject.delete(self.expr_id_1)

        self.mock_daily_training_dao.return_value.get.assert_called_once_with()
        self.mock_user_expressions_dao.return_value.get.assert_called_once_with(
            exclude=[self.expr_id_2, self.expr_id_3], limit=48
        )
        expected_daily_training_data = {
            **self.mock_daily_training_data,
            "learning_list": [
                {
                    "expressionId": self.expr_id_4,
                    "position": 0,
                    "practiceCount": 0,
                    "knowledgeLevel": 0,
                    "lastPracticeTime": None,
                },
                *self.mock_daily_training_data["learning_list"][1:],
            ],
        }
        self.mock_daily_training_dao.return_value.put.assert_called_once_with(
            expected_daily_training_data, commit=True
        )


class UpdateExpressionsTests(DailyTrainingRepoTestsHelper):
    def setUp(self):
        super().setUp()
        self.mock_daily_training_data["learnListSize"] = 3
        self.mock_daily_training_data["learning_list"][0][
            "knowledgeLevel"
        ] = 0.5
        self.mock_daily_training_data["learning_list"][0]["practiceCount"] = 2
        self.mock_daily_training_data["learning_list"][1][
            "knowledgeLevel"
        ] = 0.8
        self.mock_daily_training_data["learning_list"][1]["practiceCount"] = 3

        self.user_expr_1.knowledge_level = 0.5
        self.user_expr_1.practice_count = 2
        self.user_expr_1.knowledge_level = 0.8
        self.user_expr_1.practice_count = 3

    def _mock_daily_training_dao(self, get_return_data):
        mock_daily_training_dao = Mock()
        mock_daily_training_dao.return_value.get.return_value = get_return_data
        return mock_daily_training_dao

    def _get_subject(self, mock_daily_training_dao):
        return DailyTrainingRepo(
            user_id=self.user_id,
            session=self.mock_session,
            daily_training_dao=mock_daily_training_dao,
            user_expressions_dao=self.mock_user_expressions_dao,
        )

    def test_update_expression(self):
        mock_daily_training_dao = self._mock_daily_training_dao(
            self.mock_daily_training_data
        )

        subject = self._get_subject(mock_daily_training_dao)

        subject.update_expressions(
            [
                {
                    "user_expression": self.user_expr_1,
                    "is_trained_successfully": True,
                },
                {
                    "user_expression": self.user_expr_2,
                    "is_trained_successfully": False,
                },
            ]
        )

        mock_daily_training_dao.return_value.get.assert_called_once_with()
        mock_daily_training_dao.return_value.put.assert_called_once_with(
            {
                "knowledgeLevelThreshold": 0.9,
                "learnListSize": 3,
                "practiceCountThreshold": 50,
                "learning_list": [
                    {
                        "expressionId": self.user_expr_2.expression_id,
                        "knowledgeLevel": 0.6000000000000001,
                        "position": 0,
                        "practiceCount": 4,
                        "lastPracticeTime": ANY,
                    },
                    {
                        "expressionId": self.user_expr_1.expression_id,
                        "knowledgeLevel": 0.6666666666666666,
                        "position": 1,
                        "practiceCount": 3,
                        "lastPracticeTime": ANY,
                    },
                    {
                        "expressionId": self.expr_id_3,
                        "knowledgeLevel": 0,
                        "position": 0,
                        "practiceCount": 0,
                        "lastPracticeTime": None,
                    },
                ],
            },
            commit=False,
        )
        self.mock_user_expressions_dao.return_value.bulk_update.assert_called_once_with(
            [
                self.user_expr_1,
                self.user_expr_2,
            ]
        )

    def test_update_expression_new_position_bigger_than_learn_list_len(self):
        self.mock_daily_training_data["learning_list"][0]["position"] = 3

        mock_daily_training_dao = self._mock_daily_training_dao(
            self.mock_daily_training_data
        )

        subject = self._get_subject(mock_daily_training_dao)

        subject.update_expressions(
            [
                {
                    "user_expression": self.user_expr_1,
                    "is_trained_successfully": True,
                },
                {
                    "user_expression": self.user_expr_2,
                    "is_trained_successfully": False,
                },
            ]
        )

        mock_daily_training_dao.return_value.get.assert_called_once_with()
        mock_daily_training_dao.return_value.put.assert_called_once_with(
            {
                "knowledgeLevelThreshold": 0.9,
                "learnListSize": 3,
                "practiceCountThreshold": 50,
                "learning_list": [
                    {
                        "expressionId": self.user_expr_2.expression_id,
                        "knowledgeLevel": 0.6000000000000001,
                        "position": 0,
                        "practiceCount": 4,
                        "lastPracticeTime": ANY,
                    },
                    {
                        "expressionId": self.expr_id_3,
                        "knowledgeLevel": 0,
                        "position": 0,
                        "practiceCount": 0,
                        "lastPracticeTime": None,
                    },
                    {
                        "expressionId": self.user_expr_1.expression_id,
                        "knowledgeLevel": 0.6666666666666666,
                        "position": 2,
                        "practiceCount": 3,
                        "lastPracticeTime": ANY,
                    },
                ],
            },
            commit=False,
        )
        self.mock_user_expressions_dao.return_value.bulk_update.assert_called_once_with(
            [
                self.user_expr_1,
                self.user_expr_2,
            ]
        )


class RefreshTests(DailyTrainingRepoTestsHelper):
    def setUp(self):
        super().setUp()
        self.mock_daily_training_data = {
            "learnListSize": 3,
            "practiceCountThreshold": 50,
            "knowledgeLevelThreshold": 0.9,
            "learning_list": [
                {
                    "expressionId": self.expr_id_1,
                    "position": 1,
                    "practiceCount": 51,
                    "knowledgeLevel": 0.91,
                    "lastPracticeTime": "2023-10-03 12:00:00",
                },
                {
                    "expressionId": self.expr_id_2,
                    "position": 2,
                    "practiceCount": 6,
                    "knowledgeLevel": 0.9,
                    "lastPracticeTime": "2023-10-01 12:00:00",
                },
                {
                    "expressionId": self.expr_id_3,
                    "position": 3,
                    "practiceCount": 5,
                    "knowledgeLevel": 0.5,
                    "lastPracticeTime": "2023-10-02 12:00:00",
                },
            ],
        }
        self.mock_daily_training_dao = Mock(spec=DailyTrainingDAO)

    def test_refresh_when_item_is_removed_due_to_reaching_training_criteria(
        self,
    ):
        self.mock_daily_training_dao.return_value.get.return_value = (
            self.mock_daily_training_data
        )
        self.mock_user_expressions_dao.return_value.get.return_value = [
            self.user_expr_4,
        ]
        subject = DailyTrainingRepo(
            user_id=self.user_id,
            session=self.mock_session,
            daily_training_dao=self.mock_daily_training_dao,
            user_expressions_dao=self.mock_user_expressions_dao,
        )

        subject.refresh()

        expected_daily_training_data = {
            "knowledgeLevelThreshold": 0.9,
            "learnListSize": 3,
            "practiceCountThreshold": 50,
            "learning_list": [
                {
                    "expressionId": self.expr_id_4,
                    "knowledgeLevel": 0,
                    "position": 0,
                    "practiceCount": 0,
                    "lastPracticeTime": None,
                },
                {
                    "expressionId": self.expr_id_2,
                    "knowledgeLevel": 0.9,
                    "position": 2,
                    "practiceCount": 6,
                    "lastPracticeTime": "2023-10-01 12:00:00",
                },
                {
                    "expressionId": self.expr_id_3,
                    "knowledgeLevel": 0.5,
                    "position": 3,
                    "practiceCount": 5,
                    "lastPracticeTime": "2023-10-02 12:00:00",
                },
            ],
        }

        self.mock_daily_training_dao.return_value.get.assert_called_once_with()
        self.mock_user_expressions_dao.return_value.get.assert_called_once_with(
            exclude=[self.expr_id_2, self.expr_id_3], limit=1
        )
        self.mock_daily_training_dao.return_value.put.assert_called_once_with(
            expected_daily_training_data, commit=True
        )

    def test_refresh_when_item_has_not_enough_practice_count_but_enough_knowledge_level(
        self,
    ):
        mock_daily_training_data = deepcopy(self.mock_daily_training_data)
        mock_daily_training_data["learning_list"][0]["practiceCount"] = 49
        self.mock_daily_training_dao.return_value.get.return_value = (
            mock_daily_training_data
        )
        subject = DailyTrainingRepo(
            user_id=self.user_id,
            session=self.mock_session,
            daily_training_dao=self.mock_daily_training_dao,
            user_expressions_dao=self.mock_user_expressions_dao,
        )
        subject.refresh()

        self.mock_daily_training_dao.return_value.get.assert_called_once_with()
        self.mock_user_expressions_dao.return_value.get.assert_not_called()
        self.mock_daily_training_dao.return_value.put.assert_called_once_with(
            mock_daily_training_data, commit=True
        )

    def test_refresh_when_item_has_not_enough_knowledge_level_but_enough_practice_count(
        self,
    ):
        mock_daily_training_data = deepcopy(self.mock_daily_training_data)
        mock_daily_training_data["learning_list"][0]["knowledgeLevel"] = 0.89
        self.mock_daily_training_dao.return_value.get.return_value = (
            mock_daily_training_data
        )
        subject = DailyTrainingRepo(
            user_id=self.user_id,
            session=self.mock_session,
            daily_training_dao=self.mock_daily_training_dao,
            user_expressions_dao=self.mock_user_expressions_dao,
        )
        subject.refresh()

        self.mock_daily_training_dao.return_value.get.assert_called_once_with()
        self.mock_user_expressions_dao.return_value.get.assert_not_called()
        self.mock_daily_training_dao.return_value.put.assert_called_once_with(
            mock_daily_training_data, commit=True
        )

    def test_refresh_when_nothing_to_add(self):
        self.mock_daily_training_dao.return_value.get.return_value = (
            self.mock_daily_training_data
        )
        self.mock_user_expressions_dao.return_value.get.return_value = []
        subject = DailyTrainingRepo(
            user_id=self.user_id,
            session=self.mock_session,
            daily_training_dao=self.mock_daily_training_dao,
            user_expressions_dao=self.mock_user_expressions_dao,
        )

        subject.refresh()

        expected_daily_training_data = {
            "knowledgeLevelThreshold": 0.9,
            "learnListSize": 3,
            "practiceCountThreshold": 50,
            "learning_list": [
                {
                    "expressionId": self.expr_id_2,
                    "knowledgeLevel": 0.9,
                    "position": 2,
                    "practiceCount": 6,
                    "lastPracticeTime": "2023-10-01 12:00:00",
                },
                {
                    "expressionId": self.expr_id_3,
                    "knowledgeLevel": 0.5,
                    "position": 3,
                    "practiceCount": 5,
                    "lastPracticeTime": "2023-10-02 12:00:00",
                },
            ],
        }

        self.mock_daily_training_dao.return_value.get.assert_called_once_with()
        self.mock_user_expressions_dao.return_value.get.assert_called_once_with(
            exclude=[self.expr_id_2, self.expr_id_3], limit=1
        )
        self.mock_daily_training_dao.return_value.put.assert_called_once_with(
            expected_daily_training_data, commit=True
        )

    def test_refresh_when_when_result_list_is_bigger_than_max_size(self):
        mock_daily_training_data = deepcopy(self.mock_daily_training_data)
        mock_daily_training_data["learnListSize"] = 1
        self.mock_daily_training_dao.return_value.get.return_value = (
            mock_daily_training_data
        )
        subject = DailyTrainingRepo(
            user_id=self.user_id,
            session=self.mock_session,
            daily_training_dao=self.mock_daily_training_dao,
            user_expressions_dao=self.mock_user_expressions_dao,
        )
        subject.refresh()

        expected_daily_training_data = {
            "knowledgeLevelThreshold": 0.9,
            "learnListSize": 1,
            "practiceCountThreshold": 50,
            "learning_list": [
                {
                    "expressionId": self.expr_id_2,
                    "knowledgeLevel": 0.9,
                    "position": 2,
                    "practiceCount": 6,
                    "lastPracticeTime": "2023-10-01 12:00:00",
                },
                {
                    "expressionId": self.expr_id_3,
                    "knowledgeLevel": 0.5,
                    "position": 3,
                    "practiceCount": 5,
                    "lastPracticeTime": "2023-10-02 12:00:00",
                },
            ],
        }

        self.mock_daily_training_dao.return_value.get.assert_called_once_with()
        self.mock_user_expressions_dao.return_value.get.assert_not_called()
        self.mock_daily_training_dao.return_value.put.assert_called_once_with(
            expected_daily_training_data, commit=True
        )


class GetByIDTests(DailyTrainingRepoTestsHelper):
    def test_get_by_id(self):
        self.mock_user_expressions_dao.return_value.get.return_value = [
            self.user_expr_1,
        ]

        actual = self.subject.get_by_id(self.expr_id_1)

        self.assertEqual(self.expr_id_1, actual.expression_id)

        self.mock_daily_training_dao.return_value.get.assert_called_once_with()
        self.mock_user_expressions_dao.return_value.get.assert_called_once_with(
            include=[self.expr_id_1]
        )

    def test_get_by_id_not_found_returns_none(self):
        self.mock_user_expressions_dao.return_value.get.return_value = []

        actual = self.subject.get_by_id(self.expr_id_1)

        self.assertIsNone(actual)

        self.mock_daily_training_dao.return_value.get.assert_called_once_with()
        self.mock_user_expressions_dao.return_value.get.assert_called_once_with(
            include=[self.expr_id_1]
        )


class UpdateSettingsTests(DailyTrainingRepoTestsHelper):
    def test_update_settings(self):
        settings = {
            "max_learn_list_size": 3,
            "knowledge_level_threshold": 0.8,
            "practice_count_threshold": 10,
        }
        self.subject.update_settings(settings)

        expected_daily_training_data = {
            **self.mock_daily_training_data,
            "learnListSize": 3,
            "knowledgeLevelThreshold": 0.8,
            "practiceCountThreshold": 10,
        }

        self.mock_daily_training_dao.return_value.put.assert_called_once_with(
            expected_daily_training_data, commit=True
        )


class CountLearnListItemsTests(DailyTrainingRepoTestsHelper):
    def test_count_learn_list_items(self):
        actual = self.subject.count_learn_list_items()
        expected = len(self.mock_daily_training_data["learning_list"])
        self.assertEqual(expected, actual)
        self.mock_daily_training_dao.return_value.get.assert_called_once_with()


class IsExpressionInLearnListTests(DailyTrainingRepoTestsHelper):
    def test_found_in_learn_list(self):
        actual = self.subject.is_expression_in_learn_list(self.expr_id_1)
        self.assertTrue(actual)

        self.mock_daily_training_dao.return_value.get.assert_called_once_with()

    def test_not_found_in_learn_list(self):
        actual = self.subject.is_expression_in_learn_list(self.expr_id_4)
        self.assertFalse(actual)

        self.mock_daily_training_dao.return_value.get.assert_called_once_with()
