from tests.functional.utils import FunctionalTestsHelper


class UserPageTest(FunctionalTestsHelper):
    def setUp(self):
        super().setUp()

        with open("tests/functional/data/setup_test_user.sql", "r") as file:
            sql = file.read()

        self._setup_test_db(sql)

    def test_user_get(self):
        user_id = "04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef"
        session = {
            "user": "daily_training@test.mail",
            "user_id": user_id,
        }
        self._set_session(**session)

        context = self._get_test_template_context(
            "GET", "user/index.html", "/"
        )

        expected_context = {
            "dailyTrainingExpressionsNumber": 3,
            "totalExpressions": 5,
            "recallExpressionsNumber": 4,
            "sentenceTrainingExpressionsNumber": 0,
        }

        self.assertEqual(expected_context, context["exprs"])
