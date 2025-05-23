from unittest import TestCase
from unittest.mock import patch

from exercises.sentence_training import SentenceTraining


class GetExpressionsNumberCanBeTrainedInSentenceTests(TestCase):
    def setUp(self) -> None:
        self.user_id = "test_user_id"

        repo_patcher = patch("exercises.sentence_training.UserExpressionsDAO")
        mock_repo = repo_patcher.start()
        self.mock_count = (
            mock_repo.return_value.count_trained_expressions_having_context
        )
        self.addCleanup(repo_patcher.stop)

    def test_get(self):
        expected = 5
        self.mock_count.return_value = expected

        actual = SentenceTraining(
            self.user_id
        ).get_expressions_number_can_be_trained_in_sentence()

        self.assertEqual(expected, actual)
        self.mock_count.assert_called_once_with()
