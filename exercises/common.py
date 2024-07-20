from datetime import datetime
from typing import Optional, TypedDict

from models.models import Expression


class ChallengeDict(TypedDict):
    question: str
    tip: Optional[str]
    answer: str
    expression_id: str


class ChallengeSolutionDict(TypedDict):
    definition: str
    usersAnswer: str
    correctAnswer: str
    translation: Optional[str]
    example: str


class ExerciseExpressionsListItem(TypedDict):
    expression_id: str
    expression: str
    knowledge_level: float
    practice_count: int
    last_practice_time: Optional[datetime]


def get_challenge_object(expr: Expression) -> ChallengeDict:
    return {
        "answer": expr.expression,
        "expression_id": str(expr.id),
        "question": expr.definition,
        "tip": expr.expression,
    }


def get_challenge_solution_object(
    challenge_expr: Expression, user_answer: str
) -> ChallengeSolutionDict:
    return {
        "correctAnswer": challenge_expr.expression,
        "usersAnswer": user_answer,
        "definition": challenge_expr.definition,
        "translation": challenge_expr.translation("uk"),
        "example": challenge_expr.example,
    }


def get_exercise_expressions_list_item(
    expr_id: str,
    expression: str,
    knowledge_level: float,
    practice_count: int,
    last_practice_time: Optional[datetime],
) -> ExerciseExpressionsListItem:
    return {
        "expression_id": expr_id,
        "expression": expression,
        "knowledge_level": knowledge_level,
        "practice_count": practice_count,
        "last_practice_time": last_practice_time,
    }


def is_answer_correct(correct_answer: str, user_answer: str) -> bool:
    user_answer = " ".join([word.strip() for word in user_answer.split()])
    return user_answer.lower() == correct_answer.lower()


def calculate_knowledge_level(
    current_knowledge_level: float, practice_count: int, successful: bool
) -> float:
    success_score = 1 if successful else 0
    return ((current_knowledge_level * practice_count) + success_score) / (
        practice_count + 1
    )
