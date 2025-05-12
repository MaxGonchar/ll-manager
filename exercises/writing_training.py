from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TypedDict
from uuid import uuid4

from exercises.common import calculate_knowledge_level
from repository.writings_repo import WritingsRepo
from repository.user_expressions_repo import UserExpressionsRepo
from helpers.time_helpers import get_current_utc_time
from models.models import UserExpression, Writings
from services.assistant import (
    ExpressionDetectionResponse,
    ExpressionUsageResponse,
    GeneralJudgementResponse,
    VeniceAssistant,
)


class WritingChallenge(TypedDict):
    writings: list[dict]
    expressions: list[dict]


DEFAULT_PROPERTIES = {
    "maxExpressionsToTrain": 10,
    "maxWritingsToStore": 10,
}


class WritingTraining:
    def __init__(
        self,
        user_id: str,
        writings_repo: WritingsRepo = WritingsRepo,
        user_expr_repo: UserExpressionsRepo = UserExpressionsRepo,
        assistant: VeniceAssistant = VeniceAssistant,
    ):
        self.user_id = user_id
        self.writings_repo = writings_repo(self.user_id)
        self.user_expr_repo = user_expr_repo(self.user_id)
        self.assistant = assistant()

    # for now we store only one writing training per user
    def get_writings(self) -> WritingChallenge:
        writings = self.writings_repo.get() or self._create_writings()
        return self._generate_writing_challenge(writings)

    def submit_writing(self, text: str) -> WritingChallenge:
        writings = self.writings_repo.get()

        (
            general_judgement,
            detected_expression_ids,
        ) = self._get_general_judgement(
            text, self._build_expressions_to_detect_message(writings)
        )

        if detected_expression_ids.expressions:
            judgments = self._get_expression_usage_judgement(
                text,
                detected_expression_ids,
                writings,
            )
            user_expressions_to_update = self._user_expressions_to_update(
                judgments
            )
            writings = self._update_dialogue_expressions_status(
                writings,
                judgments,
            )
            self._update_user_expressions(
                judgments,
                user_expressions_to_update,
            )

        writings = self._enrich_expressions(writings)
        writings = self._update_dialogue_messages(
            writings, text, general_judgement
        )

        self.writings_repo.add(writings)

        return self._generate_writing_challenge(writings)

    def _update_dialogue_messages(
        self,
        writings: Writings,
        text: str,
        general_judgement: GeneralJudgementResponse,
    ) -> Writings:
        comment = [
            {
                "problem": item.problem,
                "explanation": item.explanation,
                "solution": item.solution,
            }
            for item in general_judgement.problems
            if item.problem not in ("None", "")
        ]
        writings.add_message(text, comment=comment)
        writings.updated = get_current_utc_time()

        return writings

    def _update_user_expressions(
        self,
        judgments: list[ExpressionUsageResponse],
        user_expressions_to_update: list[UserExpression],
    ):
        for judgement in judgments:
            for user_expression in user_expressions_to_update:
                if str(user_expression.expression.id) == judgement.id:
                    user_expression.knowledge_level = (
                        calculate_knowledge_level(
                            user_expression.knowledge_level,
                            user_expression.practice_count,
                            judgement.is_correct,
                        )
                    )
                    user_expression.practice_count += 1
                    user_expression.last_practice_time = get_current_utc_time()
                    self.user_expr_repo.put(user_expression)

    @staticmethod
    def _update_dialogue_expressions_status(
        writings: Writings, judgments: list[ExpressionUsageResponse]
    ) -> Writings:
        for judgement in judgments:
            expression_id = judgement.id
            if judgement.is_correct:
                writings.remove_expression_by(expression_id)
            else:
                writings.update_expression_by_id(
                    expression_id,
                    "failed",
                    judgement.comment,
                )
        return writings

    def _user_expressions_to_update(
        self, judgments: list[ExpressionUsageResponse]
    ) -> list[UserExpression]:
        expression_ids_to_update = [judgment.id for judgment in judgments]
        user_expressions_to_update = self.user_expr_repo.get(
            include=expression_ids_to_update
        )
        return user_expressions_to_update

    def _get_expression_usage_judgement(
        self,
        text: str,
        detected_expression_ids: ExpressionDetectionResponse,
        writings: Writings,
    ) -> list[ExpressionUsageResponse]:
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(
                    self.assistant.get_expression_usage_judgement,
                    text,
                    {
                        "id": expression_id,
                        "expression": writings.get_expression(expression_id)[
                            "expression"
                        ],
                        "meaning": writings.get_expression(expression_id)[
                            "definition"
                        ],
                    },
                )
                for expression_id in detected_expression_ids.expressions
            ]
            judgments = [future.result() for future in as_completed(futures)]
        return judgments

    def _get_general_judgement(
        self, text: str, expressions_to_detect: list[dict]
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
    def _build_expressions_to_detect_message(writings: Writings) -> list[dict]:
        expressions_to_detect = [
            {"id": expr["id"], "expression": expr["expression"]}
            for expr in writings.expressions
        ]
        return expressions_to_detect

    def _create_writings(self) -> Writings:
        id_ = str(uuid4())
        writings = Writings(
            id=id_,
            user_id=self.user_id,
            properties=DEFAULT_PROPERTIES,
            writings=[],
            expressions=[],
            added=get_current_utc_time(),
            updated=get_current_utc_time(),
        )
        writings = self._enrich_expressions(writings)
        self.writings_repo.add(writings)
        return writings

    def _enrich_expressions(self, writings: Writings) -> Writings:
        if (
            dif := int(writings.properties["maxExpressionsToTrain"])
            - len(writings.expressions)
        ) > 0:
            existing_expression_ids = [
                expression["id"] for expression in writings.expressions
            ]
            user_expressions_to_add = (
                self.user_expr_repo.get_trained_expressions(
                    limit=dif, excludes=existing_expression_ids
                )
            )
            writings.add_expressions(
                [
                    user_expression.expression
                    for user_expression in user_expressions_to_add
                ]
            )
            return writings

        return writings

    @staticmethod
    def _generate_writing_challenge(writings: Writings) -> WritingChallenge:
        return {
            "writings": writings.writings,
            "expressions": writings.expressions,
        }
