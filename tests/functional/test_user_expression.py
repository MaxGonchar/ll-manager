from tests.functional.utils import FunctionalTestsHelper


class AddUserExpressionTest(FunctionalTestsHelper):
    def setUp(self):
        super().setUp()

        with open(
            "tests/functional/data/setup_test_user_expression.sql", "r"
        ) as file:
            sql = file.read()

        self._setup_test_db(sql)

        self.user_id = "04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef"
        session = {
            "user": "daily_training@test.mail",
            "user_id": self.user_id,
        }
        self._set_session(**session)

    def test_expression_get(self):
        context = self._get_test_template_context(
            "GET",
            "expressions/expression.html",
            "/user/expressions/4d7993aa-d897-4647-994b-e0625c88f349",
        )

        expression = context["expression"]
        self.assertEqual("preceding", expression["expression"])
        self.assertEqual(
            "coming before something in order, position, or time",
            expression["definition"],
        )
        self.assertEqual("попередній", expression["translation"])
        self.assertEqual([], expression["tags"])

    def test_expression_get_no_translation(self):
        context = self._get_test_template_context(
            "GET",
            "expressions/expression.html",
            "/user/expressions/542d93d5-6a38-4ce6-95ba-de942ad3b309",
        )

        expression = context["expression"]
        self.assertEqual(
            "go away from terrible school", expression["expression"]
        )
        self.assertEqual(
            "go away from terrible school definition",
            expression["definition"],
        )
        self.assertEqual("no translation", expression["translation"])
        self.assertEqual([], expression["tags"])
