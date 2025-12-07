import json
from dotenv import dotenv_values

from common.utils import get_connection

USER_ID = "b5f55871-4a7d-4c27-aaa5-e3542d8554a7"
CONFIGS = dotenv_values(".env.prod")
# USER_ID = "9c9e7618-8d4a-4de5-8d6b-b5aa5d71549e"
# CONFIGS = dotenv_values(".env.dev")


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
    print(f"{'|i':<4} {'|pk':<5} {'|lp':<5} {'|kl':<5} {'|expr'}")
    print("-" * 40)

    for i, item in enumerate(ll_list):
        pk = item["practiceCount"]
        pk_display = str(pk)
        
        if int(pk) == 79:
            pk_display = "\033[92m79\033[0m"
        elif int(pk) == 78:
            pk_display = "\033[93m78\033[0m"
        
        if int(pk) in [78, 79]:
            pk_formatted = pk_display + "  "
        else:
            pk_formatted = f"{pk_display:<4}"
        
        print(
            (
                f"|{i:<3} "
                f"|{pk_formatted} "
                f"|{item['position']:<4} "
                f"|{int(item['knowledgeLevel'] * 100):<4} "
                f"|{get_expression(item['expressionId'])}"
            )
        )


def main():
    props = get_properties(USER_ID)[0]
    ll_list = get_ll_list(props)
    print_ll_list(ll_list)


if __name__ == "__main__":
    main()
