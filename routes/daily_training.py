from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    g,
)

from constants import MessageStatus, Role
from exercises.daily_training_v2 import (
    DailyTraining,
    LearnListItemNotFoundExpression,
)
from forms.daily_training_forms import DailyTrainingSettingsForm
from helpers.rbac_helper import role_required
from helpers.ff_helper import is_feature_flag_enabled

exercise_bp = Blueprint("exercise", __name__, url_prefix="/exercise")


def _init_daily_training(user_id: str):
    from exercises.daily_training_v3 import DailyTraining
    from repository.training_expressions_repo import DailyTrainingRepo

    return DailyTraining(DailyTrainingRepo(user_id))


@exercise_bp.route("/daily-training", methods=["GET", "POST"])
def daily_training_challenge():
    role_required(
        [
            Role.SUPER_ADMIN.value,
            Role.ADMIN.value,
            Role.SELF_EDUCATED.value,
        ]
    )

    dt = (
        _init_daily_training(g.user_id)
        if is_feature_flag_enabled("DAILY_TRAINING_V3")
        else DailyTraining(g.user_id)
    )

    if request.method == "GET":
        challenge = dt.get_challenge()

        if challenge is None:
            flash("Nosing to test")
            return redirect(url_for("user.index"))

        return render_template(
            "exercises/daily_training_challenge.html",
            challenge=challenge,
        )

    expression_id = request.form["expression_id"]
    answer = request.form["answer"]
    hint = request.form["hint"] == "true"

    solution = dt.submit_challenge(expression_id, answer, hint=hint)

    return render_template(
        "exercises/daily_training_solution.html", solution=solution
    )


@exercise_bp.route("/daily-training-expressions", methods=["GET"])
def daily_training_expressions():
    role_required(
        [
            Role.SUPER_ADMIN.value,
            Role.ADMIN.value,
            Role.SELF_EDUCATED.value,
        ]
    )

    d_training = (
        _init_daily_training(g.user_id)
        if is_feature_flag_enabled("DAILY_TRAINING_V3")
        else DailyTraining(g.user_id)
    )

    exprs = d_training.get_learn_list_expressions()
    return render_template(
        "exercises/daily_training_expressions.html", exprs=exprs
    )


@exercise_bp.route("<string:expression_id>/delete", methods=["GET"])
def remove_from_daily_training(expression_id: str):
    role_required(
        [
            Role.SUPER_ADMIN.value,
            Role.ADMIN.value,
            Role.SELF_EDUCATED.value,
        ]
    )

    d_training = (
        _init_daily_training(g.user_id)
        if is_feature_flag_enabled("DAILY_TRAINING_V3")
        else DailyTraining(g.user_id)
    )

    try:
        d_training.remove_item_from_learn_list(expression_id)
    except LearnListItemNotFoundExpression:
        pass

    return redirect(url_for("exercise.daily_training_expressions"))


@exercise_bp.route("settings", methods=["GET", "POST"])
def settings():
    role_required(
        [
            Role.SUPER_ADMIN.value,
            Role.ADMIN.value,
            Role.SELF_EDUCATED.value,
        ]
    )

    d_training = (
        _init_daily_training(g.user_id)
        if is_feature_flag_enabled("DAILY_TRAINING_V3")
        else DailyTraining(g.user_id)
    )
    form = DailyTrainingSettingsForm()

    if form.validate_on_submit():
        d_training.update_settings(
            form.llist_size.data,  # type: ignore
            form.practice_count_threshold.data,  # type: ignore
            form.knowledge_level_threshold.data / 100,  # type: ignore
        )
        d_training.refresh_learning_list()
        flash("Updated", MessageStatus.SUCCESS.value)
        return redirect(url_for("exercise.settings"))

    form.llist_size.data = d_training.dt_data.max_llist_size
    form.practice_count_threshold.data = (
        d_training.dt_data.practice_count_threshold
    )
    form.knowledge_level_threshold.data = int(
        d_training.dt_data.knowledge_level_threshold * 100
    )

    return render_template("exercises/daily_training_settings.html", form=form)
