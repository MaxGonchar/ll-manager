from flask import Blueprint, request, g, render_template, redirect, url_for

from helpers.rbac_helper import role_required
from constants import Role
from exercises.writing_training import WritingTraining

writing_training_bp = Blueprint(
    "writing_training", __name__, url_prefix="/exercise/writing-training"
)


@writing_training_bp.route("/", methods=["GET", "POST"])
def writing_training():
    role_required(
        [
            Role.SUPER_ADMIN.value,
            Role.ADMIN.value,
            Role.SELF_EDUCATED.value,
        ]
    )
    writing_training = WritingTraining(g.user_id)
    data = writing_training.get_writings()

    if request.method == "POST":
        input_data = request.form["input"]
        writing_training.submit_writing(input_data)
        return redirect(url_for("writing_training.writing_training"))

    return render_template(
        "exercises/writing_training.html",
        data=data,
    )
