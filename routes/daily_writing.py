from flask import Blueprint, render_template, request, g

from helpers.rbac_helper import role_required
from constants import Role
from exercises.daily_writing import DailyWriting
from repository.training_expressions_repo import DailyTrainingRepo
from services.assistant import VeniceAssistant

daily_writing_bp = Blueprint(
    "daily_writing", __name__, url_prefix="/daily-writing"
)


def _init_daily_writing(user_id: str):
    return DailyWriting(user_id, DailyTrainingRepo, VeniceAssistant)


@daily_writing_bp.route("/", methods=["GET", "POST"])
def daily_writing():
    role_required(
        [
            Role.SUPER_ADMIN.value,
            Role.ADMIN.value,
            Role.SELF_EDUCATED.value,
        ]
    )

    dw = _init_daily_writing(g.user_id)

    if request.method == "POST":
        data = dw.submit_writing(
            request.form["input"], request.form.getlist("expression_ids")
        )
        return render_template("exercises/daily_writing.html", data=data)

    data = dw.get_challenge()
    return render_template("exercises/daily_writing.html", data=data)
