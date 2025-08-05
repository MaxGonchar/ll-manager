from typing import TypedDict
from repository.training_expressions_repo import TrainingRepoABC
from services.assistant import (
    ExpressionDetectionResponse,
    ExpressionUsageResponse,
    GeneralJudgementResponse,
    VeniceAssistant,
)


MAX_EXPRESSIONS_TO_TRAIN = 10


class WritingTrainingExpression(TypedDict):
    id: str
    expression: str
    definition: str
    status: str
    comment: str | None


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
        expressions = [
            item["expression"].expression
            for item in self.repo.get_next(MAX_EXPRESSIONS_TO_TRAIN)
        ]
        return {
            "expressions": [
                {
                    "id": expr["expression"].id,
                    "expression": expr["expression"].expression,
                    "definition": expr["expression"].definition,
                    "status": "not_checked",
                    "comment": None,
                }
                for expr in expressions
            ],
            "lastWriting": None,
        }

    def submit_writing(
        self, text: str, expressions_to_train_ids: list[str]
    ) -> DailyWritingData:
        data = {
            "expressions": [
                {
                    "id": "1",
                    "expression": "test expression 1",
                    "definition": "definition 1",
                    "status": "failed",
                    "comment": "This is a sample comment for expression 1.",
                },
                {
                    "id": "2",
                    "expression": "test expression 2",
                    "definition": "definition 2",
                    "status": "not_checked",
                },
            ],
            "lastWriting": {
                "userText": "This is a sample text for the last writing.",
                "comment": [
                    {
                        "problem": "test problem",
                        "explanation": "test explanation",
                        "solution": "test solution",
                    },
                    {
                        "problem": "another problem",
                        "explanation": "another explanation",
                        "solution": "another solution",
                    },
                ],
            },
        }
