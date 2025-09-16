from flask import (
    Blueprint,
    request,
    render_template,
    url_for,
    flash,
    redirect,
    g,
)

from constants import Role
from helpers.rbac_helper import role_required
from exercises.sentence_training_v2 import SentenceTraining
from repository.training_expressions_repo import DailyTrainingRepo

daily_sentence_training_bp = Blueprint(
    "daily_sentence_training", __name__, url_prefix="/daily-sentence-training"
)


def _init_sentence_training(user_id: str):
    return SentenceTraining(DailyTrainingRepo(user_id))


@daily_sentence_training_bp.route("/", methods=["GET", "POST"])
def daily_sentence_training():
    role_required(
        [
            Role.SUPER_ADMIN.value,
            Role.ADMIN.value,
            Role.SELF_EDUCATED.value,
        ]
    )

    st = _init_sentence_training(g.user_id)

    if request.method == "GET":
        challenge = st.get_challenge()

        if challenge is None:
            flash("Nothing to recall")
            return redirect(url_for("user.index"))

        return render_template(
            "exercises/sentence_training_challenge.html",
            challenge=challenge,
            action=url_for("daily_sentence_training.daily_sentence_training"),
        )

    solution = st.submit_challenge(
        request.form["expression_id"],
        request.form["context_id"],
        request.form["answer"],
        request.form["hint"] == "true",
    )
    return render_template(
        "exercises/sentence_training_solution.html",
        solution=solution,
        action=url_for("daily_sentence_training.daily_sentence_training"),
    )
