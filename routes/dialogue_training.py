from flask import Blueprint, render_template, request, g

from forms.dialogue_train_forms import DialogueCreateForm
from helpers.rbac_helper import role_required
from constants import Role
from exercises.dialogue_training import DialogueTraining

dialogue_training_bp = Blueprint("dialogue_training", __name__, url_prefix="/exercise")


@dialogue_training_bp.route("/dialogues", methods=["GET"])
def dialogues():
    role_required(
        [
            Role.SUPER_ADMIN.value,
            Role.ADMIN.value,
            Role.SELF_EDUCATED.value,
        ]
    )
    dialogues = [
        {"id": "123", "title": "Dialogue 1 qweqweqweqweqweqweqweqwe", "description": "This is a description"},
        {"id": "123", "title": "Dialogue 2 qweqweqweqweqweqweqweqwe", "description": "This is a description"},
        {"id": "123", "title": "Dialogue 3 qweqweqweqweqweqweqweqwe", "description": "This is a description"},
    ]
    return render_template(
        "exercises/dialogue_training_list.html",
        dialogues=dialogues,
    )


@dialogue_training_bp.route("/dialogues/new", methods=["GET", "POST"])
def dialogue_new():
    role_required(
        [
            Role.SUPER_ADMIN.value,
            Role.ADMIN.value,
            Role.SELF_EDUCATED.value,
        ]
    )
    form = DialogueCreateForm()

    if form.validate_on_submit():
        dialogue_id = DialogueTraining(g.user_id).create_dialogue(
            title=form.title.data,
            description=form.description
        )
        return render_template("PAGE FOR DIALOGUE")

    return render_template("exercises/dialogue_training_new.html", form=form)


@dialogue_training_bp.route("/dialogues/<dialogue_id>", methods=["GET", "POST"])
def dialogue():
    pass
