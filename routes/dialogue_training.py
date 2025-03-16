from flask import Blueprint, render_template, request, g, redirect, url_for

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
    dialogues = DialogueTraining(g.user_id).get_dialogues()
    return render_template(
        "exercises/dialogue_training_list.html",
        dialogues=dialogues,
    )


@dialogue_training_bp.route("/dialogues/<dialogue_id>/delete", methods=["GET"])
def delete_dialogue(dialogue_id):
    role_required(
        [
            Role.SUPER_ADMIN.value,
            Role.ADMIN.value,
            Role.SELF_EDUCATED.value,
        ]
    )
    DialogueTraining(g.user_id).delete_dialogue(dialogue_id)
    return redirect(url_for("dialogue_training.dialogues"))


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
            description=form.description.data
        )
        return redirect(url_for("dialogue_training.dialogue", dialogue_id=dialogue_id))

    return render_template("exercises/dialogue_training_new.html", form=form)


@dialogue_training_bp.route("/dialogues/<dialogue_id>", methods=["GET", "POST"])
def dialogue(dialogue_id):
    dialogue = DialogueTraining(g.user_id).get_dialogue(dialogue_id)
    if request.method == "GET":
        return render_template("exercises/dialogue_training.html", data=dialogue)
    
    dialogue = DialogueTraining(g.user_id).process_input(dialogue_id, request.form["input"])
    return render_template("exercises/dialogue_training.html", data=dialogue)
