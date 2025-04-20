from copy import deepcopy
import os
from unittest import TestCase
from unittest.mock import patch, Mock, call

from services.assistant import (
    ExpressionDetectionResponse,
    Problem,
    GeneralJudgementResponse,
    ExpressionUsageResponse,
)
from exercises.dialogue_training import DialogueTraining
from models.models import Dialogue
from tests.unit.fixtures import (
    get_dialogue,
    get_user_expression,
    get_expression,
)


class BaseDialogueTrainingTest(TestCase):
    def setUp(self):
        self.user_id = "464ed801-72ee-41c1-9e11-4ac08ff84ea4"
        os.environ["VENICE_MODEL"] = "test_model"
        os.environ["VENICE_API_KEY"] = "test_api_key"

        self.mock_dialogue_repo = Mock()
        self.mock_user_expression_repo = Mock()
        self.mock_assistant = Mock()
        self.subject = DialogueTraining(
            self.user_id,
            self.mock_dialogue_repo,
            self.mock_user_expression_repo,
            self.mock_assistant,
        )

    def tearDown(self):
        os.environ.pop("VENICE_MODEL", None)
        os.environ.pop("VENICE_API_KEY", None)

    def reset_all_mock(self):
        self.mock_dialogue_repo.reset_mock()
        self.mock_user_expression_repo.reset_mock()
        self.mock_assistant.reset_mock()


class GetTests(BaseDialogueTrainingTest):
    def setUp(self):
        super().setUp()
        self.dialogues = [
            get_dialogue(
                id_="4d7993aa-d897-4647-994b-e0625c88f349",
                user_id=self.user_id,
                title="Dialogue 1",
                description="Dialogue 1 description",
                settings={"setting": "value"},
                dialogues=[{"dialogue": "dialogue 1"}],
                expressions=[{"expression": "expression 1"}],
                added="2016-06-22 19:10:26",
                updated="2016-06-22 19:10:25",
            ),
            get_dialogue(
                id_="24d96f68-46e1-4fb3-b300-81cd89cea435",
                user_id=self.user_id,
                title="Dialogue 2",
                description="Dialogue 2 description",
                settings={"setting": "value"},
                dialogues=[{"dialogue": "dialogue 2"}],
                expressions=[{"expression": "expression 2"}],
                added="2016-06-22 19:10:24",
                updated="2016-06-22 19:10:25",
            ),
        ]

    def test_get_all(self):
        self.mock_dialogue_repo.return_value.get.return_value = self.dialogues
        expected = [
            {
                "id": "4d7993aa-d897-4647-994b-e0625c88f349",
                "title": "Dialogue 1",
                "description": "Dialogue 1 description",
                "trainedExpressionsCount": 0,
            },
            {
                "id": "24d96f68-46e1-4fb3-b300-81cd89cea435",
                "title": "Dialogue 2",
                "description": "Dialogue 2 description",
                "trainedExpressionsCount": 0,
            },
        ]
        actual = self.subject.get_dialogues()

        self.assertEqual(expected, actual)

        self.mock_dialogue_repo.return_value.get.assert_called_once_with()

    def test_get_one(self):
        self.mock_dialogue_repo.return_value.get.return_value = self.dialogues[
            0
        ]
        expected = {
            "id": "4d7993aa-d897-4647-994b-e0625c88f349",
            "title": "Dialogue 1",
            "description": "Dialogue 1 description",
            "settings": {"setting": "value"},
            "dialogue": [{"dialogue": "dialogue 1"}],
            "expressions": [{"expression": "expression 1"}],
        }
        actual = self.subject.get_dialogue(
            "4d7993aa-d897-4647-994b-e0625c88f349"
        )

        self.assertEqual(expected, actual)

        self.mock_dialogue_repo.return_value.get.assert_called_once_with(
            "4d7993aa-d897-4647-994b-e0625c88f349"
        )


