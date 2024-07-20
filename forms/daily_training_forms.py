from flask_wtf import FlaskForm
from wtforms import IntegerField
from wtforms.validators import NumberRange

from constants import (
    LLIST_SIZE_DESCRIPTION,
    PRACTICE_COUNT_THRESHOLD_DESCRIPTION,
    KNOWLEDGE_LEVEL_THRESHOLD_DESCRIPTION,
)


class DailyTrainingSettingsForm(FlaskForm):
    llist_size = IntegerField(
        "Learning list size",
        validators=[NumberRange(0, 150)],
        description=LLIST_SIZE_DESCRIPTION,
    )
    practice_count_threshold = IntegerField(
        "Practice count",
        validators=[NumberRange(1, 150)],
        description=PRACTICE_COUNT_THRESHOLD_DESCRIPTION,
    )
    knowledge_level_threshold = IntegerField(
        "Knowledge level",
        validators=[NumberRange(0, 100)],
        description=KNOWLEDGE_LEVEL_THRESHOLD_DESCRIPTION,
    )
