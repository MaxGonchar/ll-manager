from datetime import datetime
from unittest import TestCase
from unittest.mock import patch
from exercises.daily_training_v2 import (
    DailyTraining,
    ExpressionNotFoundException,
    LearnListItemNotFoundExpression,
)
from tests.unit.fixtures import (
    get_dt_data,
    get_expression,
    get_learn_list_item,
    get_user,
    get_user_expression,
)


class GetChallengeTests(TestCase):
    def setUp(self):
        self.user_id = "d32cd1e8-7111-4e0a-84aa-c5664df8a063"

        dt_repo_patcher = patch(
            "exercises.daily_training_v2.DailyTrainingRepo"
        )
        mock_dt_repo = dt_repo_patcher.start()
        self.mock_dt_repo_get = mock_dt_repo.return_value.get
        self.addCleanup(dt_repo_patcher.stop)

        us_expr_patcher = patch(
            "exercises.daily_training_v2.UserExpressionsRepo"
        )
        mock_us_expr_repo = us_expr_patcher.start()
        self.mock_get_user_expr_by_id = (
            mock_us_expr_repo.return_value.get_by_id
        )
        self.addCleanup(us_expr_patcher.stop)

    def test_get_challenge_when_empty_llist_returns_None(
        self,
    ):
        self.mock_dt_repo_get.return_value = get_dt_data([])
        subject = DailyTraining(self.user_id)

        self.assertIsNone(subject.get_challenge())

        self.mock_dt_repo_get.assert_called_once_with()
        self.mock_get_user_expr_by_id.assert_not_called()

    def test_get_challenge_when_expression_not_found_raise_ExpressionNotFoundException(
        self,
    ):
        self.mock_dt_repo_get.return_value = get_dt_data(
            [get_learn_list_item()]
        )
        self.mock_get_user_expr_by_id.return_value = None

        subject = DailyTraining(self.user_id)

        with self.assertRaises(ExpressionNotFoundException):
            subject.get_challenge()

        self.mock_dt_repo_get.assert_called_once_with()
        self.mock_get_user_expr_by_id.assert_called_once_with("test_expr_id")

    def test_get_challenge_success(self):
        expr = "test expression"
        expr_id = "test_expr_id"
        definition = "definition of test expression"

        self.mock_dt_repo_get.return_value = get_dt_data(
            [get_learn_list_item()]
        )
        self.mock_get_user_expr_by_id.return_value = get_user_expression(
            user_id=self.user_id,
            user=get_user(self.user_id),
            expression=get_expression(
                expression_id=expr_id, expression=expr, definition=definition
            ),
        )

        subject = DailyTraining(self.user_id)

        expected = {
            "answer": expr,
            "expression_id": expr_id,
            "question": definition,
            "tip": expr,
        }

        actual = subject.get_challenge()

        self.assertEqual(expected, actual)

        self.mock_dt_repo_get.assert_called_once_with()
        self.mock_get_user_expr_by_id.assert_called_once_with("test_expr_id")


