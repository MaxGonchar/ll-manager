from typing import List
from http import HTTPStatus
from flask import g, abort, request
import logging
import os


def role_required(roles: List[str]):
    user_role = g.user_role
    if user_role not in roles:
        user_id = g.user_id
        path = request.path
        method = request.method

        if os.getenv("LL_TESTING") != "1":
            logging.warning(
                f"ACCESS FORBIDDEN. {user_id=}, {user_role=}, {path=}, {method=}"
            )

        abort(HTTPStatus.FORBIDDEN.value)
