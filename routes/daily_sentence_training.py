from flask import Blueprint, request, render_template, url_for

from constants import Role
from helpers.rbac_helper import role_required

daily_sentence_training_bp = Blueprint(
    "daily_sentence_training", __name__, url_prefix="/daily-sentence-training"
)


@daily_sentence_training_bp.route("/", methods=["GET", "POST"])
def daily_sentence_training():
    role_required(
        [
            Role.SUPER_ADMIN.value,
            Role.ADMIN.value,
            Role.SELF_EDUCATED.value,
        ]
    )

    if request.method == "GET":
        challenge = {
            "expressionId": "98b002c9-28e1-4e0e-a44b-7245bd59ff45",
            "contextId": "5f86f0f8-f604-4471-af53-3b1642296133",
            "sentence": "I'll guess it.",
            "translation": "Я вгадаю.",
            "template": "I'll {} it.",
            "values": ["guess"],
            "practiceCount": 5,
            "knowledgeLevel": 2,
        }
        return render_template(
            "exercises/sentence_training_challenge.html",
            challenge=challenge,
            action=url_for("daily_sentence_training.daily_sentence_training"),
        )

    solution = {
        "correctAnswer": "I'll guess it.",
        "usersAnswer": "I'll guess it.",
        "translation": "Я вгадаю.",
    }
    return render_template(
        "exercises/sentence_training_solution.html",
        solution=solution,
        action=url_for("daily_sentence_training.daily_sentence_training"),
    )
