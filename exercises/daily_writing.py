from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TypedDict
from repository.training_expressions_repo import (
    TrainingRepoABC,
    UpdateTrainedExpression,
)
from services.assistant import (
    ExpressionDetectionRequest,
    ExpressionDetectionResponse,
    ExpressionUsageResponse,
    ExpressionUsageRequest,
    GeneralJudgementResponse,
    VeniceAssistant,
)
from models.models import UserExpression


MAX_EXPRESSIONS_TO_TRAIN = 10


class WritingTrainingExpression(TypedDict):
    id: str
    expression: str
    definition: str
    status: str
    comment: str | None
    pk: int #  practice count
    kl: float #  knowledge level


class WritingComment(TypedDict):
    problem: str
    explanation: str
    solution: str


class LastWritingData(TypedDict):
    userText: str
    comment: list[WritingComment] | None


class DailyWritingData(TypedDict):
    expressions: list[WritingTrainingExpression]
    lastWriting: LastWritingData | None


class DailyWriting:
    def __init__(
        self,
        user_id: str,
        training_repo: type[TrainingRepoABC],
        assistant: type[VeniceAssistant],
    ) -> None:
        self.repo = training_repo(user_id)
        self.assistant = assistant()

    def get_challenge(self) -> DailyWritingData:
        return {
            "expressions": [
                {
                    "id": item["expression"].expression.id,
                    "expression": item["expression"].expression.expression,
                    "definition": item["expression"].expression.definition,
                    "status": "not_checked",
                    "comment": None,
                    "pk": item["practiceCount"],
                    "kl": item["knowledgeLevel"],
                }
                for item in self.repo.get_next(MAX_EXPRESSIONS_TO_TRAIN)
            ],
            "lastWriting": None,
        }

    def submit_writing(
        self, text: str, expressions_to_train_ids: list[str]
    ) -> DailyWritingData:

        expressions_to_train = self.repo.get_by_ids(expressions_to_train_ids)
        expressions_to_detect = self._build_expressions_to_detect_message(
            expressions_to_train
        )
        (
            general_judgement,
            detected_expression_ids,
        ) = self._get_general_judgement(text, expressions_to_detect)

        judgments = []

        if detected_expression_ids.expressions:
            judgments = self._get_expression_usage_judgement(
                text,
                self._build_expression_usage_request(
                    expressions_to_train, detected_expression_ids.expressions
                ),
            )

            self.repo.update_expressions(
                self._get_trined_expressions_to_update(
                    expressions_to_train, judgments
                )
            )

        data: DailyWritingData = {
            "expressions": [
                {
                    "id": item["expression"].expression.id,
                    "expression": item["expression"].expression.expression,
                    "definition": item["expression"].expression.definition,
                    "status": "not_checked",
                    "comment": None,
                    "pk": item["practiceCount"],
                    "kl": item["knowledgeLevel"],
                }
                for item in self.repo.get_next(MAX_EXPRESSIONS_TO_TRAIN)
            ],
            "lastWriting": {
                "userText": text,
                "comment": [
                    {
                        "problem": item.problem,
                        "explanation": item.explanation,
                        "solution": item.solution,
                    }
                    for item in general_judgement.problems
                    if item.problem not in ("None", "")
                ],
            },
        }

        if judgments:
            judgments_data = {item.id: item for item in judgments}

            for expr in data["expressions"]:
                if expr["id"] in judgments_data:
                    expr["status"] = (
                        "success"
                        if judgments_data[expr["id"]].is_correct
                        else "failed"
                    )
                    expr["comment"] = judgments_data[expr["id"]].comment

        return data

    def _get_general_judgement(
        self,
        text: str,
        expressions_to_detect: list[ExpressionDetectionRequest],
    ):
        with ThreadPoolExecutor() as executor:
            future_general_judgement = executor.submit(
                self.assistant.get_general_judgement, text
            )
            future_detected_expression_ids = executor.submit(
                self.assistant.detect_phrases_usage,
                text,
                expressions_to_detect,
            )
            general_judgement = future_general_judgement.result()
            detected_expression_ids = future_detected_expression_ids.result()

        return general_judgement, detected_expression_ids

    @staticmethod
    def _build_expressions_to_detect_message(
        user_expressions: list[UserExpression],
    ) -> list[ExpressionDetectionRequest]:
        return [
            {
                "id": user_expr.expression_id,
                "expression": user_expr.expression.expression,
            }
            for user_expr in user_expressions
        ]

    def _get_expression_usage_judgement(
        self,
        text: str,
        expressions_usage_requests: list[ExpressionUsageRequest],
    ) -> list[ExpressionUsageResponse]:
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(
                    self.assistant.get_expression_usage_judgement,
                    text,
                    expression_usage_request,
                )
                for expression_usage_request in expressions_usage_requests
            ]
            judgments = [future.result() for future in as_completed(futures)]
        return judgments

    def _build_expression_usage_request(
        self,
        user_expressions: list[UserExpression],
        expressions_ids: list[str],
    ) -> list[ExpressionUsageRequest]:
        return [
            {
                "id": user_expr.expression_id,
                "expression": user_expr.expression.expression,
                "meaning": user_expr.expression.definition,
            }
            for user_expr in user_expressions
            if str(user_expr.expression_id) in expressions_ids
        ]

    def _get_trined_expressions_to_update(
        self,
        expressions_to_train: list[UserExpression],
        judgments: list[ExpressionUsageResponse],
    ) -> list[UpdateTrainedExpression]:
        trained_expressions_data = {
            item.id: item.is_correct for item in judgments
        }
        expressions_to_update = []
        for expr in expressions_to_train:
            if expr.expression_id in trained_expressions_data:
                expressions_to_update.append(
                    {
                        "user_expression": expr,
                        "is_trained_successfully": trained_expressions_data[
                            expr.expression_id
                        ],
                    }
                )
        return expressions_to_update
