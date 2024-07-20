from unittest import TestCase
from unittest.mock import patch

from tests.unit.fixtures import get_user_expression, get_user, get_expression
from exercises.expression_recall import ExpressionRecall
from exercises.exceptions import ExpressionNotFoundException


class GetChallengeTests(TestCase):
    def setUp(self):
        self.user_id = "test_user_id"

        repo_patcher = patch("exercises.expression_recall.UserExpressionsRepo")
        mock_repo = repo_patcher.start()
        self.mock_get = mock_repo.return_value.get_oldest_trained_expression
        self.addCleanup(repo_patcher.stop)

        self.subject = ExpressionRecall(self.user_id)

    def test_challenge_is_got(self):
        expression = "test expression"
        definition = "test definition"
        expression_id = "test_expression_id"

        self.mock_get.return_value = get_user_expression(
            user_id=self.user_id,
            user=get_user(self.user_id),
            expression=get_expression(expression_id, expression, definition),
        )

        actual = self.subject.get_challenge()
        expected = {
            "answer": expression,
            "expression_id": expression_id,
            "question": definition,
            "tip": expression,
        }

        self.assertEqual(expected, actual)

        self.mock_get.assert_called_once_with()

    def test_no_expression_for_challenge_returns_none(self):
        self.mock_get.return_value = None

        self.assertIsNone(self.subject.get_challenge())

        self.mock_get.assert_called_once_with()


class SubmitChallengeTests(TestCase):
    def setUp(self):
        self.user_id = "test_user_id"

        repo_patcher = patch("exercises.expression_recall.UserExpressionsRepo")
        mock_repo = repo_patcher.start()
        self.mock_get = mock_repo.return_value.get_by_id
        self.mock_put = mock_repo.return_value.put
        self.addCleanup(repo_patcher.stop)

        self.test_user_expr = get_user_expression(
            user_id=self.user_id,
            user=get_user(self.user_id),
            expression=get_expression("expression_id", "expression"),
            kl=0.5,
            pc=9,
        )

        self.subject = ExpressionRecall(self.user_id)

    @patch("exercises.expression_recall.get_current_utc_time")
    def test_submit_successful_challenge(self, mock_get_time):
        self.mock_get.return_value = self.test_user_expr
        mock_get_time.return_value = "test_time"

        actual = self.subject.submit_challenge("expr_id", "expression")
        expected = {
            "correctAnswer": self.test_user_expr.expression.expression,
            "definition": self.test_user_expr.expression.definition,
            "example": self.test_user_expr.expression.example,
            "translation": self.test_user_expr.expression.translation("uk"),
            "usersAnswer": "expression",
        }

        self.assertEqual(expected, actual)

        self.mock_get.assert_called_once_with("expr_id")

        put_args = self.mock_put.call_args.args

        self.assertEqual(1, len(put_args))

        self.assertEqual(
            self.test_user_expr.expression, put_args[0].expression
        )
        self.assertEqual(0.55, put_args[0].knowledge_level)
        self.assertEqual(10, put_args[0].practice_count)
        self.assertEqual("test_time", put_args[0].last_practice_time)

    @patch("exercises.expression_recall.get_current_utc_time")
    def test_submit_failed_challenge(self, mock_get_time):
        self.mock_get.return_value = self.test_user_expr
        mock_get_time.return_value = "test_time"

        actual = self.subject.submit_challenge("expr_id", "aboba")
        expected = {
            "correctAnswer": self.test_user_expr.expression.expression,
            "definition": self.test_user_expr.expression.definition,
            "example": self.test_user_expr.expression.example,
            "translation": self.test_user_expr.expression.translation("uk"),
            "usersAnswer": "aboba",
        }

        self.assertEqual(expected, actual)

        self.mock_get.assert_called_once_with("expr_id")

        put_args = self.mock_put.call_args.args

        self.assertEqual(1, len(put_args))

        self.assertEqual(
            self.test_user_expr.expression, put_args[0].expression
        )
        self.assertEqual(0.45, put_args[0].knowledge_level)
        self.assertEqual(10, put_args[0].practice_count)
        self.assertEqual("test_time", put_args[0].last_practice_time)

    def test_submit_challenge_with_hint(self):
        self.mock_get.return_value = self.test_user_expr

        actual = self.subject.submit_challenge("expr_id", "aboba", hint=True)
        expected = {
            "correctAnswer": self.test_user_expr.expression.expression,
            "definition": self.test_user_expr.expression.definition,
            "example": self.test_user_expr.expression.example,
            "translation": self.test_user_expr.expression.translation("uk"),
            "usersAnswer": "aboba",
        }

        self.assertEqual(expected, actual)

        self.mock_get.assert_called_once_with("expr_id")
        self.mock_put.assert_not_called()

    def test_submit_challenge_when_user_expression_not_found_raises_exception(
        self,
    ):
        self.mock_get.return_value = None

        with self.assertRaises(ExpressionNotFoundException):
            self.subject.submit_challenge("expr_id", "aboba")

        self.mock_get.assert_called_once_with("expr_id")
        self.mock_put.assert_not_called()


