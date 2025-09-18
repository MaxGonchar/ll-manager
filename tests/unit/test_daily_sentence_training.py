from unittest import TestCase
from unittest.mock import Mock
import random

from exercises.sentence_training_v2 import SentenceTraining
from exercises.exceptions import (
    ContextNotFoundException,
    ExpressionNotFoundException,
)
from repository.training_expressions_repo import TrainingRepoABC
from tests.unit.fixtures import (
    get_user_expression,
    get_expression,
    get_user,
    get_expression_context,
)


class SentenceTrainingTestHelper(TestCase):
    def setUp(self):
        self.repo = Mock(spec=TrainingRepoABC)
        self.user_expression = get_user_expression(
            user_id="test-user-id",
            user=get_user("test-user-id"),
            expression=get_expression(
                expression_id="test-expression-id",
                expression="bow",
                definition="a knot tied with two loops and two loose ends, used especially for tying shoelaces and decorative ribbons.",
                context=[
                    get_expression_context(
                        id_="test-context-id-1",
                        expression_id="test-expression-id",
                        sentence="She expertly tied a bow on her daughter's hair ribbon, making her look adorable for the party.",
                        translation={
                            "uk": "Вона майстерно зав'язала перев'язку на стрічці дочки, зробивши її виглядати мило для вечірки."
                        },
                        template={
                            "tpl": "She expertly tied a {} on her daughter's hair ribbon",
                            "values": ["bow"],
                        },
                    ),
                    get_expression_context(
                        id_="test-context-id-2",
                        expression_id="test-expression-id",
                        sentence="The bow on the gift box was so beautifully crafted that it made the present seem even more special.",
                        translation={
                            "uk": "Перев'язка на подарунку була дуже гарно зроблена, тому подарунок виглядав ще більш особливим."
                        },
                        template={
                            "tpl": "The {} on the gift box was so beautifully crafted that it made the present seem even more special.",
                            "values": ["bow"],
                        },
                    ),
                    get_expression_context(
                        id_="test-context-id-3",
                        expression_id="test-expression-id",
                        sentence="When learning to tie a bow, it's important to practice with shoelaces to master the technique.",
                        translation={
                            "uk": "При навчанні зав'язуванню перев'язки важливо практикуватися на шнурках, щоб оволодіти технікою."
                        },
                        template={
                            "tpl": "When learning to tie a {}, it's important to practice with shoelaces to master the technique.",
                            "values": ["bow"],
                        },
                    ),
                ],
            ),
        )


class GetExpressionsNumberCanBeTrainedInSentenceTest(
    SentenceTrainingTestHelper
):
    def setUp(self):
        super().setUp()
        self.subject = SentenceTraining(self.repo)

    def test_get_expressions_number_can_be_trained_in_sentence(self):
        self.repo.count_learn_list_items.return_value = 5
        actual = (
            self.subject.get_expressions_number_can_be_trained_in_sentence()
        )
        self.assertEqual(5, actual)
        self.repo.count_learn_list_items.assert_called_once()


class GetChallengeTest(SentenceTrainingTestHelper):
    def setUp(self) -> None:
        super().setUp()
        random.seed(0)

    def test_get_challenge(self):
        self.repo.get_next.return_value = [
            {
                "expression": self.user_expression,
                "knowledgeLevel": 0.5,
                "practiceCount": 3,
            }
        ]
        subject = SentenceTraining(self.repo)
        expected = {
            "expressionId": "test-expression-id",
            "contextId": "test-context-id-2",
            "sentence": "The bow on the gift box was so beautifully crafted that it made the present seem even more special.",
            "translation": "Перев'язка на подарунку була дуже гарно зроблена, тому подарунок виглядав ще більш особливим.",
            "template": "The {} on the gift box was so beautifully crafted that it made the present seem even more special.",
            "values": ["bow"],
            "practiceCount": 3,
            "knowledgeLevel": 0.5,
        }
        actual = subject.get_challenge()
        self.assertEqual(expected, actual)
        self.repo.get_next.assert_called_once_with(1)

    def test_get_challenge_no_expressions(self):
        self.repo.get_next.return_value = []
        subject = SentenceTraining(self.repo)
        actual = subject.get_challenge()
        self.assertIsNone(actual)
        self.repo.get_next.assert_called_once_with(1)

    def test_get_challenge_no_contexts(self):
        self.user_expression.expression.context = []
        self.repo.get_next.return_value = [
            {
                "expression": self.user_expression,
                "knowledgeLevel": 0.5,
                "practiceCount": 3,
            }
        ]
        subject = SentenceTraining(self.repo)

        with self.assertRaises(ContextNotFoundException):
            subject.get_challenge()

        self.repo.get_next.assert_called_once_with(1)