class SubmitChallengeTests(TestCase):
    def setUp(self):
        self.user_id = "test_user_id"
        self.mock_time = "2023-05-19 09:34:15"

        dt_repo_patcher = patch(
            "exercises.daily_training_v2.DailyTrainingRepo"
        )
        mock_dt_repo = dt_repo_patcher.start()
        self.mock_dt_repo_get = mock_dt_repo.return_value.get
        self.mock_dt_repo_put = mock_dt_repo.return_value.put
        self.addCleanup(dt_repo_patcher.stop)

        us_expr_patcher = patch(
            "exercises.daily_training_v2.UserExpressionsRepo"
        )
        mock_us_expr_repo = us_expr_patcher.start()
        self.mock_get_user_expr_by_id = (
            mock_us_expr_repo.return_value.get_by_id
        )
        self.mock_get_user_exprs = mock_us_expr_repo.return_value.get
        self.mock_put_user_expr = mock_us_expr_repo.return_value.put
        self.addCleanup(us_expr_patcher.stop)

        get_current_time_patcher = patch(
            "exercises.daily_training_v2.get_current_utc_time",
            return_value=self.mock_time,
        )
        get_current_time_patcher.start()
        self.addCleanup(get_current_time_patcher.stop)

    def test_submit_challenge_correct(self):
        self.mock_dt_repo_get.return_value = get_dt_data(
            [
                get_learn_list_item(
                    item_id="test_expr_id_1",
                    position=1,
                    pract_count=1,
                    know_level=0,
                ),
                get_learn_list_item(
                    item_id="test_expr_id_2",
                    position=2,
                    pract_count=2,
                    know_level=0.5,
                ),
                get_learn_list_item(
                    item_id="test_expr_id_3",
                    position=3,
                    pract_count=3,
                    know_level=0.7,
                ),
            ],
            lls=3,
        )

        mock_user = get_user(self.user_id)
        mock_expr = get_expression(
            expression_id="test_expr_id_1",
            expression="test expression 1",
        )
        self.mock_get_user_expr_by_id.return_value = get_user_expression(
            user_id=self.user_id,
            user=mock_user,
            expression=mock_expr,
            kl=0,
            pc=1,
        )

        subject = DailyTraining(self.user_id)

        actual = subject.submit_challenge(
            "test_expr_id_1", "test expression 1"
        )

        expected = {
            "correctAnswer": "test expression 1",
            "usersAnswer": "test expression 1",
            "definition": "test definition",
            "translation": "тестовий вираз",
            "example": "example of usage of test expression",
        }

        self.assertEqual(expected, actual)

        self.mock_dt_repo_get.assert_called_once_with()
        self.mock_get_user_expr_by_id.assert_called_once_with("test_expr_id_1")
        self.mock_get_user_exprs.assert_not_called()
        self.mock_dt_repo_put.assert_called_once_with(
            {
                "knowledgeLevelThreshold": 0.9,
                "learnListSize": 3,
                "practiceCountThreshold": 90,
                "learning_list": [
                    {
                        "expressionId": "test_expr_id_2",
                        "knowledgeLevel": 0.5,
                        "position": 2,
                        "practiceCount": 2,
                        "lastPracticeTime": None,
                    },
                    {
                        "expressionId": "test_expr_id_3",
                        "knowledgeLevel": 0.7,
                        "position": 3,
                        "practiceCount": 3,
                        "lastPracticeTime": None,
                    },
                    {
                        "expressionId": "test_expr_id_1",
                        "knowledgeLevel": 0.5,
                        "position": 2,
                        "practiceCount": 2,
                        "lastPracticeTime": self.mock_time,
                    },
                ],
            }
        )

        put_u_expr = self.mock_put_user_expr.call_args.args[0]

        self.assertEqual(mock_expr, put_u_expr.expression)
        self.assertEqual(0.5, put_u_expr.knowledge_level)
        self.assertEqual(2, put_u_expr.practice_count)
        self.assertEqual(self.mock_time, put_u_expr.last_practice_time)

    def test_submit_challenge_incorrect(self):
        self.mock_dt_repo_get.return_value = get_dt_data(
            [
                get_learn_list_item(
                    item_id="test_expr_id_1",
                    position=1,
                    pract_count=1,
                    know_level=1,
                ),
                get_learn_list_item(
                    item_id="test_expr_id_2",
                    position=2,
                    pract_count=2,
                    know_level=0.5,
                ),
                get_learn_list_item(
                    item_id="test_expr_id_3",
                    position=3,
                    pract_count=3,
                    know_level=0.7,
                ),
            ],
            lls=3,
        )

        mock_user = get_user(self.user_id)
        mock_expr = get_expression(
            expression_id="test_expr_id_1",
            expression="test expression 1",
        )
        self.mock_get_user_expr_by_id.return_value = get_user_expression(
            user_id=self.user_id,
            user=mock_user,
            expression=mock_expr,
            kl=1,
            pc=1,
        )

        subject = DailyTraining(self.user_id)

        actual = subject.submit_challenge("test_expr_id_1", "wrong answer")
        expected = {
            "correctAnswer": "test expression 1",
            "usersAnswer": "wrong answer",
            "definition": "test definition",
            "translation": "тестовий вираз",
            "example": "example of usage of test expression",
        }

        self.assertEqual(expected, actual)

        self.mock_dt_repo_get.assert_called_once_with()
        self.mock_get_user_expr_by_id.assert_called_once_with("test_expr_id_1")
        self.mock_get_user_exprs.assert_not_called()
        self.mock_dt_repo_put.assert_called_once_with(
            {
                "knowledgeLevelThreshold": 0.9,
                "learnListSize": 3,
                "practiceCountThreshold": 90,
                "learning_list": [
                    {
                        "expressionId": "test_expr_id_1",
                        "knowledgeLevel": 0.5,
                        "position": 0,
                        "practiceCount": 2,
                        "lastPracticeTime": self.mock_time,
                    },
                    {
                        "expressionId": "test_expr_id_2",
                        "knowledgeLevel": 0.5,
                        "position": 2,
                        "practiceCount": 2,
                        "lastPracticeTime": None,
                    },
                    {
                        "expressionId": "test_expr_id_3",
                        "knowledgeLevel": 0.7,
                        "position": 3,
                        "practiceCount": 3,
                        "lastPracticeTime": None,
                    },
                ],
            }
        )

        put_u_expr = self.mock_put_user_expr.call_args.args[0]

        self.assertEqual(mock_expr, put_u_expr.expression)
        self.assertEqual(0.5, put_u_expr.knowledge_level)
        self.assertEqual(2, put_u_expr.practice_count)
        self.assertEqual(self.mock_time, put_u_expr.last_practice_time)

    def test_submit_challenge_with_hint(self):
        self.mock_dt_repo_get.return_value = get_dt_data(
            [
                get_learn_list_item(
                    item_id="test_expr_id_1",
                    position=1,
                    pract_count=1,
                    know_level=1,
                ),
            ],
            lls=3,
        )

        mock_user = get_user(self.user_id)
        mock_expr = get_expression(
            expression_id="test_expr_id_1",
            expression="test expression 1",
        )
        self.mock_get_user_expr_by_id.return_value = get_user_expression(
            user_id=self.user_id,
            user=mock_user,
            expression=mock_expr,
            kl=1,
            pc=1,
        )

        subject = DailyTraining(self.user_id)

        actual = subject.submit_challenge(
            "test_expr_id_1", "wrong answer", hint=True
        )
        expected = {
            "correctAnswer": "test expression 1",
            "usersAnswer": "wrong answer",
            "definition": "test definition",
            "translation": "тестовий вираз",
            "example": "example of usage of test expression",
        }

        self.assertEqual(expected, actual)

        self.mock_dt_repo_get.assert_called_once_with()
        self.mock_get_user_expr_by_id.assert_called_once_with("test_expr_id_1")
        self.mock_get_user_exprs.assert_not_called()
        self.mock_dt_repo_put.assert_not_called()
        self.mock_put_user_expr.assert_not_called()

    def test_submit_challenge_new_position_bigger_than_learn_list_len(self):
        self.mock_dt_repo_get.return_value = get_dt_data(
            [
                get_learn_list_item(
                    item_id="test_expr_id_1",
                    position=4,
                    pract_count=1,
                    know_level=0,
                ),
                get_learn_list_item(
                    item_id="test_expr_id_2",
                    position=2,
                    pract_count=2,
                    know_level=0.5,
                ),
                get_learn_list_item(
                    item_id="test_expr_id_3",
                    position=3,
                    pract_count=3,
                    know_level=0.7,
                ),
            ],
            lls=3,
        )

        mock_user = get_user(self.user_id)
        mock_expr = get_expression(
            expression_id="test_expr_id_1",
            expression="test expression 1",
        )
        self.mock_get_user_expr_by_id.return_value = get_user_expression(
            user_id=self.user_id,
            user=mock_user,
            expression=mock_expr,
            kl=0,
            pc=1,
        )

        subject = DailyTraining(self.user_id)

        actual = subject.submit_challenge(
            "test_expr_id_1", "test expression 1"
        )
        expected = {
            "correctAnswer": "test expression 1",
            "usersAnswer": "test expression 1",
            "definition": "test definition",
            "translation": "тестовий вираз",
            "example": "example of usage of test expression",
        }

        self.assertEqual(expected, actual)

        self.mock_dt_repo_get.assert_called_once_with()
        self.mock_get_user_expr_by_id.assert_called_once_with("test_expr_id_1")
        self.mock_get_user_exprs.assert_not_called()
        self.mock_dt_repo_put.assert_called_once_with(
            {
                "knowledgeLevelThreshold": 0.9,
                "learnListSize": 3,
                "practiceCountThreshold": 90,
                "learning_list": [
                    {
                        "expressionId": "test_expr_id_2",
                        "knowledgeLevel": 0.5,
                        "position": 2,
                        "practiceCount": 2,
                        "lastPracticeTime": None,
                    },
                    {
                        "expressionId": "test_expr_id_3",
                        "knowledgeLevel": 0.7,
                        "position": 3,
                        "practiceCount": 3,
                        "lastPracticeTime": None,
                    },
                    {
                        "expressionId": "test_expr_id_1",
                        "knowledgeLevel": 0.5,
                        "position": 2,
                        "practiceCount": 2,
                        "lastPracticeTime": self.mock_time,
                    },
                ],
            }
        )

        put_u_expr = self.mock_put_user_expr.call_args.args[0]

        self.assertEqual(mock_expr, put_u_expr.expression)
        self.assertEqual(0.5, put_u_expr.knowledge_level)
        self.assertEqual(2, put_u_expr.practice_count)
        self.assertEqual(self.mock_time, put_u_expr.last_practice_time)

    def test_submit_challenge_new_position_lower_0(self):
        self.mock_dt_repo_get.return_value = get_dt_data(
            [
                get_learn_list_item(
                    item_id="test_expr_id_1",
                    position=0,
                    pract_count=1,
                    know_level=0,
                ),
                get_learn_list_item(
                    item_id="test_expr_id_2",
                    position=2,
                    pract_count=2,
                    know_level=0.5,
                ),
                get_learn_list_item(
                    item_id="test_expr_id_3",
                    position=3,
                    pract_count=3,
                    know_level=0.7,
                ),
            ],
            lls=3,
        )

        mock_user = get_user(self.user_id)
        mock_expr = get_expression(
            expression_id="test_expr_id_1",
            expression="test expression 1",
        )
        self.mock_get_user_expr_by_id.return_value = get_user_expression(
            user_id=self.user_id,
            user=mock_user,
            expression=mock_expr,
            kl=0,
            pc=1,
        )

        subject = DailyTraining(self.user_id)

        actual = subject.submit_challenge("test_expr_id_1", "wrong")
        expected = {
            "correctAnswer": "test expression 1",
            "usersAnswer": "wrong",
            "definition": "test definition",
            "translation": "тестовий вираз",
            "example": "example of usage of test expression",
        }

        self.assertEqual(expected, actual)

        self.mock_dt_repo_get.assert_called_once_with()
        self.mock_get_user_expr_by_id.assert_called_once_with("test_expr_id_1")
        self.mock_get_user_exprs.assert_not_called()
        self.mock_dt_repo_put.assert_called_once_with(
            {
                "knowledgeLevelThreshold": 0.9,
                "learnListSize": 3,
                "practiceCountThreshold": 90,
                "learning_list": [
                    {
                        "expressionId": "test_expr_id_1",
                        "knowledgeLevel": 0,
                        "position": 0,
                        "practiceCount": 2,
                        "lastPracticeTime": self.mock_time,
                    },
                    {
                        "expressionId": "test_expr_id_2",
                        "knowledgeLevel": 0.5,
                        "position": 2,
                        "practiceCount": 2,
                        "lastPracticeTime": None,
                    },
                    {
                        "expressionId": "test_expr_id_3",
                        "knowledgeLevel": 0.7,
                        "position": 3,
                        "practiceCount": 3,
                        "lastPracticeTime": None,
                    },
                ],
            }
        )

        put_u_expr = self.mock_put_user_expr.call_args.args[0]

        self.assertEqual(mock_expr, put_u_expr.expression)
        self.assertEqual(0, put_u_expr.knowledge_level)
        self.assertEqual(2, put_u_expr.practice_count)
        self.assertEqual(self.mock_time, put_u_expr.last_practice_time)

    def test_submit_challenge_with_removing_from_learn_list_and_adding_new_one(
        self,
    ):
        self.mock_dt_repo_get.return_value = get_dt_data(
            [
                get_learn_list_item(
                    item_id="test_expr_id_1",
                    position=1,
                    pract_count=89,
                    know_level=0.9,
                ),
                get_learn_list_item(
                    item_id="test_expr_id_2",
                    position=2,
                    pract_count=2,
                    know_level=0.5,
                ),
                get_learn_list_item(
                    item_id="test_expr_id_3",
                    position=3,
                    pract_count=3,
                    know_level=0.7,
                ),
            ],
            lls=3,
        )

        mock_user = get_user(self.user_id)
        mock_expr = get_expression(
            expression_id="test_expr_id_1",
            expression="test expression 1",
        )
        self.mock_get_user_expr_by_id.return_value = get_user_expression(
            user_id=self.user_id,
            user=mock_user,
            expression=mock_expr,
            kl=0,
            pc=1,
        )
        self.mock_get_user_exprs.return_value = [
            get_user_expression(
                user_id=self.user_id,
                user=mock_user,
                expression=get_expression(
                    expression_id="test_expr_id_4",
                    expression="test expression 4",
                ),
            )
        ]

        subject = DailyTraining(self.user_id)

        actual = subject.submit_challenge(
            "test_expr_id_1", "test expression 1"
        )
        expected = {
            "correctAnswer": "test expression 1",
            "usersAnswer": "test expression 1",
            "definition": "test definition",
            "translation": "тестовий вираз",
            "example": "example of usage of test expression",
        }

        self.assertEqual(expected, actual)

        self.mock_dt_repo_get.assert_called_once_with()
        self.mock_get_user_expr_by_id.assert_called_once_with("test_expr_id_1")
        self.mock_get_user_exprs.assert_called_once_with(
            exclude=["test_expr_id_2", "test_expr_id_3"], limit=1
        )
        self.mock_dt_repo_put.assert_called_once_with(
            {
                "knowledgeLevelThreshold": 0.9,
                "learnListSize": 3,
                "practiceCountThreshold": 90,
                "learning_list": [
                    {
                        "expressionId": "test_expr_id_4",
                        "knowledgeLevel": 0,
                        "position": 0,
                        "practiceCount": 0,
                        "lastPracticeTime": None,
                    },
                    {
                        "expressionId": "test_expr_id_2",
                        "knowledgeLevel": 0.5,
                        "position": 2,
                        "practiceCount": 2,
                        "lastPracticeTime": None,
                    },
                    {
                        "expressionId": "test_expr_id_3",
                        "knowledgeLevel": 0.7,
                        "position": 3,
                        "practiceCount": 3,
                        "lastPracticeTime": None,
                    },
                ],
            }
        )

        put_u_expr = self.mock_put_user_expr.call_args.args[0]

        self.assertEqual(mock_expr, put_u_expr.expression)
        self.assertEqual(0.5, put_u_expr.knowledge_level)
        self.assertEqual(2, put_u_expr.practice_count)
        self.assertEqual(self.mock_time, put_u_expr.last_practice_time)

    def test_submit_challenge_knowledge_level_not_enough(self):
        self.mock_dt_repo_get.return_value = get_dt_data(
            [
                get_learn_list_item(
                    item_id="test_expr_id_1",
                    position=2,
                    pract_count=100,
                    know_level=0.8,
                ),
                get_learn_list_item(
                    item_id="test_expr_id_2",
                    position=2,
                    pract_count=2,
                    know_level=0.5,
                ),
                get_learn_list_item(
                    item_id="test_expr_id_3",
                    position=3,
                    pract_count=3,
                    know_level=0.7,
                ),
            ],
            lls=3,
        )

        mock_user = get_user(self.user_id)
        mock_expr = get_expression(
            expression_id="test_expr_id_1",
            expression="test expression 1",
        )
        self.mock_get_user_expr_by_id.return_value = get_user_expression(
            user_id=self.user_id,
            user=mock_user,
            expression=mock_expr,
            kl=0,
            pc=1,
        )

        subject = DailyTraining(self.user_id)

        actual = subject.submit_challenge(
            "test_expr_id_1", "test expression 1"
        )
        expected = {
            "correctAnswer": "test expression 1",
            "usersAnswer": "test expression 1",
            "definition": "test definition",
            "translation": "тестовий вираз",
            "example": "example of usage of test expression",
        }

        self.assertEqual(expected, actual)

        self.mock_dt_repo_get.assert_called_once_with()
        self.mock_get_user_expr_by_id.assert_called_once_with("test_expr_id_1")
        self.mock_get_user_exprs.assert_not_called()
        self.mock_dt_repo_put.assert_called_once_with(
            {
                "knowledgeLevelThreshold": 0.9,
                "learnListSize": 3,
                "practiceCountThreshold": 90,
                "learning_list": [
                    {
                        "expressionId": "test_expr_id_2",
                        "knowledgeLevel": 0.5,
                        "position": 2,
                        "practiceCount": 2,
                        "lastPracticeTime": None,
                    },
                    {
                        "expressionId": "test_expr_id_3",
                        "knowledgeLevel": 0.7,
                        "position": 3,
                        "practiceCount": 3,
                        "lastPracticeTime": None,
                    },
                    {
                        "expressionId": "test_expr_id_1",
                        "knowledgeLevel": 0.801980198019802,
                        "position": 2,
                        "practiceCount": 101,
                        "lastPracticeTime": self.mock_time,
                    },
                ],
            }
        )

        put_u_expr = self.mock_put_user_expr.call_args.args[0]

        self.assertEqual(mock_expr, put_u_expr.expression)
        self.assertEqual(0.5, put_u_expr.knowledge_level)
        self.assertEqual(2, put_u_expr.practice_count)
        self.assertEqual(self.mock_time, put_u_expr.last_practice_time)

    def test_submit_challenge_practice_count_not_enough(self):
        self.mock_dt_repo_get.return_value = get_dt_data(
            [
                get_learn_list_item(
                    item_id="test_expr_id_1",
                    position=2,
                    pract_count=88,
                    know_level=0.9,
                ),
                get_learn_list_item(
                    item_id="test_expr_id_2",
                    position=2,
                    pract_count=2,
                    know_level=0.5,
                ),
                get_learn_list_item(
                    item_id="test_expr_id_3",
                    position=3,
                    pract_count=3,
                    know_level=0.7,
                ),
            ],
            lls=3,
        )

        mock_user = get_user(self.user_id)
        mock_expr = get_expression(
            expression_id="test_expr_id_1",
            expression="test expression 1",
        )
        self.mock_get_user_expr_by_id.return_value = get_user_expression(
            user_id=self.user_id,
            user=mock_user,
            expression=mock_expr,
            kl=0,
            pc=1,
        )

        subject = DailyTraining(self.user_id)

        actual = subject.submit_challenge(
            "test_expr_id_1", "test expression 1"
        )
        expected = {
            "correctAnswer": "test expression 1",
            "usersAnswer": "test expression 1",
            "definition": "test definition",
            "translation": "тестовий вираз",
            "example": "example of usage of test expression",
        }

        self.assertEqual(expected, actual)

        self.mock_dt_repo_get.assert_called_once_with()
        self.mock_get_user_expr_by_id.assert_called_once_with("test_expr_id_1")
        self.mock_get_user_exprs.assert_not_called()
        self.mock_dt_repo_put.assert_called_once_with(
            {
                "knowledgeLevelThreshold": 0.9,
                "learnListSize": 3,
                "practiceCountThreshold": 90,
                "learning_list": [
                    {
                        "expressionId": "test_expr_id_2",
                        "knowledgeLevel": 0.5,
                        "position": 2,
                        "practiceCount": 2,
                        "lastPracticeTime": None,
                    },
                    {
                        "expressionId": "test_expr_id_3",
                        "knowledgeLevel": 0.7,
                        "position": 3,
                        "practiceCount": 3,
                        "lastPracticeTime": None,
                    },
                    {
                        "expressionId": "test_expr_id_1",
                        "knowledgeLevel": 0.901123595505618,
                        "position": 2,
                        "practiceCount": 89,
                        "lastPracticeTime": self.mock_time,
                    },
                ],
            }
        )

        put_u_expr = self.mock_put_user_expr.call_args.args[0]

        self.assertEqual(mock_expr, put_u_expr.expression)
        self.assertEqual(0.5, put_u_expr.knowledge_level)
        self.assertEqual(2, put_u_expr.practice_count)
        self.assertEqual(self.mock_time, put_u_expr.last_practice_time)

    def test_submit_challenge_when_expression_not_found(self):
        self.mock_dt_repo_get.return_value = get_dt_data(
            [
                get_learn_list_item(
                    item_id="test_expr_id_1",
                    position=1,
                    pract_count=1,
                    know_level=0,
                ),
            ],
            lls=3,
        )

        self.mock_get_user_expr_by_id.return_value = None

        subject = DailyTraining(self.user_id)

        with self.assertRaises(ExpressionNotFoundException):
            subject.submit_challenge("test_expr_id_1", "test expression 1")

        self.mock_dt_repo_get.assert_called_once_with()
        self.mock_get_user_expr_by_id.assert_called_once_with("test_expr_id_1")
        self.mock_get_user_exprs.assert_not_called()
        self.mock_dt_repo_put.assert_not_called()
        self.mock_put_user_expr.assert_not_called()

    def test_submit_challenge_no_learning_list_item(self):
        self.mock_dt_repo_get.return_value = get_dt_data(
            [
                get_learn_list_item(
                    item_id="test_expr_id_2",
                    position=1,
                    pract_count=1,
                    know_level=0,
                ),
            ],
            lls=3,
        )

        mock_user = get_user(self.user_id)
        mock_expr = get_expression(
            expression_id="test_expr_id_1",
            expression="test expression 1",
        )
        self.mock_get_user_expr_by_id.return_value = get_user_expression(
            user_id=self.user_id,
            user=mock_user,
            expression=mock_expr,
            kl=0,
            pc=1,
        )

        subject = DailyTraining(self.user_id)

        with self.assertRaises(LearnListItemNotFoundExpression):
            subject.submit_challenge("test_expr_id_1", "test expression 1")

        self.mock_dt_repo_get.assert_called_once_with()
        self.mock_get_user_expr_by_id.assert_called_once_with("test_expr_id_1")
        self.mock_get_user_exprs.assert_not_called()
        self.mock_dt_repo_put.assert_not_called()
        self.mock_put_user_expr.assert_not_called()


