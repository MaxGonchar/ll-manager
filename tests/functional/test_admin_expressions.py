from tests.functional.utils import FunctionalTestsHelper


class GetTests(FunctionalTestsHelper):
    def setUp(self):
        super().setUp()

        with open(
            "tests/functional/data/setup_test_admin_expressions.sql", "r"
        ) as file:
            sql = file.read()

        self._setup_test_db(sql)

    def test_get(self):
        user_id = "2f732f36-c0f4-430f-921d-b62877891c80"
        session = {
            "user": "admin@test.com",
            "user_id": user_id,
        }
        self._set_session(**session)

        context = self._get_test_template_context(
            "GET",
            "admin/expressions_list.html",
            "/admin/expressions",
        )

        expected_ids = [
            "d5c26549-74f7-4930-9c2c-16d10d46e55e",
            "24d96f68-46e1-4fb3-b300-81cd89cea435",
            "4d7993aa-d897-4647-994b-e0625c88f349",
            "542d93d5-6a38-4ce6-95ba-de942ad3b309",
            "53c2fc3c-0a99-477d-9feb-3a07792eaf86",
            "eaf0a44f-abb2-4ddd-98d0-8944c163dae5",
            "66c21b88-3e73-471a-9776-9b691978e650",
            "b02dcda4-65ae-45ba-a2d7-0502fae3d08a",
            "4eb806c0-a8cd-4ac9-8387-1b79cb97b138",
        ]
        actual_ids = [expr["id"] for expr in context["exprs"]]

        self.maxDiff = None
        self.assertEqual(expected_ids, actual_ids)


class SearchTests(FunctionalTestsHelper):
    def setUp(self):

        super().setUp()

        with open(
            "tests/functional/data/setup_test_admin_expressions.sql", "r"
        ) as file:
            sql = file.read()

        self._setup_test_db(sql)

    def test_search(self):
        user_id = "2f732f36-c0f4-430f-921d-b62877891c80"
        session = {
            "user": "admin@test.com",
            "user_id": user_id,
        }
        self._set_session(**session)

        body = {
            "action": "search",
        }

        cases = {
            "school go": [
                "542d93d5-6a38-4ce6-95ba-de942ad3b309",
                "66c21b88-3e73-471a-9776-9b691978e650",
                "b02dcda4-65ae-45ba-a2d7-0502fae3d08a",
            ],
            "go school": [
                "542d93d5-6a38-4ce6-95ba-de942ad3b309",
                "66c21b88-3e73-471a-9776-9b691978e650",
                "b02dcda4-65ae-45ba-a2d7-0502fae3d08a",
            ],
            "go": [
                "542d93d5-6a38-4ce6-95ba-de942ad3b309",
                "eaf0a44f-abb2-4ddd-98d0-8944c163dae5",
                "66c21b88-3e73-471a-9776-9b691978e650",
                "b02dcda4-65ae-45ba-a2d7-0502fae3d08a",
            ],
            "school": [
                "542d93d5-6a38-4ce6-95ba-de942ad3b309",
                "53c2fc3c-0a99-477d-9feb-3a07792eaf86",
                "66c21b88-3e73-471a-9776-9b691978e650",
                "b02dcda4-65ae-45ba-a2d7-0502fae3d08a",
            ],
            "aboba": [],
        }
        for case, expected in cases.items():
            with self.subTest(case):
                body["query"] = case
                context = self._get_test_template_context(
                    "POST",
                    "admin/expressions_list.html",
                    "/admin/expressions",
                    data=body,
                )
                context_expressions = [
                    str(item["id"]) for item in context["exprs"]
                ]
                self.assertEqual(expected, context_expressions, case)