class CreateDialogueTests(BaseDialogueTrainingTest):
    def setUp(self):
        super().setUp()

        self.dialogue_id = "4d7993aa-d897-4647-994b-e0625c88f349"
        uuid_patcher = patch(
            "exercises.dialogue_training.uuid4",
            return_value=self.dialogue_id,
        )
        uuid_patcher.start()
        self.addCleanup(uuid_patcher.stop)

    def test_create_dialogue(self):
        expression_id_1 = "ab856dd3-7a68-4693-a0bc-e14a1799c19b"
        expression_id_2 = "ab856dd3-7a68-4693-a0bc-e14a1799c19c"
        expression_1 = get_expression(
            expression_id=expression_id_1,
            expression="expression 1",
            definition="definition 1",
        )
        expression_2 = get_expression(
            expression_id=expression_id_2,
            expression="expression 2",
            definition="definition 2",
        )
        user_expression_1 = get_user_expression(
            user_id=self.user_id,
            user=None,
            expression=expression_1,
        )
        user_expression_2 = get_user_expression(
            user_id=self.user_id,
            user=None,
            expression=expression_2,
        )
        self.mock_user_expression_repo.return_value.get_trained_expressions.return_value = [
            user_expression_1,
            user_expression_2,
        ]

        actual = self.subject.create_dialogue(
            "Dialogue 1", "Dialogue 1 description"
        )

        self.assertEqual(self.dialogue_id, actual)

        self.mock_user_expression_repo.return_value.get_trained_expressions.assert_called_once_with(
            10
        )

        actual_dialogue = (
            self.mock_dialogue_repo.return_value.create.call_args.args[0]
        )
        self.assertEqual(self.dialogue_id, actual_dialogue.id)
        self.assertEqual(self.user_id, actual_dialogue.user_id)
        self.assertEqual("Dialogue 1", actual_dialogue.title)
        self.assertEqual("Dialogue 1 description", actual_dialogue.description)
        self.assertEqual(
            {"maxExpressionsToTrain": 10}, actual_dialogue.settings
        )
        self.assertEqual(
            [
                {
                    "id": 1,
                    "role": "assistant",
                    "text": "Hello! What are we going to talk about?",
                }
            ],
            actual_dialogue.dialogues,
        )
        self.assertEqual(
            [
                {
                    "definition": "definition 1",
                    "expression": "expression 1",
                    "id": "ab856dd3-7a68-4693-a0bc-e14a1799c19b",
                    "status": "not_checked",
                },
                {
                    "definition": "definition 2",
                    "expression": "expression 2",
                    "id": "ab856dd3-7a68-4693-a0bc-e14a1799c19c",
                    "status": "not_checked",
                },
            ],
            actual_dialogue.expressions,
        )
        self.assertEqual(
            {"trainedExpressionsCount": 0},
            actual_dialogue.properties,
        )


class DeleteDialogueTests(BaseDialogueTrainingTest):
    def test_delete_dialogue(self):
        dialogue_id = "test_id"

        self.subject.delete_dialogue(dialogue_id)

        self.mock_dialogue_repo.return_value.delete.assert_called_once_with(
            dialogue_id
        )