class GetLearnListExpressionsTests(TestCase):
    def setUp(self):
        self.user_id = "test_user_id"

        dt_repo_patcher = patch(
            "exercises.daily_training_v2.DailyTrainingRepo"
        )
        mock_dt_repo = dt_repo_patcher.start()
        self.mock_dt_repo_get = mock_dt_repo.return_value.get
        self.addCleanup(dt_repo_patcher.stop)

        us_expr_patcher = patch(
            "exercises.daily_training_v2.UserExpressionsRepo"
        )
        mock_us_expr_repo = us_expr_patcher.start()
        self.mock_get_user_exprs = mock_us_expr_repo.return_value.get
        self.addCleanup(us_expr_patcher.stop)

    def test_get_learn_list_expressions(self):
        expr_id_1 = "test_expr_id_1"
        expr_id_2 = "test_expr_id_2"

        self.mock_dt_repo_get.return_value = get_dt_data(
            [
                get_learn_list_item(
                    item_id=expr_id_1,
                    pract_count=3,
                    last_pract_time="2023-04-12 10:10:25",
                ),
                get_learn_list_item(item_id=expr_id_2, pract_count=4),
            ],
        )
        user = get_user(self.user_id)
        expr_1 = get_expression(expr_id_1, "expression 1")
        expr_2 = get_expression(expr_id_2, "expression 2")
        self.mock_get_user_exprs.return_value = [
            get_user_expression(
                user_id=self.user_id,
                user=user,
                expression=expr_1,
                pc=3,
                lpt="2023-04-12 10:10:25",
            ),
            get_user_expression(
                user_id=self.user_id,
                user=user,
                expression=expr_2,
                pc=4,
                lpt="2023-04-12 10:10:20",
            ),
        ]
        expected = [
            {
                "expression_id": expr_id_2,
                "expression": "expression 2",
                "knowledge_level": 0,
                "practice_count": 4,
                "last_practice_time": None,
            },
            {
                "expression_id": expr_id_1,
                "expression": "expression 1",
                "knowledge_level": 0,
                "practice_count": 3,
                "last_practice_time": datetime.strptime(
                    "2023-04-12 10:10:25", "%Y-%m-%d %H:%M:%S"
                ),
            },
        ]

        subject = DailyTraining(self.user_id)

        actual = subject.get_learn_list_expressions()

        self.assertEqual(expected, actual)

        self.mock_dt_repo_get.assert_called_once_with()
        self.mock_get_user_exprs.assert_called_once_with(
            include=[expr_id_1, expr_id_2]
        )

    def test_get_learn_list_expressions_got_no_user_expressions(self):
        expr_id_1 = "test_expr_id_1"
        expr_id_2 = "test_expr_id_2"

        self.mock_dt_repo_get.return_value = get_dt_data(
            [
                get_learn_list_item(
                    item_id=expr_id_1,
                ),
                get_learn_list_item(
                    item_id=expr_id_2,
                ),
            ],
        )
        self.mock_get_user_exprs.return_value = []

        subject = DailyTraining(self.user_id)

        with self.assertRaises(ExpressionNotFoundException):
            subject.get_learn_list_expressions()

        self.mock_dt_repo_get.assert_called_once_with()
        self.mock_get_user_exprs.assert_called_once_with(
            include=[expr_id_1, expr_id_2]
        )

    def test_get_learn_list_expressions_empty_llist(self):
        self.mock_dt_repo_get.return_value = get_dt_data([])

        subject = DailyTraining(self.user_id)

        actual = subject.get_learn_list_expressions()

        self.assertEqual([], actual)

        self.mock_dt_repo_get.assert_called_once_with()
        self.mock_get_user_exprs.assert_not_called()


