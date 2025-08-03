from flask import Blueprint, render_template, g

from helpers.ff_helper import is_feature_flag_enabled
from services.user_expression_service import UserExpressionService
from exercises.daily_training_v2 import DailyTraining
from exercises.expression_recall import ExpressionRecall
from exercises.sentence_training import SentenceTraining
from helpers.rbac_helper import role_required
from constants import Role

user_bp = Blueprint("user", __name__, url_prefix="/")


def _init_daily_training(user_id: str):
    from exercises.daily_training_v3 import DailyTraining
    from repository.training_expressions_repo import DailyTrainingRepo

    return DailyTraining(DailyTrainingRepo(user_id))


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
    dt = _init_daily_training(user_id)
    exprs = {
        "dailyTrainingExpressionsNumber": dt.count_learn_list_items(),
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
