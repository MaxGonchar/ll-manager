from dotenv import dotenv_values
from psycopg2.extras import DictCursor

from common.utils import get_connection


def get_expression(config):
    sql = """
        SELECT
            e.expression,
            e.definition,
            t.tag
        FROM expressions e
        JOIN tag_expression te ON e.id=te.expression_id
        JOIN tags t ON te.tag_id=t.id
        JOIN user_expression ue ON e.id=ue.expression_id
        LEFT JOIN expression_context ec ON e.id=ec.expression_id
        WHERE ec.id IS NULL
        ORDER BY e.added DESC
        LIMIT 1
    """
    with get_connection(config).cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute(sql)
        expr = cursor.fetchone()
    return expr


def main():
    configs = dotenv_values(".env.prod")
    expr = get_expression(configs)
    template = f"""I have a {expr['tag']} "{expr['expression']}" meaning "{expr['definition']}"
Give me, please, 3 examples of usage in sentence for this expression
with translation to Ukrainian for each sentence (without transcription, only translation)
    """
    print(template)


if __name__ == "__main__":
    main()
