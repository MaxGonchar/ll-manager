from unittest import TestCase
from unittest.mock import patch, call

from services.user_expression_service import UserExpressionService
from services.exceptions import (
    UserNotFoundException,
    TagNotFoundException,
    UserExpressionNotFoundException,
    InvalidPostUserExpressionDataException,
)
from tests.unit.fixtures import get_expression, get_user, get_user_expression
from tests.unit.fixtures import (
    get_tag,
)


class SearchTests(TestCase):
    def setUp(self):
        self.user_id = "test_user_id"

        user_expr_repo_patcher = patch(
            "services.user_expression_service.UserExpressionsRepo"
        )
        mock_ue_repo = user_expr_repo_patcher.start()
        self.mock_search = mock_ue_repo.return_value.search
        self.addCleanup(user_expr_repo_patcher.stop)

        daily_training_patcher = patch(
            "services.user_expression_service.DailyTraining"
        )
        mock_daily_training = daily_training_patcher.start()
        self.mock_is_in_llist = (
            mock_daily_training.return_value.is_expression_in_learn_list
        )
        self.addCleanup(daily_training_patcher.stop)

        self.subject = UserExpressionService(self.user_id)

    def test_search(self):
        user = get_user(self.user_id)

        expr_id_1 = "test_expr_id_1"
        expr_1 = "test_expression_1"
        know_level_1 = 0.91
        pract_count_1 = 1
        last_pract_time_1 = "2023-04-13 10:10:25"
        is_in_llist_1 = True

        expr_id_2 = "test_expr_id_2"
        expr_2 = "test_expression_2"
        know_level_2 = 0.92
        pract_count_2 = 2
        last_pract_time_2 = "2023-04-14 10:10:25"
        is_in_llist_2 = False

        self.mock_search.return_value = [
            get_user_expression(
                user_id=self.user_id,
                user=user,
                expression=get_expression(expr_id_1, expr_1),
                kl=know_level_1,
                pc=pract_count_1,
                lpt=last_pract_time_1,
            ),
            get_user_expression(
                user_id=self.user_id,
                user=user,
                expression=get_expression(expr_id_2, expr_2),
                kl=know_level_2,
                pc=pract_count_2,
                lpt=last_pract_time_2,
            ),
        ]
        self.mock_is_in_llist.side_effect = [True, False]

        actual = self.subject.search("pattern")
        expected = [
            {
                "expressionId": expr_id_1,
                "expression": expr_1,
                "knowledgeLevel": know_level_1,
                "practiceCount": pract_count_1,
                "lastPracticeTime": last_pract_time_1,
                "isInLearnList": is_in_llist_1,
            },
            {
                "expressionId": expr_id_2,
                "expression": expr_2,
                "knowledgeLevel": know_level_2,
                "practiceCount": pract_count_2,
                "lastPracticeTime": last_pract_time_2,
                "isInLearnList": is_in_llist_2,
            },
        ]

        self.assertEqual(expected, actual)
        self.mock_search.assert_called_once_with("pattern")

    def test_search_nothing_found(self):
        self.mock_search.return_value = []

        actual = self.subject.search("pattern")

        self.assertEqual([], actual)
        self.mock_search.assert_called_once_with("pattern")


