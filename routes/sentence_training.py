from flask import (
    Blueprint,
    render_template,
    request,
    g,
    flash,
    redirect,
    url_for,
)

from helpers.rbac_helper import role_required
from constants import Role
from exercises.sentence_training import SentenceTraining

sentence_training_bp = Blueprint(
    "sentence_training", __name__, url_prefix="/exercise"
)


# TODO: (NEXT ITERATION) if failed - force to retry; consider hint as failure
@sentence_training_bp.route("/sentence_training", methods=["GET", "POST"])
def sentence_training_challenge():
    role_required(
        [
            Role.SUPER_ADMIN.value,
            Role.ADMIN.value,
            Role.SELF_EDUCATED.value,
        ]
    )

    sentence_training = SentenceTraining(g.user_id)

    if request.method == "GET":
        if not (challenge := sentence_training.get_challenge()):
            flash("Nosing to recall")
            return redirect(url_for("user.index"))

        return render_template(
            "exercises/sentence_training_challenge.html", challenge=challenge
        )

    expression_id = request.form["expression_id"]
    context_id = request.form["context_id"]
    answer = request.form["answer"]
    hint = request.form["hint"] == "true"

    solution = sentence_training.submit_challenge(
        expression_id, context_id, answer, hint
    )

    return render_template(
        "exercises/sentence_training_solution.html", solution=solution
    )