class RemoveItemFromLearnListTests(TestCase):
    def setUp(self):
        self.user_id = "test_user_id"

        dt_repo_patcher = patch(
            "exercises.daily_training_v2.DailyTrainingRepo"
        )
        mock_dt_repo = dt_repo_patcher.start()
        self.mock_dt_repo_get = mock_dt_repo.return_value.get
        self.mock_dt_repo_put = mock_dt_repo.return_value.put
        self.addCleanup(dt_repo_patcher.stop)

    def test_remove_item_from_learn_list(self):
        expr_id_1 = "test_expr_id_1"
        expr_id_2 = "test_expr_id_2"

        item_1 = get_learn_list_item(item_id=expr_id_1)
        item_2 = get_learn_list_item(item_id=expr_id_2)

        self.mock_dt_repo_get.return_value = get_dt_data([item_1, item_2])

        subject = DailyTraining(self.user_id)

        subject.remove_item_from_learn_list(expr_id_1)

        self.mock_dt_repo_put.assert_called_once_with(get_dt_data([item_2]))

    def test_remove_nonexisting_item_from_learn_list_raises_exception(self):
        expr_id_1 = "test_expr_id_1"

        item_1 = get_learn_list_item(item_id=expr_id_1)

        self.mock_dt_repo_get.return_value = get_dt_data([item_1])

        subject = DailyTraining(self.user_id)

        with self.assertRaises(LearnListItemNotFoundExpression):
            subject.remove_item_from_learn_list("nonexisting id")

        self.mock_dt_repo_put.assert_not_called()


