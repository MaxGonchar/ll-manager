from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    g,
)

from forms.expression_forms import PostExpressionForm
from helpers.ff_helper import is_feature_flag_enabled
from services.user_expression_service import UserExpressionService
from services.tags_service import TagsService
from exercises.daily_training_v2 import DailyTraining
from constants import GrammarTag, Role
from helpers.rbac_helper import role_required

expressions_bp = Blueprint(
    "expressions", __name__, url_prefix="/user/expressions"
)


def _init_daily_training(user_id: str):
    from exercises.daily_training_v3 import DailyTraining
    from repository.training_expressions_repo import DailyTrainingRepo

    return DailyTraining(DailyTrainingRepo(user_id))


# TO IMPROVE: add pagination
@expressions_bp.route("", methods=["GET", "POST"])
def user_expressions():
    role_required(
        [
            Role.SUPER_ADMIN.value,
            Role.ADMIN.value,
            Role.SELF_EDUCATED.value,
        ]
    )

    query_expression = ""
    ue_sv = UserExpressionService(g.user_id)

    if request.method == "GET":
        exprs = ue_sv.get_all()
        return render_template(
            "expressions/list.html",
            exprs=exprs,
            query_expression=query_expression,
        )

    action = request.form["action"]
    query_expression = request.form["query"]

    exprs = []
    if action == "search":
        exprs = ue_sv.search(query_expression)

    if action == "add":
        return redirect(
            url_for("expressions.post_expression", expression=query_expression)
        )

    return render_template(
        "expressions/list.html", exprs=exprs, query_expression=query_expression
    )


@expressions_bp.route("/post/<string:expression>", methods=["GET", "POST"])
def post_expression(expression):
    role_required(
        [
            Role.SUPER_ADMIN.value,
            Role.ADMIN.value,
            Role.SELF_EDUCATED.value,
        ]
    )

    form = PostExpressionForm(TagsService().get_tag_names())

    if request.method == "GET":
        form.expression.data = expression

    if form.validate_on_submit():
        properties = {}

        if form.grammar.data and form.grammar_tag.data:

            if grammar_tag := GrammarTag.new_from_display(
                form.grammar_tag.data
            ):
                properties = {
                    "grammar": {grammar_tag.key: {"text": form.grammar.data}}
                }

        UserExpressionService(g.user_id).post_expression(
            expression=form.expression.data,  # type: ignore
            definition=form.definition.data,  # type: ignore
            translation=form.translation.data,  # type: ignore
            example=form.example.data,  # type: ignore
            tag_names=form.all_tags,  # type: ignore
            properties=properties,
        )

        return redirect(url_for("expressions.user_expressions"))

    return render_template("expressions/post.html", form=form)


@expressions_bp.route("<string:expression_id>", methods=["GET"])
def user_expression(expression_id: str):
    role_required(
        [
            Role.SUPER_ADMIN.value,
            Role.ADMIN.value,
            Role.SELF_EDUCATED.value,
        ]
    )

    expr = UserExpressionService(g.user_id).get_expression_by_id(expression_id)

    return render_template("expressions/expression.html", expression=expr)


@expressions_bp.route(
    "<string:expression_id>/add-to-daily-training", methods=["GET"]
)
def add_expression_to_daily_training(expression_id: str):
    role_required(
        [
            Role.SUPER_ADMIN.value,
            Role.ADMIN.value,
            Role.SELF_EDUCATED.value,
        ]
    )

    d_training = _init_daily_training(g.user_id)
    d_training.add_item_to_learn_list(expression_id)
    return redirect(url_for("expressions.user_expressions"))
