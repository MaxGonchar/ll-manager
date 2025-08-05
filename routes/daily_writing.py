from flask import Blueprint, render_template, request, g

from helpers.rbac_helper import role_required
from constants import Role

daily_writing_bp = Blueprint(
    "daily_writing", __name__, url_prefix="/daily-writing"
)


@daily_writing_bp.route("/", methods=["GET", "POST"])
def daily_writing():
    role_required(
        [
            Role.SUPER_ADMIN.value,
            Role.ADMIN.value,
            Role.SELF_EDUCATED.value,
        ]
    )

    data = {
        "expressions": [
            {
                "id": "1",
                "expression": "test expression 1",
                "definition": "definition 1",
                "status": "failed",
                "comment": "This is a sample comment for expression 1.",
            },
            {
                "id": "2",
                "expression": "test expression 2",
                "definition": "definition 2",
                "status": "not_checked",
            },
        ],
        "lastWriting": {
            "userText": "This is a sample text for the last writing.",
            "comment": [
                {
                    "problem": "test problem",
                    "explanation": "test explanation",
                    "solution": "test solution",
                },
                {
                    "problem": "another problem",
                    "explanation": "another explanation",
                    "solution": "another solution",
                },
            ],
        },
    }

    return render_template("exercises/daily_writing.html", data=data)
