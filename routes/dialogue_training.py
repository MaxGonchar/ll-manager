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
    # MOCK DIALOGUES
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
def dialogue(dialogue_id):
    # MOCK DIALOGUE DATA
    dialogue = {
        "id": "123",
        "title": "Dialogue 1",
        "description": "This is a description",
        "dialogue": [
            {
                "id": 1,
                "author": "user",
                "text": "Hello, how are you? I want to know how are you doing today. This is a long message and I want to see how it will be displayed on the screen",
                "comment": "This is a comment, related to the user's message. It can be used to provide feedback or additional information. This is a comment, related to the user's message. It can be used to provide feedback or additional information. This is a comment, related to the user's message. It can be used to provide feedback or additional information. This is a comment, related to the user's message. It can be used to provide feedback or additional information. This is a comment, related to the user's message. It can be used to provide feedback or additional information.",
            },
            {
                "id": 2,
                "author": "assistant",
                "text": "I am fine, thank you. How can I help you? I can provide you with information about the weather, news, or answer your questions. I am fine, thank you. How can I help you? I can provide you with information about the weather, news, or answer your questions. I am fine, thank you. How can I help you? I can provide you with information about the weather, news, or answer your questions. I am fine, thank you. How can I help you? I can provide you with information about the weather, news, or answer your questions.",
            },
            {
                "id": 3,
                "author": "user",
                "text": "What is your name? I want to know your name and how can I call you in the future if I need help or have questions about something specific",
            },
            {
                "id": 4,
                "author": "assistant",
                "text": "My name is Assistant and I am here to help you. You can call me Assistant or ask me any questions you have. I am here to help you with anything you need. My name is Assistant and I am here to help you. You can call me Assistant or ask me any questions you have. I am here to help you with anything you need. My name is Assistant and I am here to help you. You can call me Assistant or ask me any questions you have. I am here to help you with anything you need.",
            },
            {
                "id": 5,
                "author": "user",
                "text": "Thank you for the information. I will keep it in mind and ask you if I need help in the future. Have a nice day!",
                "comment": "This is a comment, related to the user's message. It can be used to provide feedback or additional information. This is a comment, related to the user's message. It can be used to provide feedback or additional information. This is a comment, related to the user's message. It can be used to provide feedback or additional information. This is a comment, related to the user's message. It can be used to provide feedback or additional information. This is a comment, related to the user's message. It can be used to provide feedback or additional information. ###",
            },
            {
                "id": 6,
                "author": "assistant",
                "text": "You are welcome! Have a nice day too! If you have any questions or need help, feel free to ask me. I am here to help you with anything you need. You are welcome! Have a nice day too! If you have any questions or need help, feel free to ask me. I am here to help you with anything you need. You are welcome! Have a nice day too! If you have any questions or need help, feel free to ask me. I am here to help you with anything you need.",
            },
            {
                "id": 7,
                "author": "user",
                "text": "Ok let's talk about something else. I want to know more about the weather in my city. Can you provide me with information about the weather?",
                "comment": "This is a comment, related to the user's message. It can be used to provide feedback or additional information. This is a comment, related to the user's message. It can be used to provide feedback or additional information. This is a comment, related to the user's message. It can be used to provide feedback or additional information. This is a comment, related to the user's message. It can be used to provide feedback or additional information. This is a comment, related to the user's message. It can be used to provide feedback or additional information. ***",
            },
            {
                "id": 8,
                "author": "assistant",
                "text": "Sure! I can provide you with information about the weather in your city. Please tell me the name of your city and I will check the weather forecast for you. Sure! I can provide you with information about the weather in your city. Please tell me the name of your city and I will check the weather forecast for you. Sure! I can provide you with information about the weather in your city. Please tell me the name of your city and I will check the weather forecast for you. Sure! I can provide you with information about the weather in your city. Please tell me the name of your city and I will check the weather forecast for you.",
            },
        ],
        "expressions": [
            {
                "id": 1,
                "expression": "Hello",
                "definition": "Greeting",
                "status": "failed",
                "comment": "This is a comment"
            },
            {
                "id": 2,
                "expression": "as if",
                "definition": "Expression of doubt",
                "status": "not_checked",
            },
            {
                "id": 3,
                "expression": "as if not",
                "definition": "Expression of doubt",
                "status": "failed",
                "comment": "This is a big comment describing the reason why the expression is failed and what should be done to improve it"
            },
            {
                "id": 4,
                "expression": "rain of cats and dogs",
                "definition": "Heavy rain with big drops",
                "status": "not_checked",
            },
            {
                "id": 5,
                "expression": "attractive",
                "definition": "Pleasant to look at",
                "status": "not_checked",
            }
        ]
    }
    if request.method == "GET":
        return render_template("exercises/dialogue_training.html", data=dialogue)
    
    print(request.form["input"])
    # print(list(request.form.keys()))
    return render_template("exercises/dialogue_training.html", data=dialogue)
