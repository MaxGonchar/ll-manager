from flask import (
    Blueprint,
    g,
    render_template,
    request,
    flash,
    redirect,
    url_for,
)

from exercises.expression_recall import ExpressionRecall
from helpers.rbac_helper import role_required
from constants import Role

expression_recall_bp = Blueprint(
    "expression_recall", __name__, url_prefix="/exercise"
)


@expression_recall_bp.route("/expression_recall", methods=["GET", "POST"])
def expression_recall_challenge():
    role_required(
        [
            Role.SUPER_ADMIN.value,
            Role.ADMIN.value,
            Role.SELF_EDUCATED.value,
        ]
    )

    expr_recall = ExpressionRecall(g.user_id)

    if request.method == "GET":

        if not (challenge := expr_recall.get_challenge()):
            flash("Nosing to recall")
            return redirect(url_for("user.index"))

        return render_template(
            "exercises/expression_recall_challenge.html", challenge=challenge
        )

    expression_id = request.form["expression_id"]
    answer = request.form["answer"]
    hint = request.form["hint"] == "true"

    solution = expr_recall.submit_challenge(expression_id, answer, hint=hint)

    return render_template(
        "exercises/expression_recall_solution.html", solution=solution
    )


@expression_recall_bp.route("/expression_recall_expressions")
def expression_recall_expressions():
    role_required(
        [
            Role.SUPER_ADMIN.value,
            Role.ADMIN.value,
            Role.SELF_EDUCATED.value,
        ]
    )

    expr_recall = ExpressionRecall(g.user_id)
    return render_template(
        "exercises/expression_recall_expressions.html",
        exprs=expr_recall.get_expressions_needed_recalling(),
    )