class UpdateSettingsTests(TestCase):
    def setUp(self):
        self.user_id = "test_user_id"
        self.user = get_user(self.user_id)

        dt_repo_patcher = patch(
            "exercises.daily_training_v2.DailyTrainingRepo"
        )
        mock_dt_repo = dt_repo_patcher.start()

        self.mock_dt_repo_get = mock_dt_repo.return_value.get

        self.mock_dt_repo_put = mock_dt_repo.return_value.put
        self.addCleanup(dt_repo_patcher.stop)

        user_expr_repo_patcher = patch(
            "exercises.daily_training_v2.UserExpressionsRepo"
        )
        mock_user_expr_repo = user_expr_repo_patcher.start()
        self.mock_user_expr_repo_get = mock_user_expr_repo.return_value.get
        self.addCleanup(user_expr_repo_patcher.stop)

    def test_update_settings(self):
        ll_item_1 = get_learn_list_item(item_id="id-1")
        ll_item_2 = get_learn_list_item(
            item_id="id-2", position=2, pract_count=9, know_level=0.9
        )
        ll_item_3 = get_learn_list_item(
            item_id="id-3", position=3, pract_count=10, know_level=0.82
        )
        ll_item_4 = get_learn_list_item(
            item_id="id-4", position=4, pract_count=13, know_level=0.80
        )
        ll_item_5 = get_learn_list_item(
            item_id="id-5", position=5, pract_count=12, know_level=0.84
        )
        ll_item_6 = get_learn_list_item(
            item_id="id-6", position=6, pract_count=12, know_level=0.84
        )
        ll_item_7 = get_learn_list_item(
            item_id="id-7", position=7, pract_count=13, know_level=0.86
        )

        self.mock_dt_repo_get.return_value = get_dt_data(
            ll=[
                ll_item_1,
                ll_item_2,
                ll_item_3,
                ll_item_4,
                ll_item_5,
                ll_item_6,
                ll_item_7,
            ],
            lls=6,
            pct=20,
        )
        self.mock_user_expr_repo_get.return_value = [
            get_user_expression(
                self.user_id,
                self.user,
                expression=get_expression("id-7", "test expression"),
                kl=0,
                pc=0,
            )
        ]

        subject = DailyTraining(self.user_id)
        subject.update_settings(5, 10, 0.84)

        self.mock_user_expr_repo_get.assert_called_once_with(
            exclude=["id-1", "id-2", "id-3", "id-4"], limit=1
        )
        self.mock_dt_repo_put.assert_called_once_with(
            {
                "knowledgeLevelThreshold": 0.84,
                "learnListSize": 5,
                "practiceCountThreshold": 10,
                "learning_list": [
                    {
                        "expressionId": "id-7",
                        "knowledgeLevel": 0,
                        "position": 0,
                        "practiceCount": 0,
                        "lastPracticeTime": None,
                    },
                    {
                        "expressionId": "id-1",
                        "knowledgeLevel": 0,
                        "position": 1,
                        "practiceCount": 0,
                        "lastPracticeTime": None,
                    },
                    {
                        "expressionId": "id-2",
                        "knowledgeLevel": 0.9,
                        "position": 2,
                        "practiceCount": 9,
                        "lastPracticeTime": None,
                    },
                    {
                        "expressionId": "id-3",
                        "knowledgeLevel": 0.82,
                        "position": 3,
                        "practiceCount": 10,
                        "lastPracticeTime": None,
                    },
                    {
                        "expressionId": "id-4",
                        "knowledgeLevel": 0.8,
                        "position": 4,
                        "practiceCount": 13,
                        "lastPracticeTime": None,
                    },
                ],
            }
        )


