from http import HTTPStatus

from tests.functional.utils import FunctionalTestsHelper

SUPER_ADMIN = "super-admin"
ADMIN = "admin"
SELF_EDUCATED = "self-educated"
INVALID_ROLE = "invalid-role"

ALL_VALID_ROLES = (SUPER_ADMIN, ADMIN, SELF_EDUCATED)
ADMINS = (SUPER_ADMIN, ADMIN)

# print(app.url_map)
ROUTS = [
    # ('/static/<filename>', ("GET")),
    # ('/login', ("POST", "GET")),
    # ('/login/sign-on', ("POST", "GET")),
    # ('/login/logout', ("GET")),
    {
        "url": "/",
        "methods": [{"method": "GET", "allowed_roles": ALL_VALID_ROLES}],
    },
    {
        "url": "/exercise/daily-training",
        "methods": [
            {"method": "POST", "allowed_roles": ALL_VALID_ROLES},
            {"method": "GET", "allowed_roles": ALL_VALID_ROLES},
        ],
    },
    {
        "url": "/exercise/daily-training-expressions",
        "methods": [{"method": "GET", "allowed_roles": ALL_VALID_ROLES}],
    },
    {
        "url": "/exercise/<expression_id>/delete",
        "methods": [{"method": "GET", "allowed_roles": ALL_VALID_ROLES}],
    },
    {
        "url": "/exercise/settings",
        "methods": [
            {"method": "POST", "allowed_roles": ALL_VALID_ROLES},
            {"method": "GET", "allowed_roles": ALL_VALID_ROLES},
        ],
    },
    {
        "url": "/user/expressions",
        "methods": [
            {"method": "POST", "allowed_roles": ALL_VALID_ROLES},
            {"method": "GET", "allowed_roles": ALL_VALID_ROLES},
        ],
    },
    {
        "url": "/user/expressions/<expression_id>",
        "methods": [{"method": "GET", "allowed_roles": ALL_VALID_ROLES}],
    },
    {
        "url": "/user/expressions/<expression_id>",
        "methods": [{"method": "GET", "allowed_roles": ALL_VALID_ROLES}],
    },
    {
        "url": "/exercise/expression_recall",
        "methods": [
            {"method": "POST", "allowed_roles": ALL_VALID_ROLES},
            {"method": "GET", "allowed_roles": ALL_VALID_ROLES},
        ],
    },
    {
        "url": "/exercise/expression_recall_expressions",
        "methods": [{"method": "GET", "allowed_roles": ALL_VALID_ROLES}],
    },
    {
        "url": "/admin",
        "methods": [{"method": "GET", "allowed_roles": ADMINS}],
    },
    # {
    #     "url": "/admin/expressions/<expression_id>/sentences",
    #     "methods": [
    #         {"method": "GET", "allowed_roles": ADMINS},
    #         {"method": "POST", "allowed_roles": ADMINS},
    #     ],
    # },
    # ('/', ("GET")),
    # ('/admin', ("GET")),
    # ('/status', ("GET")),
    # ('/expressions', ("GET")),
    # ('/expressions/<expression_id>', ("POST", "GET")),
]

ROLES = {
    SUPER_ADMIN: "4d7993aa-d897-4647-994b-e0625c88f349",
    ADMIN: "aba08f26-174c-421f-87ea-033cb4104182",
    SELF_EDUCATED: "70f276b3-2cf6-4c85-9dd0-30f14b643ef6",
    INVALID_ROLE: "eed91f47-b411-4019-a5c9-748e16f947e4",
}


class RBACTests(FunctionalTestsHelper):
    def setUp(self):
        super().setUp()

        with open("tests/functional/data/setup_test_rbac.sql", "r") as file:
            sql = file.read()

        self._setup_test_db(sql)

    def test_rbac_forbidden(self):
        for patient in ROUTS:

            for method in patient["methods"]:
                forbidden_roles = set(ROLES.keys()) - set(
                    method["allowed_roles"]
                )

                for role in forbidden_roles:
                    with self.subTest(
                        role=role, method=method["method"], url=patient["url"]
                    ):
                        self._test_method(
                            patient["url"], method["method"], ROLES[role]
                        )

    def _test_method(self, url: str, method: str, role: str):
        self.test_session["user_id"] = role
        self._set_session(**self.test_session)

        if method == "GET":
            resp = self.client.get(url)
        elif method == "POST":
            resp = self.client.post(url)
        else:
            raise NotImplemented(
                f"{method} - {url} is not covered by rbac test"
            )

        self.assertEqual(HTTPStatus.FORBIDDEN.value, resp.status_code)