class PostTests(TestCase):
    def setUp(self):
        self.user_id = "test_user_id"

        user_expr_repo_patcher = patch(
            "services.user_expression_service.UserExpressionsRepo"
        )
        mock_ue_repo = user_expr_repo_patcher.start()
        self.mock_post = mock_ue_repo.return_value.post
        self.addCleanup(user_expr_repo_patcher.stop)

        daily_training_patcher = patch(
            "services.user_expression_service.DailyTraining"
        )
        mock_daily_training = daily_training_patcher.start()
        self.mock_refresh_llist = (
            mock_daily_training.return_value.refresh_learning_list
        )
        self.addCleanup(daily_training_patcher.stop)

        user_repo_patcher = patch("services.user_expression_service.UsersDAO")
        self.mock_get_user = user_repo_patcher.start().return_value.get_by_id
        self.addCleanup(user_repo_patcher.stop)

        tag_repo_patcher = patch("services.user_expression_service.TagsRepo")
        self.mock_get_tag = tag_repo_patcher.start().return_value.get_by_name
        self.addCleanup(tag_repo_patcher.stop)

        self.subject = UserExpressionService(self.user_id)

    @patch("services.user_expression_service.uuid4")
    @patch("services.user_expression_service.get_current_utc_time")
    def test_post(self, mock_time, mock_uuid):
        expr_id = "58480d08-3626-453d-9b48-31086b4341ae"
        added = "2023-04-12 10:10:25"
        mock_time.return_value = added
        mock_uuid.return_value = expr_id

        expression = "test expression"
        definition = "test definition"
        translation = "test translation"
        example = "test example"
        tag_name_1 = "test-tag-1"
        tag_name_2 = "test-tag-2"

        user_props = {"nativeLang": "uk"}

        user = get_user(self.user_id, properties=user_props)
        tag_1 = get_tag("test_tag_id_1", tag_name=tag_name_1)
        tag_2 = get_tag("test_tag_id_2", tag_name=tag_name_2)

        self.mock_get_user.return_value = user
        self.mock_get_tag.side_effect = [tag_1, tag_2]

        self.subject.post_expression(
            expression,
            definition,
            translation,
            example,
            [tag_name_1, tag_name_2],
        )

        self.mock_get_user.assert_called_once_with(self.user_id)
        self.mock_get_tag.assert_has_calls(
            [call(tag_name_1), call(tag_name_2)]
        )
        self.mock_refresh_llist.assert_called_once_with()

        actual = self.mock_post.call_args.args[0]

        self.assertEqual(user, actual.user)
        self.assertEqual(1, actual.active)
        self.assertEqual(added, actual.added)
        self.assertEqual(added, actual.updated)

        self.assertEqual(expr_id, actual.expression.id)
        self.assertEqual(expression, actual.expression.expression)
        self.assertEqual(definition, actual.expression.definition)
        self.assertEqual({"uk": translation}, actual.expression.translations)
        self.assertEqual(example, actual.expression.example)
        self.assertEqual(added, actual.expression.added)
        self.assertEqual(added, actual.expression.updated)
        self.assertEqual([tag_1, tag_2], actual.expression.tags)

    def test_post_user_not_found_rises_exception(self):
        self.mock_get_user.return_value = None

        with self.assertRaises(UserNotFoundException):
            self.subject.post_expression("1", "2", "3", "4", ["5"])

        self.mock_get_user.assert_called_once_with(self.user_id)
        self.mock_get_tag.assert_not_called()
        self.mock_post.assert_not_called()
        self.mock_refresh_llist.assert_not_called()

    def test_post_tag_not_found_rises_exception(self):
        self.mock_get_user.return_value = get_user(self.user_id)
        self.mock_get_tag.return_value = None

        with self.assertRaises(TagNotFoundException):
            self.subject.post_expression("1", "2", "3", "4", ["5"])

        self.mock_get_user.assert_called_once_with(self.user_id)
        self.mock_get_tag.assert_called_once_with("5")
        self.mock_post.assert_not_called()
        self.mock_refresh_llist.assert_not_called()

    def test_empty_tags_list_rises_exception(self):
        self.mock_get_user.return_value = get_user(self.user_id)

        with self.assertRaises(InvalidPostUserExpressionDataException):
            self.subject.post_expression("1", "2", "3", "4", [])

        self.mock_get_user.assert_called_once_with(self.user_id)
        self.mock_get_tag.assert_not_called()
        self.mock_post.assert_not_called()
        self.mock_refresh_llist.assert_not_called()


class GetExpressionByIDTests(TestCase):
    def setUp(self):
        self.user_id = "test_user_id"

        user_expr_repo_patcher = patch(
            "services.user_expression_service.UserExpressionsRepo"
        )
        mock_ue_repo = user_expr_repo_patcher.start()
        self.mock_get_us_expr_by_id = mock_ue_repo.return_value.get_by_id
        self.addCleanup(user_expr_repo_patcher.stop)

        self.subject = UserExpressionService(self.user_id)

    def test_get_user_expression_by_id(self):
        expression_id = "test_expression_id"
        expression = "test expression"
        definition = "test definition"
        translation = "test translation"
        tag = "test tag"

        user_props = {
            "nativeLang": "uk",
        }
        user = get_user(self.user_id, properties=user_props)
        self.mock_get_us_expr_by_id.return_value = get_user_expression(
            user_id=self.user_id,
            user=user,
            expression=get_expression(
                "expr_id_1",
                expression,
                definition=definition,
                translations={"uk": translation},
                tags=[get_tag("tag_id", tag)],
            ),
        )
        actual = self.subject.get_expression_by_id(expression_id)
        expected = {
            "expression": expression,
            "definition": definition,
            "translation": translation,
            "tags": [tag],
            "examples": [],
        }

        self.assertEqual(expected, actual)

        self.mock_get_us_expr_by_id.assert_called_once_with(expression_id)

    def test_get_user_expression_by_id_not_found_raise_exception(self):
        self.mock_get_us_expr_by_id.return_value = None

        with self.assertRaises(UserExpressionNotFoundException):
            self.subject.get_expression_by_id("id")


