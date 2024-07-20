from tests.functional.utils import FunctionalTestsHelper


class UserPageTest(FunctionalTestsHelper):
    def setUp(self):
        super().setUp()

        with open(
            "tests/functional/data/setup_test_user_expressions.sql", "r"
        ) as file:
            sql = file.read()

        self._setup_test_db(sql)

    def test_user_expressions_get(self):
        user_id = "04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef"
        session = {
            "user": "daily_training@test.mail",
            "user_id": user_id,
        }
        self._set_session(**session)

        context = self._get_test_template_context(
            "GET", "expressions/list.html", "/user/expressions"
        )
        context_expressions = [
            str(item["expressionId"]) for item in context["exprs"]
        ]

        expected_expressions = [
            "a0a68135-bc73-4025-a754-966450fa6cac",
            "4eb806c0-a8cd-4ac9-8387-1b79cb97b138",
            "24d96f68-46e1-4fb3-b300-81cd89cea435",
            "d5c26549-74f7-4930-9c2c-16d10d46e55e",
            "4d7993aa-d897-4647-994b-e0625c88f349",
            "b02dcda4-65ae-45ba-a2d7-0502fae3d08a",
            "eaf0a44f-abb2-4ddd-98d0-8944c163dae5",
            "542d93d5-6a38-4ce6-95ba-de942ad3b309",
        ]

        self.assertEqual(expected_expressions, context_expressions)

    def test_user_expressions_search(self):
        user_id = "04aa4f4e-a53e-4b6c-96c5-3604e3fcc4ef"
        session = {
            "user": "daily_training@test.mail",
            "user_id": user_id,
        }
        self._set_session(**session)

        body = {
            "action": "search",
        }

        cases = {
            "school go": [
                "b02dcda4-65ae-45ba-a2d7-0502fae3d08a",
                "542d93d5-6a38-4ce6-95ba-de942ad3b309",
            ],
            "go school": [
                "b02dcda4-65ae-45ba-a2d7-0502fae3d08a",
                "542d93d5-6a38-4ce6-95ba-de942ad3b309",
            ],
            "go": [
                "b02dcda4-65ae-45ba-a2d7-0502fae3d08a",
                "eaf0a44f-abb2-4ddd-98d0-8944c163dae5",
                "542d93d5-6a38-4ce6-95ba-de942ad3b309",
            ],
            "school": [
                "b02dcda4-65ae-45ba-a2d7-0502fae3d08a",
                "542d93d5-6a38-4ce6-95ba-de942ad3b309",
            ],
            "aboba": [],
        }
        for case, expected in cases.items():
            with self.subTest(case):
                body["query"] = case
                context = self._get_test_template_context(
                    "POST",
                    "expressions/list.html",
                    "/user/expressions",
                    data=body,
                )
                context_expressions = [
                    str(item["expressionId"]) for item in context["exprs"]
                ]
                self.assertEqual(expected, context_expressions, case)