class GetNumberOfExpressionsNeededRecallingTests(TestCase):
    def setUp(self):
        self.user_id = "test_user_id"

        repo_patcher = patch("exercises.expression_recall.UserExpressionsRepo")
        mock_repo = repo_patcher.start()
        self.mock_get_count = mock_repo.return_value.count_trained_expressions
        self.addCleanup(repo_patcher.stop)

        self.subject = ExpressionRecall(self.user_id)

    def test_get_number_of_expressions_needed_recalling(self):
        self.mock_get_count.return_value = 10

        self.assertEqual(
            10, self.subject.get_number_of_expressions_needed_recalling()
        )


class GetExpressionsNeededRecallingTests(TestCase):
    def setUp(self):
        self.user_id = "test_user_id"

        repo_patcher = patch("exercises.expression_recall.UserExpressionsRepo")
        mock_repo = repo_patcher.start()
        self.mock_get = mock_repo.return_value.get_all_trained_expressions
        self.addCleanup(repo_patcher.stop)

        self.subject = ExpressionRecall(self.user_id)

    def test_get_expressions_needed_recalling(self):
        expr_id_1 = "expr_id_1"
        expr_1 = "expr_1"
        lpt_1 = "2016-06-22 19:10:25"
        kl_1 = 0.5
        pc_1 = 10
        expr_id_2 = "expr_id_2"
        expr_2 = "expr_2"
        lpt_2 = "2016-06-23 19:10:25"
        kl_2 = 0.8
        pc_2 = 3

        self.mock_get.return_value = [
            get_user_expression(
                self.user_id,
                user=get_user(self.user_id),
                expression=get_expression(
                    expression_id=expr_id_1, expression=expr_1
                ),
                kl=kl_1,
                pc=pc_1,
                lpt=lpt_1,
            ),
            get_user_expression(
                self.user_id,
                user=get_user(self.user_id),
                expression=get_expression(
                    expression_id=expr_id_2, expression=expr_2
                ),
                kl=kl_2,
                pc=pc_2,
                lpt=lpt_2,
            ),
        ]

        actual = self.subject.get_expressions_needed_recalling()

        expected = [
            {
                "expression": expr_1,
                "expression_id": expr_id_1,
                "knowledge_level": kl_1,
                "last_practice_time": lpt_1,
                "practice_count": pc_1,
            },
            {
                "expression": expr_2,
                "expression_id": expr_id_2,
                "knowledge_level": kl_2,
                "last_practice_time": lpt_2,
                "practice_count": pc_2,
            },
        ]

        self.assertEqual(expected, actual)

        self.mock_get.assert_called_once_with()

    def test_get_expressions_needed_recalling_no_expressions(self):
        self.mock_get.return_value = []

        actual = self.subject.get_expressions_needed_recalling()

        self.assertEqual([], actual)

        self.mock_get.assert_called_once_with()