class SubmitDialogueStatementTests(BaseDialogueTrainingTest):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.dialogue_id = "4d7993aa-d897-4647-994b-e0625c88f349"
        self.statement = "test statement"

        self.dialogue = Dialogue(
            id=self.dialogue_id,
            user_id=self.user_id,
            title="Dialogue 1",
            description="Dialogue 1 description",
            properties={"trainedExpressionsCount": 0},
            settings={"maxExpressionsToTrain": 3},
            dialogues=[
                {
                    "id": 1,
                    "role": "assistant",
                    "text": "Hello! What are we going to talk about?",
                },
            ],
            expressions=[
                {
                    "id": "1",
                    "expression": "expression 1",
                    "definition": "definition 1",
                    "status": "not_checked",
                },
                {
                    "id": "2",
                    "expression": "expression 2",
                    "definition": "definition 2",
                    "status": "not_checked",
                },
                {
                    "id": "3",
                    "expression": "expression 3",
                    "definition": "definition 3",
                    "status": "not_checked",
                },
            ],
            added="2016-06-22 19:10:26",
            updated="2016-06-22 19:10:25",
        )

        self.updated = "2016-06-22 19:15:25"
        current_patcher = patch(
            "exercises.dialogue_training.get_current_utc_time",
            return_value=self.updated,
        )
        current_patcher.start()
        self.addCleanup(current_patcher.stop)

    def _get_expected_updated_dialogue(
        self, problems=None, expressions=None, trained_expressions_count=0
    ):
        res = Dialogue(
            id=self.dialogue_id,
            user_id=self.user_id,
            title="Dialogue 1",
            description="Dialogue 1 description",
            properties={"trainedExpressionsCount": trained_expressions_count},
            settings={"maxExpressionsToTrain": 3},
            dialogues=[
                {
                    "id": 1,
                    "role": "assistant",
                    "text": "Hello! What are we going to talk about?",
                },
                {
                    "id": 2,
                    "role": "user",
                    "text": "test statement",
                    "comment": [
                        {
                            "problem": "the problem",
                            "explanation": "the explanation",
                            "solution": "the solution",
                        }
                    ],
                },
                {"id": 3, "role": "assistant", "text": "test response"},
            ],
            expressions=[
                {
                    "id": "1",
                    "expression": "expression 1",
                    "definition": "definition 1",
                    "status": "not_checked",
                },
                {
                    "id": "2",
                    "expression": "expression 2",
                    "definition": "definition 2",
                    "status": "not_checked",
                },
                {
                    "id": "3",
                    "expression": "expression 3",
                    "definition": "definition 3",
                    "status": "not_checked",
                },
            ],
            added="2016-06-22 19:10:26",
            updated=self.updated,
        )
        if problems is not None:
            res.dialogues[1]["comment"] = problems
        if expressions is not None:
            res.expressions = expressions
        return res

    def _get_expected_response(self, problems=None, expressions=None):
        res = {
            "description": "Dialogue 1 description",
            "dialogue": [
                {
                    "id": 1,
                    "role": "assistant",
                    "text": "Hello! What are we going to talk about?",
                },
                {"id": 2, "role": "user", "text": "test statement"},
                {"id": 3, "role": "assistant", "text": "test response"},
            ],
            "expressions": [
                {
                    "definition": "definition 1",
                    "expression": "expression 1",
                    "id": "1",
                    "status": "not_checked",
                },
                {
                    "definition": "definition 2",
                    "expression": "expression 2",
                    "id": "2",
                    "status": "not_checked",
                },
                {
                    "definition": "definition 3",
                    "expression": "expression 3",
                    "id": "3",
                    "status": "not_checked",
                },
            ],
            "id": "4d7993aa-d897-4647-994b-e0625c88f349",
            "title": "Dialogue 1",
        }
        if problems is not None:
            res["dialogue"][1]["comment"] = problems
        if expressions is not None:
            res["expressions"] = expressions
        return res

    def _get_expected_updated_dialogue_and_response(self, problems=None):
        expected_updated_dialogue = self._get_expected_updated_dialogue(
            problems
        )
        expected_response = self._get_expected_response(problems)
        return {
            "expected_dialogue": expected_updated_dialogue,
            "expected_response": expected_response,
        }

    def test_handle_general_statement_general_judgement(self):
        cases = [
            {
                "case": "get_general_judgement - two problems",
                "problems": GeneralJudgementResponse(
                    problems=[
                        Problem(
                            problem="the problem",
                            explanation="the explanation",
                            solution="the solution",
                        ),
                        Problem(
                            problem="the problem 2",
                            explanation="the explanation 2",
                            solution="the solution 2",
                        ),
                    ]
                ),
                **self._get_expected_updated_dialogue_and_response(
                    [
                        {
                            "problem": "the problem",
                            "explanation": "the explanation",
                            "solution": "the solution",
                        },
                        {
                            "problem": "the problem 2",
                            "explanation": "the explanation 2",
                            "solution": "the solution 2",
                        },
                    ]
                ),
            },
            {
                "case": "get_general_judgement - no problems",
                "problems": GeneralJudgementResponse(problems=[]),
                **self._get_expected_updated_dialogue_and_response(
                    problems=[]
                ),
            },
            {
                "case": "get_general_judgement - one of two problems is 'None'",
                "problems": GeneralJudgementResponse(
                    problems=[
                        Problem(
                            problem="None",
                            explanation="the explanation",
                            solution="",
                        ),
                        Problem(
                            problem="the problem 2",
                            explanation="the explanation 2",
                            solution="the solution 2",
                        ),
                    ]
                ),
                **self._get_expected_updated_dialogue_and_response(
                    [
                        {
                            "problem": "the problem 2",
                            "explanation": "the explanation 2",
                            "solution": "the solution 2",
                        },
                    ]
                ),
            },
            {
                "case": "get_general_judgement - one of two problems is ''",
                "problems": GeneralJudgementResponse(
                    problems=[
                        Problem(
                            problem="",
                            explanation="the explanation",
                            solution="",
                        ),
                        Problem(
                            problem="the problem 2",
                            explanation="the explanation 2",
                            solution="the solution 2",
                        ),
                    ]
                ),
                **self._get_expected_updated_dialogue_and_response(
                    [
                        {
                            "problem": "the problem 2",
                            "explanation": "the explanation 2",
                            "solution": "the solution 2",
                        },
                    ]
                ),
            },
        ]

        for case in cases:
            self.reset_all_mock()
            with self.subTest(case=case["case"]):
                self.mock_dialogue_repo.return_value.get.return_value = (
                    deepcopy(self.dialogue)
                )
                self.mock_assistant.return_value.complete_dialogue.return_value = (
                    "test response"
                )
                self.mock_assistant.return_value.get_general_judgement.return_value = case[
                    "problems"
                ]
                self.mock_assistant.return_value.detect_phrases_usage.return_value = ExpressionDetectionResponse(
                    expressions=[]
                )

                actual = self.subject.submit_dialogue_statement(
                    self.dialogue_id, self.statement
                )

                self.assertEqual(case["expected_response"], actual)

                self.mock_dialogue_repo.return_value.get.assert_called_once_with(
                    self.dialogue_id
                )
                self.mock_assistant.return_value.complete_dialogue.assert_called_once_with(
                    [
                        {
                            "role": "assistant",
                            "content": "Hello! What are we going to talk about?",
                        },
                        {"role": "user", "content": "test statement"},
                    ]
                )
                self.mock_assistant.return_value.get_general_judgement.assert_called_once_with(
                    "test statement"
                )
                self.mock_assistant.return_value.detect_phrases_usage.assert_called_once_with(
                    "test statement",
                    [
                        {"id": "1", "expression": "expression 1"},
                        {"id": "2", "expression": "expression 2"},
                        {"id": "3", "expression": "expression 3"},
                    ],
                )
                self._assert_dialogue(
                    case["expected_dialogue"],
                    self.mock_dialogue_repo.return_value.update.call_args.args[
                        0
                    ],
                )

    def test_handle_general_statement_expression_judgement(self):
        self.mock_dialogue_repo.return_value.get.return_value = deepcopy(
            self.dialogue
        )
        self.mock_assistant.return_value.complete_dialogue.return_value = (
            "test response"
        )
        self.mock_assistant.return_value.get_general_judgement.return_value = (
            GeneralJudgementResponse(problems=[])
        )
        self.mock_assistant.return_value.detect_phrases_usage.return_value = (
            ExpressionDetectionResponse(expressions=["1", "2"])
        )
        self.mock_assistant.return_value.get_expression_usage_judgement.side_effect = [
            ExpressionUsageResponse(
                id="1", is_correct=False, comment="expression-1 judgement"
            ),
            ExpressionUsageResponse(
                id="2", is_correct=True, comment="expression-2 judgement"
            ),
        ]
        self.mock_user_expression_repo.return_value.get.return_value = [
            get_user_expression(
                user_id=self.user_id,
                user=None,
                expression=get_expression(
                    expression_id="1",
                    expression="expression 1",
                    definition="definition 1",
                ),
                kl=0.5,
                pc=1,
            ),
            get_user_expression(
                user_id=self.user_id,
                user=None,
                expression=get_expression(
                    expression_id="2",
                    expression="expression 2",
                    definition="definition 2",
                ),
                kl=0.5,
                pc=1,
            ),
        ]
        self.mock_user_expression_repo.return_value.get_trained_expressions.return_value = [
            get_user_expression(
                user_id=self.user_id,
                user=None,
                expression=get_expression(
                    expression_id="4",
                    expression="expression 4",
                    definition="definition 4",
                ),
            ),
        ]

        actual = self.subject.submit_dialogue_statement(
            self.dialogue_id, self.statement
        )

        expected_expressions = [
            {
                "definition": "definition 1",
                "expression": "expression 1",
                "id": "1",
                "status": "failed",
                "comment": "expression-1 judgement",
            },
            {
                "definition": "definition 3",
                "expression": "expression 3",
                "id": "3",
                "status": "not_checked",
            },
            {
                "definition": "definition 4",
                "expression": "expression 4",
                "id": "4",
                "status": "not_checked",
            },
        ]

        self.assertEqual(
            self._get_expected_response(
                problems=[], expressions=expected_expressions
            ),
            actual,
        )

        self.mock_dialogue_repo.return_value.get.assert_called_once_with(
            self.dialogue_id
        )
        self.mock_assistant.return_value.complete_dialogue.assert_called_once_with(
            [
                {
                    "role": "assistant",
                    "content": "Hello! What are we going to talk about?",
                },
                {"role": "user", "content": "test statement"},
            ]
        )
        self.mock_assistant.return_value.get_general_judgement.assert_called_once_with(
            "test statement"
        )
        self.mock_assistant.return_value.detect_phrases_usage.assert_called_once_with(
            "test statement",
            [
                {"id": "1", "expression": "expression 1"},
                {"id": "2", "expression": "expression 2"},
                {"id": "3", "expression": "expression 3"},
            ],
        )
        self.mock_assistant.return_value.get_expression_usage_judgement.assert_has_calls(
            [
                call(
                    "test statement",
                    {
                        "id": "1",
                        "expression": "expression 1",
                        "meaning": "definition 1",
                    },
                ),
                call(
                    "test statement",
                    {
                        "id": "2",
                        "expression": "expression 2",
                        "meaning": "definition 2",
                    },
                ),
            ]
        )
        self.mock_user_expression_repo.return_value.get.assert_called_once_with(
            include=["1", "2"]
        )

        put_expressions = (
            self.mock_user_expression_repo.return_value.put.call_args_list
        )
        self.assertEqual(2, len(put_expressions))
        self.assertEqual("1", put_expressions[0].args[0].expression.id)
        self.assertEqual(0.25, put_expressions[0].args[0].knowledge_level)
        self.assertEqual(2, put_expressions[0].args[0].practice_count)
        self.assertEqual(
            self.updated, put_expressions[0].args[0].last_practice_time
        )
        self.assertEqual("2", put_expressions[1].args[0].expression.id)
        self.assertEqual(0.75, put_expressions[1].args[0].knowledge_level)
        self.assertEqual(2, put_expressions[1].args[0].practice_count)
        self.assertEqual(
            self.updated, put_expressions[1].args[0].last_practice_time
        )

        self.mock_user_expression_repo.return_value.get_trained_expressions.assert_called_once_with(
            limit=1, excludes=["1", "3"]
        )
        self._assert_dialogue(
            self._get_expected_updated_dialogue(
                problems=[],
                expressions=expected_expressions,
                trained_expressions_count=1,
            ),
            self.mock_dialogue_repo.return_value.update.call_args.args[0],
        )

    def _assert_dialogue(self, expected: Dialogue, actual: Dialogue):
        self.assertEqual(expected.id, actual.id)
        self.assertEqual(expected.user_id, actual.user_id)
        self.assertEqual(expected.title, actual.title)
        self.assertEqual(expected.description, actual.description)
        self.assertEqual(expected.properties, actual.properties)
        self.assertEqual(expected.settings, actual.settings)
        self.assertEqual(expected.dialogues, actual.dialogues)
        self.assertEqual(expected.expressions, actual.expressions)
        self.assertEqual(expected.added, actual.added)
        self.assertEqual(expected.updated, actual.updated)