class RefreshLearningListTests(TestCase):
    def setUp(self):
        self.user_id = "test_user_id"

        dt_repo_patcher = patch(
            "exercises.daily_training_v2.DailyTrainingRepo"
        )
        mock_dt_repo = dt_repo_patcher.start()
        self.mock_dt_repo_get = mock_dt_repo.return_value.get
        self.mock_dt_repo_put = mock_dt_repo.return_value.put
        self.addCleanup(dt_repo_patcher.stop)

        us_expr_patcher = patch(
            "exercises.daily_training_v2.UserExpressionsRepo"
        )
        mock_us_expr_repo = us_expr_patcher.start()
        self.mock_get_user_exprs = mock_us_expr_repo.return_value.get
        self.addCleanup(us_expr_patcher.stop)

    def test_refresh_with_adding(self):
        expr_id_1 = "test_expr_id_1"
        expr_id_2 = "test_expr_id_2"
        expr_id_3 = "test_expr_id_3"
        self.mock_dt_repo_get.return_value = get_dt_data(
            [get_learn_list_item(item_id=expr_id_1)], lls=3
        )
        self.mock_get_user_exprs.return_value = [
            get_user_expression(
                user_id=self.user_id,
                user=get_user(self.user_id),
                expression=get_expression(expr_id_2, "expression 1"),
                pc=3,
                lpt="2023-04-12 10:10:25",
            ),
            get_user_expression(
                user_id=self.user_id,
                user=get_user(self.user_id),
                expression=get_expression(expr_id_3, "expression 3"),
                pc=4,
                lpt="2023-04-12 10:10:20",
            ),
        ]

        subject = DailyTraining(self.user_id)

        subject.refresh_learning_list()

        self.mock_get_user_exprs.assert_called_once_with(
            exclude=["test_expr_id_1"], limit=2
        )
        self.mock_dt_repo_put.assert_called_once_with(
            get_dt_data(
                [
                    get_learn_list_item(item_id=expr_id_2, position=0),
                    get_learn_list_item(item_id=expr_id_3, position=0),
                    get_learn_list_item(item_id=expr_id_1),
                ],
                lls=3,
            )
        )

    def test_refresh_no_user_expressions_to_add(self):
        expr_id_1 = "test_expr_id_1"
        dt_data = get_dt_data([get_learn_list_item(item_id=expr_id_1)], lls=3)
        self.mock_dt_repo_get.return_value = dt_data
        self.mock_get_user_exprs.return_value = []

        subject = DailyTraining(self.user_id)

        subject.refresh_learning_list()

        self.mock_get_user_exprs.assert_called_once_with(
            exclude=["test_expr_id_1"], limit=2
        )
        self.mock_dt_repo_put.assert_called_once_with(dt_data)

    def test_refresh_nothing_to_change(self):
        expr_id_1 = "test_expr_id_1"
        dt_data = get_dt_data([get_learn_list_item(item_id=expr_id_1)], lls=1)
        self.mock_dt_repo_get.return_value = dt_data

        subject = DailyTraining(self.user_id)

        subject.refresh_learning_list()

        self.mock_get_user_exprs.assert_not_called()
        self.mock_dt_repo_put.assert_called_once_with(dt_data)

    def test_refresh_current_llist_bigger_than_in_settings(self):
        expr_id_1 = "test_expr_id_1"
        expr_id_2 = "test_expr_id_2"
        expr_id_3 = "test_expr_id_3"
        dt_data = get_dt_data(
            [
                get_learn_list_item(item_id=expr_id_1),
                get_learn_list_item(item_id=expr_id_2),
                get_learn_list_item(item_id=expr_id_3),
            ],
            lls=2,
        )
        self.mock_dt_repo_get.return_value = dt_data

        subject = DailyTraining(self.user_id)

        subject.refresh_learning_list()

        self.mock_get_user_exprs.assert_not_called()
        self.mock_dt_repo_put.assert_called_once_with(dt_data)


