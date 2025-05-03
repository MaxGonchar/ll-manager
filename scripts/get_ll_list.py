import json
from dotenv import dotenv_values

from common.utils import get_connection

USER_ID = "b5f55871-4a7d-4c27-aaa5-e3542d8554a7"
CONFIGS = dotenv_values(".env.prod")


def get_properties(user_id):
    sql = """
        SELECT properties
        FROM users
        WHERE id=%(user_id)s
    """
    with get_connection(CONFIGS).cursor() as cursor:
        cursor.execute(sql, {"user_id": user_id})
        props = cursor.fetchone()
    return props


def get_expression(expr_id):
    sql = """
        SELECT expression
        FROM expressions
        WHERE id=%(expr_id)s
    """
    with get_connection(CONFIGS).cursor() as cursor:
        cursor.execute(sql, {"expr_id": expr_id})
        expr = cursor.fetchone()
    return expr[0]


def get_ll_list(props):
    return props["challenges"]["dailyTraining"]["learning_list"]


def print_ll_list(ll_list):
    for item in ll_list:
        print(
            item["practiceCount"],
            item["position"],
            get_expression(item["expressionId"]),
        )


def main():
    props = get_properties(USER_ID)[0]
    ll_list = get_ll_list(props)
    print_ll_list(ll_list)


if __name__ == "__main__":
    main()
