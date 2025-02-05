from flask import Blueprint, render_template

dialogue_training_bp = Blueprint("dialogue_training", __name__, url_prefix="/exercise")


@dialogue_training_bp.route("/dialogues", methods=["GET"])
def dialogues():
    dialogues = [
        {"id": "123", "title": "Dialogue 1 qweqweqweqweqweqweqweqwe", "description": "This is a description"},
        {"id": "123", "title": "Dialogue 2 qweqweqweqweqweqweqweqwe", "description": "This is a description"},
        {"id": "123", "title": "Dialogue 3 qweqweqweqweqweqweqweqwe", "description": "This is a description"},
    ]
    return render_template(
        "exercises/dialogue_training_list.html",
        dialogues=dialogues,
    )