class AddItemToLearnListTests(TestCase):
    def setUp(self):
        self.user_id = "test_user_id"

        dt_repo_patcher = patch(
            "exercises.daily_training_v2.DailyTrainingRepo"
        )
        mock_dt_repo = dt_repo_patcher.start()
        self.mock_dt_repo_get = mock_dt_repo.return_value.get
        self.mock_dt_repo_put = mock_dt_repo.return_value.put
        self.addCleanup(dt_repo_patcher.stop)

    def test_add_item_to_learn_list(self):
        expr_id_1 = "test_expr_id_1"
        expr_id_2 = "test_expr_id_2"
        self.mock_dt_repo_get.return_value = get_dt_data(
            [get_learn_list_item(item_id=expr_id_1)], lls=3
        )

        subject = DailyTraining(self.user_id)
        subject.add_item_to_learn_list(expr_id_2)

        self.mock_dt_repo_put.assert_called_once_with(
            get_dt_data(
                [
                    get_learn_list_item(item_id=expr_id_2, position=0),
                    get_learn_list_item(item_id=expr_id_1),
                ],
                lls=3,
            )
        )

    def test_add_item_to_learn_list_when_llist_has_already_max_size_is_ok(
        self,
    ):
        expr_id_1 = "test_expr_id_1"
        expr_id_2 = "test_expr_id_2"
        expr_id_3 = "test_expr_id_3"

        self.mock_dt_repo_get.return_value = get_dt_data(
            [
                get_learn_list_item(item_id=expr_id_1),
                get_learn_list_item(item_id=expr_id_2),
            ],
            lls=2,
        )

        subject = DailyTraining(self.user_id)
        subject.add_item_to_learn_list(expr_id_3)

        self.mock_dt_repo_put.assert_called_once_with(
            get_dt_data(
                [
                    get_learn_list_item(item_id=expr_id_3, position=0),
                    get_learn_list_item(item_id=expr_id_1),
                    get_learn_list_item(item_id=expr_id_2),
                ],
                lls=2,
            )
        )


