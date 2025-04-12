from typing import TypedDict
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor, as_completed

from helpers.time_helpers import get_current_utc_time
from repository.dialogue_training_repo import DialogueTrainingRepo
from repository.user_expressions_repo import UserExpressionsRepo
from models.models import Dialogue, UserExpression
from services.assistant import ExpressionDetectionResponse, ExpressionUsageResponse, GeneralJudgementResponse, VeniceAssistant
from exercises.common import calculate_knowledge_level


DEFAULT_SETTINGS = {"maxExpressionsToTrain": 10}
DEFAULT_DIALOGUE = [
    {
        "id": 1,
        "role": "assistant",
        "text": "Hello! What are we going to talk about?",
    },
]


class DialogueListItemDict(TypedDict):
    id: str
    title: str
    description: str


class DialogueDict(TypedDict):
    id: str
    title: str
    description: str
    settings: dict
    dialogues: list[dict]
    expressions: list[dict]


class DialogueTraining:
    def __init__(
        self,
        user_id: str,
        dialogue_repo: DialogueTrainingRepo = DialogueTrainingRepo,
        user_expr_repo: UserExpressionsRepo = UserExpressionsRepo,
        assistant: VeniceAssistant = VeniceAssistant,
    ):
        self.user_id = user_id
        self.dialogue_repo = dialogue_repo(user_id)
        self.user_expr_repo = user_expr_repo(user_id)
        self.assistant = assistant()

    def get_dialogues(self):
        """Return a list of dialogues for the user"""
        dialogues = self.dialogue_repo.get()
        dialogues_list = [
            {
                "id": dialogue.id,
                "title": dialogue.title,
                "description": dialogue.description,
            }
            for dialogue in dialogues
        ]
        return dialogues_list

    def create_dialogue(self, title: str, description: str) -> str:
        """Create a new dialogue and return the dialogue id"""
        id_ = str(uuid4())
        expressions = self.user_expr_repo.get_oldest_trained_expressions(
            int(DEFAULT_SETTINGS["maxExpressionsToTrain"])
        )
        expressions_list = [
            {
                "id": str(expression.expression_id),
                "expression": expression.expression.expression,
                "definition": expression.expression.definition,
                "status": "not_checked",
            }
            for expression in expressions
        ]
        dialogue = Dialogue(
            id=id_,
            user_id=self.user_id,
            title=title,
            settings=DEFAULT_SETTINGS,
            dialogues=DEFAULT_DIALOGUE,
            expressions=expressions_list,
            added=get_current_utc_time(),
            updated=get_current_utc_time(),
        )

        if description:
            dialogue.description = description

        self.dialogue_repo.create(dialogue)

        return id_

    def delete_dialogue(self, dialogue_id: str):
        """Delete a dialogue by id"""
        self.dialogue_repo.delete(dialogue_id)

    def get_dialogue(self, dialogue_id: str) -> dict:
        """Return a dialogue by id"""
        dialogue = self.dialogue_repo.get(dialogue_id)
        return {
            "id": dialogue.id,
            "title": dialogue.title,
            "description": dialogue.description,
            "settings": dialogue.settings,
            "dialogue": dialogue.dialogues,
            "expressions": dialogue.expressions,
        }

    def submit_dialogue_statement(
        self, dialogue_id: str, statement: str
    ) -> dict:
        """Submit a statement to the dialogue and return the updated dialogue"""
        dialogue = self.dialogue_repo.get(dialogue_id)
        (
            dialogue_completion_response,
            general_judgement,
            detected_expression_ids
        ) = self._get_statement_dedicated_assistant_response(
            self._build_dialogue_complete_message(dialogue, statement),
            statement,
            self._build_expressions_to_detect_message(dialogue),
        )
        print("*" * 50)
        print("Assistant message: ", dialogue_completion_response)
        print("---")
        print("General judgement: ", general_judgement)
        print("---")
        print("Detected expression ids: ", detected_expression_ids)
        print("*" * 50)
        if detected_expression_ids.expressions:
            judgments = self._get_expression_usage_judgement(
                statement,
                detected_expression_ids,
                dialogue,
            )
            user_expressions_to_update = self._user_expressions_to_update(
                judgments
            )
            dialogue = self._update_dialogue_expressions_status(
                dialogue,
                judgments,
            )
            self._update_user_expressions(
                judgments,
                user_expressions_to_update,
            )
        dialogue = self._enrich_dialogue_expressions(dialogue)
        dialogue = self._update_dialogue_messages(
            dialogue,
            statement,
            dialogue_completion_response,
            general_judgement,
        )
        self.dialogue_repo.update(dialogue)

        return {
            "id": dialogue.id,
            "title": dialogue.title,
            "description": dialogue.description,
            "dialogue": dialogue.dialogues,
            "expressions": dialogue.expressions,
        }
    
    @staticmethod
    def _build_dialogue_complete_message(dialogue: Dialogue, statement: str) -> list[dict]:
        messages = [
            {"role": message["role"], "content": message["text"]}
            for message in dialogue.dialogues
        ]
        messages.append({"role": "user", "content": statement})
        return messages
    
    @staticmethod
    def _build_expressions_to_detect_message(dialogue: Dialogue) -> list[dict]:
        expressions_to_detect = [
            {"id": expr["id"], "expression": expr["expression"]}
            for expr in dialogue.expressions
        ]
        return expressions_to_detect
    
    def _get_statement_dedicated_assistant_response(self, messages: list[dict], statement: str, expressions_to_detect: list[dict]) -> tuple[str, GeneralJudgementResponse, ExpressionDetectionResponse]:
        with ThreadPoolExecutor() as executor:
            future_assistant_message = executor.submit(
                self.assistant.complete_dialogue, messages
            )
            future_general_judgement = executor.submit(
                self.assistant.get_general_judgement, statement
            )
            future_detected_expression_ids = executor.submit(
                self.assistant.detect_phrases_usage,
                statement,
                expressions_to_detect,
            )

            assistant_message = future_assistant_message.result()
            general_judgement = future_general_judgement.result()
            detected_expression_ids = future_detected_expression_ids.result()

        return assistant_message, general_judgement, detected_expression_ids

    def _get_expression_usage_judgement(self, statement: str, detected_expression_ids: ExpressionDetectionResponse, dialogue: Dialogue) -> list[ExpressionUsageResponse]:
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(
                    self.assistant.get_expression_usage_judgement,
                    statement,
                    {
                        "id": expression_id,
                        "expression": dialogue.get_dialogue_expression(
                            expression_id
                        )["expression"],
                        "meaning": dialogue.get_dialogue_expression(
                            expression_id
                        )["definition"],
                    },
                )
                for expression_id in detected_expression_ids.expressions
            ]
            judgments = [
                future.result() for future in as_completed(futures)
            ]
        return judgments

    def _user_expressions_to_update(self, judgments: list[ExpressionUsageResponse]) -> list[UserExpression]:
        expression_ids_to_update = [judgment.id for judgment in judgments]
        user_expressions_to_update = self.user_expr_repo.get(
            include=expression_ids_to_update
        )
        return user_expressions_to_update

    @staticmethod
    def _update_dialogue_expressions_status(dialogue: Dialogue, judgments: list[ExpressionUsageResponse]) -> Dialogue:
        for judgement in judgments:
            expression_id = judgement.id
            if judgement.is_correct:
                dialogue.remove_expression_by(expression_id)
            else:
                dialogue.update_expression_by_id(
                    expression_id,
                    "failed",
                    judgement.comment,
                )
        return dialogue
    
    def _update_user_expressions(self, judgments: list[ExpressionUsageResponse], user_expressions_to_update: list[UserExpression]):
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
                    user_expression.last_practice_time = (
                        get_current_utc_time()
                    )
                    self.user_expr_repo.put(user_expression)
    
    def _enrich_dialogue_expressions(self, dialogue: Dialogue) -> Dialogue:
        if (
            dif := int(dialogue.settings["maxExpressionsToTrain"])
            - len(dialogue.expressions)
        ) > 0:
            existing_expression_ids = [
                expression["id"] for expression in dialogue.expressions
            ]
            user_expressions_to_add = self.user_expr_repo.get_oldest_trained_expressions_with_excludes(
                dif, excludes=existing_expression_ids
            )
            dialogue.add_expressions(
                [
                    user_expression.expression
                    for user_expression in user_expressions_to_add
                ]
            )
            return dialogue

        return dialogue

    def _update_dialogue_messages(self, dialogue: Dialogue, statement: str, dialogue_completion_response: str, general_judgement: GeneralJudgementResponse) -> Dialogue:
        comment = [
            {
                "problem": item.problem,
                "explanation": item.explanation,
                "solution": item.solution,
            }
            for item in general_judgement.problems
            if item.problem not in ("None", "")
        ]
        dialogue.add_message(statement, "user", comment=comment)
        dialogue.add_message(dialogue_completion_response, "assistant")
        dialogue.updated = get_current_utc_time()

        return dialogue