class GetAllTests(TestCase):
    def setUp(self):
        self.user_id = "test_user_id"

        user_expr_repo_patcher = patch(
            "services.user_expression_service.UserExpressionsRepo"
        )
        mock_ue_repo = user_expr_repo_patcher.start()
        self.mock_get = mock_ue_repo.return_value.get
        self.mock_search = mock_ue_repo.return_value.search
        self.mock_post = mock_ue_repo.return_value.post
        self.mock_get_us_expr_by_id = mock_ue_repo.return_value.get_by_id
        self.mock_count = mock_ue_repo.return_value.count
        self.addCleanup(user_expr_repo_patcher.stop)

        daily_training_patcher = patch(
            "services.user_expression_service.DailyTraining"
        )
        mock_daily_training = daily_training_patcher.start()
        self.mock_refresh_llist = (
            mock_daily_training.return_value.refresh_learning_list
        )
        self.mock_is_in_llist = (
            mock_daily_training.return_value.is_expression_in_learn_list
        )
        self.addCleanup(daily_training_patcher.stop)

        user_repo_patcher = patch("services.user_expression_service.UsersDAO")
        self.mock_get_user = user_repo_patcher.start().return_value.get_by_id
        self.addCleanup(user_repo_patcher.stop)

        tag_repo_patcher = patch("services.user_expression_service.TagsRepo")
        self.mock_get_tag = tag_repo_patcher.start().return_value.get_by_name
        self.addCleanup(tag_repo_patcher.stop)

        self.subject = UserExpressionService(self.user_id)

    def test_get_all(self):
        user = get_user(self.user_id)

        expr_id_1 = "test_expr_id_1"
        expr_1 = "test_expression_1"
        know_level_1 = 0.91
        pract_count_1 = 1
        last_pract_time_1 = "2023-04-13 10:10:25"
        is_in_llist_1 = True

        expr_id_2 = "test_expr_id_2"
        expr_2 = "test_expression_2"
        know_level_2 = 0.92
        pract_count_2 = 2
        last_pract_time_2 = "2023-04-14 10:10:25"
        is_in_llist_2 = False

        expr_id_3 = "test_expr_id_3"
        expr_3 = "test_expression_3"
        know_level_3 = 0.93
        pract_count_3 = 3
        last_pract_time_3 = "2023-04-15 10:10:25"
        is_in_llist_3 = True

        self.mock_get.return_value = [
            get_user_expression(
                user_id=self.user_id,
                user=user,
                expression=get_expression(expr_id_1, expr_1),
                kl=know_level_1,
                pc=pract_count_1,
                lpt=last_pract_time_1,
            ),
            get_user_expression(
                user_id=self.user_id,
                user=user,
                expression=get_expression(expr_id_2, expr_2),
                kl=know_level_2,
                pc=pract_count_2,
                lpt=last_pract_time_2,
            ),
            get_user_expression(
                user_id=self.user_id,
                user=user,
                expression=get_expression(expr_id_3, expr_3),
                kl=know_level_3,
                pc=pract_count_3,
                lpt=last_pract_time_3,
            ),
        ]
        self.mock_is_in_llist.side_effect = [True, False, True]

        actual = self.subject.get_all()
        expected = [
            {
                "expressionId": expr_id_1,
                "expression": expr_1,
                "knowledgeLevel": know_level_1,
                "practiceCount": pract_count_1,
                "lastPracticeTime": last_pract_time_1,
                "isInLearnList": is_in_llist_1,
            },
            {
                "expressionId": expr_id_2,
                "expression": expr_2,
                "knowledgeLevel": know_level_2,
                "practiceCount": pract_count_2,
                "lastPracticeTime": last_pract_time_2,
                "isInLearnList": is_in_llist_2,
            },
            {
                "expressionId": expr_id_3,
                "expression": expr_3,
                "knowledgeLevel": know_level_3,
                "practiceCount": pract_count_3,
                "lastPracticeTime": last_pract_time_3,
                "isInLearnList": is_in_llist_3,
            },
        ]

        self.assertEqual(expected, actual)

        self.mock_get.assert_called_once_with()

    def test_get_all_no_results(self):
        self.mock_get.return_value = []

        actual = self.subject.get_all()

        self.assertEqual([], actual)
        self.mock_get.assert_called_once_with()


class CountTests(TestCase):
    def setUp(self):
        self.user_id = "test_user_id"

        user_expr_repo_patcher = patch(
            "services.user_expression_service.UserExpressionsRepo"
        )
        mock_ue_repo = user_expr_repo_patcher.start()
        self.mock_count = mock_ue_repo.return_value.count
        self.addCleanup(user_expr_repo_patcher.stop)

        self.subject = UserExpressionService(self.user_id)

    def test_count_user_expressions(self):
        expected = 10
        self.mock_count.return_value = expected

        actual = self.subject.count_user_expressions()

        self.assertEqual(expected, actual)

        self.mock_count.assert_called_once_with()