class CountLearnListItemsTests(TestCase):
    def setUp(self):
        self.user_id = "test_user_id"

        dt_repo_patcher = patch(
            "exercises.daily_training_v2.DailyTrainingRepo"
        )
        mock_dt_repo = dt_repo_patcher.start()
        self.mock_dt_repo_get = mock_dt_repo.return_value.get
        self.addCleanup(dt_repo_patcher.stop)

    def test_count_learn_list(self):
        expr_id_1 = "test_expr_id_1"
        expr_id_2 = "test_expr_id_2"
        expr_id_3 = "test_expr_id_3"
        dt_data = get_dt_data(
            [
                get_learn_list_item(item_id=expr_id_1),
                get_learn_list_item(item_id=expr_id_2),
                get_learn_list_item(item_id=expr_id_3),
            ],
        )
        self.mock_dt_repo_get.return_value = dt_data

        subject = DailyTraining(self.user_id)

        actual = subject.count_learn_list_items()

        self.assertEqual(3, actual)


class IsExpressionInLearnListTests(TestCase):
    def setUp(self):
        self.user_id = "d32cd1e8-7111-4e0a-84aa-c5664df8a063"

        dt_repo_patcher = patch(
            "exercises.daily_training_v2.DailyTrainingRepo"
        )
        mock_dt_repo = dt_repo_patcher.start()
        self.mock_dt_repo_get = mock_dt_repo.return_value.get
        self.addCleanup(dt_repo_patcher.stop)

    def test_expression_id_in_learn_list(self):
        self.mock_dt_repo_get.return_value = get_dt_data(
            [get_learn_list_item("item_id_1")]
        )

        self.assertTrue(
            DailyTraining(self.user_id).is_expression_in_learn_list(
                "item_id_1"
            )
        )

    def test_expression_id_not_in_learn_list(self):
        self.mock_dt_repo_get.return_value = get_dt_data(
            [get_learn_list_item("item_id_1")]
        )

        self.assertFalse(
            DailyTraining(self.user_id).is_expression_in_learn_list(
                "item_id_2"
            )
        )

    def test_expression_id_not_in_empty_learn_list(self):
        self.mock_dt_repo_get.return_value = get_dt_data([])

        self.assertFalse(
            DailyTraining(self.user_id).is_expression_in_learn_list(
                "item_id_2"
            )
        )
