import json
from typing import List, Optional
from datetime import datetime


def date_filter(date: Optional[datetime]) -> str:
    return date.strftime("%d/%m/%y") if date is not None else "-"


def knowledge_level_filter(knowledge_level):
    return int(knowledge_level * 100)


def expression_sentence(sentence: dict) -> str:
    return sentence["tpl"].format(
        *[
            '<span style="color: #40c057;">' + item + "</span>"
            for item in sentence["values"]
        ]
    )


def string_array(array: List[str]):
    return json.dumps(array).replace("'", r"\'")


def escape_double_quotas(string: str) -> str:
    return string.replace('"', r'\"')