class SubmitChallengeTest(SentenceTrainingTestHelper):
    def test_submit_challenge_success(self):
        self.repo.get_by_ids.return_value = [self.user_expression]
        subject = SentenceTraining(self.repo)
        actual = subject.submit_challenge(
            expression_id="test-expression-id",
            context_id="test-context-id-2",
            answer="The bow on the gift box was so beautifully crafted that it made the present seem even more special.",
            hint=False,
        )
        expected = {
            "correctAnswer": "The bow on the gift box was so beautifully crafted that it made the present seem even more special.",
            "usersAnswer": "The bow on the gift box was so beautifully crafted that it made the present seem even more special.",
            "translation": "Перев'язка на подарунку була дуже гарно зроблена, тому подарунок виглядав ще більш особливим.",
        }

        self.assertEqual(expected, actual)
        self.repo.get_by_ids.assert_called_once_with(["test-expression-id"])
        self.repo.update_expressions.assert_called_once_with(
            [
                {
                    "user_expression": self.user_expression,
                    "is_trained_successfully": True,
                }
            ]
        )

    def test_submit_challenge_failure(self):
        self.repo.get_by_ids.return_value = [self.user_expression]
        subject = SentenceTraining(self.repo)
        actual = subject.submit_challenge(
            expression_id="test-expression-id",
            context_id="test-context-id-2",
            answer="Wrong answer",
            hint=False,
        )
        expected = {
            "correctAnswer": "The bow on the gift box was so beautifully crafted that it made the present seem even more special.",
            "usersAnswer": "Wrong answer",
            "translation": "Перев'язка на подарунку була дуже гарно зроблена, тому подарунок виглядав ще більш особливим.",
        }

        self.assertEqual(expected, actual)
        self.repo.get_by_ids.assert_called_once_with(["test-expression-id"])
        self.repo.update_expressions.assert_called_once_with(
            [
                {
                    "user_expression": self.user_expression,
                    "is_trained_successfully": False,
                }
            ]
        )

    def test_submit_challenge_with_hint(self):
        self.repo.get_by_ids.return_value = [self.user_expression]
        subject = SentenceTraining(self.repo)
        actual = subject.submit_challenge(
            expression_id="test-expression-id",
            context_id="test-context-id-2",
            answer="Wrong answer",
            hint=True,
        )
        expected = {
            "correctAnswer": "The bow on the gift box was so beautifully crafted that it made the present seem even more special.",
            "usersAnswer": "Wrong answer",
            "translation": "Перев'язка на подарунку була дуже гарно зроблена, тому подарунок виглядав ще більш особливим.",
        }

        self.assertEqual(expected, actual)
        self.repo.get_by_ids.assert_called_once_with(["test-expression-id"])
        self.repo.update_expressions.assert_not_called()

    def test_submit_challenge_expression_not_found(self):
        self.repo.get_by_ids.return_value = []
        subject = SentenceTraining(self.repo)
        with self.assertRaises(ExpressionNotFoundException):
            subject.submit_challenge(
                expression_id="non-existent-id",
                context_id="test-context-id-2",
                answer="Wrong answer",
                hint=False,
            )
        self.repo.get_by_ids.assert_called_once_with(["non-existent-id"])
        self.repo.update_expressions.assert_not_called()

    def test_submit_challenge_context_not_found(self):
        self.repo.get_by_ids.return_value = [self.user_expression]
        subject = SentenceTraining(self.repo)
        with self.assertRaises(ContextNotFoundException):
            subject.submit_challenge(
                expression_id="test-expression-id",
                context_id="non-existent-context-id",
                answer="Wrong answer",
                hint=False,
            )
        self.repo.get_by_ids.assert_called_once_with(["test-expression-id"])
        self.repo.update_expressions.assert_not_called()
