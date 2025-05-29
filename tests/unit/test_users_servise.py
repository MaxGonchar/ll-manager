from unittest import TestCase
from unittest.mock import patch

from tests.unit.fixtures import get_user
from services.users_service import UsersService
from services.exceptions import (
    UserNotFoundException,
    PasswordDoesntMatchException,
)


class CreateUsersTests(TestCase):
    def setUp(self):
        self.email = "test_email"
        self.psw = "test_psw"
        self.first = "test_first"
        self.last = "test_last"

        user_repo_patcher = patch("services.users_service.UsersDAO")
        self.mock_post = user_repo_patcher.start().return_value.post
        self.addCleanup(user_repo_patcher.stop)

        self.subject = UsersService()

    def test_create(self):
        self.subject.create_user(self.email, self.psw, self.first, self.last)

        actual = self.mock_post.call_args.args[0]
        expected_properties = {
            "nativeLang": "uk",
            "challenges": {
                "dailyTraining": {
                    "learnListSize": 50,
                    "practiceCountThreshold": 50,
                    "knowledgeLevelThreshold": 0.9,
                    "learning_list": [],
                }
            },
        }

        self.assertEqual(self.email, actual.email)
        self.assertEqual(self.first, actual.first)
        self.assertEqual(self.last, actual.last)
        self.assertEqual(
            "76baa771668f3d1c6c6f1060f1236acaa709236cb0e95a4e0d8b967bc1104819",
            actual.password_hash,
        )
        self.assertEqual("self-educated", actual.role)
        self.assertEqual(expected_properties, actual.properties)
        self.assertIsNotNone(actual.added)
        self.assertIsNotNone(actual.updated)
        self.assertIsNotNone(actual.last_login)
        self.assertIsNotNone(actual.id)


class LoginTests(TestCase):
    def setUp(self):
        self.user_id = "test_user_id"
        self.email = "test@user.email"
        self.role = "self-educated"
        self.psw = "test-psw"

        self.user = get_user(
            user_id=self.user_id,
            first="first",
            last="last",
            email=self.email,
            password_hash="7c9124321b7c84c74e95c3cfd598b6f9eb71a950c141bc39848dafe846eb8628",
        )

        user_repo_patcher = patch("services.users_service.UsersDAO")
        mock_user_repo = user_repo_patcher.start()
        self.mock_get = mock_user_repo.return_value.get_by_email
        self.mock_get.return_value = self.user
        self.mock_post = mock_user_repo.return_value.post
        self.addCleanup(user_repo_patcher.stop)

        self.subject = UsersService()

    @patch("services.users_service.get_current_utc_time")
    def test_login_success(self, mock_get_time):
        expected_last_login_time = "2024-01-06 15:02:15"
        mock_get_time.return_value = expected_last_login_time

        actual = self.subject.login(self.email, self.psw)

        self.assertEqual(self.user, actual)

        self.mock_get.assert_called_once_with(self.email)
        updated_ser = self.mock_post.call_args.args[0]

        self.assertEqual(updated_ser, self.user)
        self.assertEqual(expected_last_login_time, updated_ser.last_login)

    def test_login_user_not_found_rises_exception(self):
        email = "nit@existing.email"
        self.mock_get.return_value = None

        with self.assertRaises(UserNotFoundException):
            self.subject.login(email, self.psw)

        self.mock_get.assert_called_once_with(email)

    def test_login_psw_doesnt_match_raises_exception(self):
        psw = "wrong-psw"

        with self.assertRaises(PasswordDoesntMatchException):
            self.subject.login(self.email, psw)

        self.mock_get.assert_called_once_with(self.email)
