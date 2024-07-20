from tests.functional.utils import FunctionalTestsHelper


class TestAdminIndex(FunctionalTestsHelper):
    def setUp(self):
        super().setUp()

        with open(
            "tests/functional/data/setup_test_admin_index.sql", "r"
        ) as file:
            sql = file.read()

        self._setup_test_db(sql)

    def test_get(self):
        user_id = "4d7993aa-d897-4647-994b-e0625c88f349"
        session = {
            "user": "admin@test.com",
            "user_id": user_id,
        }
        self._set_session(**session)

        self._get_test_template_context(
            "GET",
            "admin/index.html",
            "/admin",
        )
