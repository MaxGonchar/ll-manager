from flask import Blueprint, render_template, g

from services.user_expression_service import UserExpressionService
from exercises.daily_training_v2 import DailyTraining
from exercises.expression_recall import ExpressionRecall
from exercises.sentence_training import SentenceTraining
from helpers.rbac_helper import role_required
from constants import Role

user_bp = Blueprint("user", __name__, url_prefix="/")


@user_bp.route("")
def index():
    role_required(
        [
            Role.SUPER_ADMIN.value,
            Role.ADMIN.value,
            Role.SELF_EDUCATED.value,
        ]
    )

    user_id = g.user_id
    exprs = {
        "dailyTrainingExpressionsNumber": DailyTraining(
            user_id
        ).count_learn_list_items(),
        "totalExpressions": UserExpressionService(
            user_id
        ).count_user_expressions(),
        "recallExpressionsNumber": ExpressionRecall(
            user_id
        ).get_number_of_expressions_needed_recalling(),
        "sentenceTrainingExpressionsNumber": SentenceTraining(
            user_id
        ).get_expressions_number_can_be_trained_in_sentence(),
    }
    return render_template("user/index.html", exprs=exprs)
