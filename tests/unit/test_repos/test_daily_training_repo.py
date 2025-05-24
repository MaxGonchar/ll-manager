from copy import deepcopy
from unittest import TestCase
from unittest.mock import Mock

from repository.training_expressions_repo import DailyTrainingRepo
from tests.unit.fixtures import (
    get_dt_data,
    get_expression,
    get_learn_list_item,
    get_user,
    get_user_expression,
)


class DailyTrainingRepoTestsHelper(TestCase):
    def setUp(self):
        self.user_id = "test_user_id"
        self.mock_daily_training_dao = Mock()
        self.mock_user_expressions_dao = Mock()
        self.mock_session = Mock()

        self.expr_id_1 = "4d7993aa-d897-4647-994b-e0625c88f349"
        self.expr_id_2 = "24d96f68-46e1-4fb3-b300-81cd89cea435"
        self.expr_id_3 = "d5c26549-74f7-4930-9c2c-16d10d46e55e"

        self.expression_1 = "test_expression_1"
        self.expression_2 = "test_expression_2"
        self.expression_3 = "test_expression_3"

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

    def test_get_list(self):
        self.mock_user_expressions_dao.return_value.get.return_value = [
            self.user_expr_1,
            self.user_expr_2,
            self.user_expr_3,
        ]

        actual = self.subject.get_list()

        self.assertEqual(3, len(actual))
        self.assertEqual(self.expr_id_1, actual[0].expression_id)
        self.assertEqual(self.expr_id_2, actual[1].expression_id)
        self.assertEqual(self.expr_id_3, actual[2].expression_id)

        self.mock_daily_training_dao.return_value.get.assert_called_once_with()
        self.mock_user_expressions_dao.return_value.get.assert_called_once_with(
            include=[self.expr_id_1, self.expr_id_2, self.expr_id_3]
        )

    def test_get_list_empty(self):
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

        actual = subject.get_list()

        self.assertEqual([], actual)

        self.mock_daily_training_dao.return_value.get.assert_called_once_with()
        self.mock_user_expressions_dao.return_value.get.assert_not_called()
