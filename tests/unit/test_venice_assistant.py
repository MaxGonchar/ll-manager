from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch
import os
import warnings

from services.assistant import (
    VeniceAssistant,
    character,
    general_judgement_template,
    expression_detection_template,
    expression_usage_template,
)

general_judgement_response = """
Here is the language analysis of the given text:

```
{
  "problems": [
    {
      "problem": "Are you wheel with it?",
      "explanation": "The word 'wheel' is incorrectly used instead of 'familiar' or 'well'. The correct phrase should be 'Are you familiar with it?' or 'Are you well with it?' but in this context, 'familiar' is more suitable.",
      "solution": "Are you familiar with it?"
    },
    {
      "problem": "Hi, let's talk about attic.",
      "explanation": "The sentence is a simple statement and lacks a question or a clear direction for the conversation. It would be more engaging to ask a question or provide more context.",
      "solution": "Hi, let's discuss the attic. What would you like to know about it?"
    },
    {
      "problem": "Hi, let's talk about attic. Are you wheel with it?",
      "explanation": "The sentence structure is simple and lacks variety. The text could benefit from more complex sentence structures and a clearer connection between the two sentences.",
      "solution": "Hi, I'd like to discuss the attic. Are you familiar with its components and functions?"
    }
  ]
}
```

In terms of punctuation errors, there are no major issues in the given text. However, the second sentence could be improved with a question mark to make it clearer that it's a question.

Grammar errors are present, mainly due to the incorrect use of the word 'wheel' instead of 'familiar' or 'well'.

Spelling errors are not present in the given text.

The sentence structure is simple and could be improved with more variety and complexity.

The readability of the text is straightforward, but it could be improved with more context and clearer connections between the sentences.
"""

general_judgement_response_format = """The output should be formatted as a JSON instance that conforms to the JSON schema below.

As an example, for the schema {"properties": {"foo": {"title": "Foo", "description": "a list of strings", "type": "array", "items": {"type": "string"}}}, "required": ["foo"]}
the object {"foo": ["bar", "baz"]} is a well-formatted instance of the schema. The object {"properties": {"foo": ["bar", "baz"]}} is not well-formatted.

Here is the output schema:
```
{"$defs": {"Problem": {"properties": {"problem": {"description": "A part from the text that has a problem", "title": "Problem", "type": "string"}, "explanation": {"description": "Explanation of the problem", "title": "Explanation", "type": "string"}, "solution": {"description": "Corrected part of text", "title": "Solution", "type": "string"}}, "required": ["problem", "explanation", "solution"], "title": "Problem", "type": "object"}}, "properties": {"problems": {"description": "List of problems", "items": {"$ref": "#/$defs/Problem"}, "title": "Problems", "type": "array"}}, "required": ["problems"]}
```"""

detect_phrases_usage_response = """To identify the used expressions, let's examine the given text: "Hi, let's talk about attic. Are you wheel with it?"

The text mentions "attic" and "wheel", which correspond to the expressions with ids '578d1e4d-2813-45d4-8886-977fc065c750' and '1867002c-6f8f-4ad3-afad-af3b66785d0e', respectively.

Here is the list of expression ids used in the text, formatted according to the provided JSON schema:

```
{
  "expressions": [
    "578d1e4d-2813-45d4-8886-977fc065c750",
    "1867002c-6f8f-4ad3-afad-af3b66785d0e"
  ]
}
```"""

phrases_detection_response_format = """The output should be formatted as a JSON instance that conforms to the JSON schema below.

As an example, for the schema {"properties": {"foo": {"title": "Foo", "description": "a list of strings", "type": "array", "items": {"type": "string"}}}, "required": ["foo"]}
the object {"foo": ["bar", "baz"]} is a well-formatted instance of the schema. The object {"properties": {"foo": ["bar", "baz"]}} is not well-formatted.

Here is the output schema:
```
{"properties": {"expressions": {"description": "List of expression ids", "items": {"type": "string"}, "title": "Expressions", "type": "array"}}, "required": ["expressions"]}
```"""

expression_usage_judgement_response = """Based on the given text, the expression "wheel" is not used correctly in the context of the sentence. The correct word to use in this context would be "familiar" or "well-versed", but it seems like the speaker is trying to use the phrase "well" as in "are you well with it?" or more commonly "are you familiar with it?" 

Here is the output in the requested JSON format:

```
{
  "id": null,
  "is_correct": false,
  "comment": "The word 'wheel' is not used correctly in this context, it seems like the speaker meant to use the word 'well' or 'familiar'."
}
```"""

expression_usage_judgement_response_format = """The output should be formatted as a JSON instance that conforms to the JSON schema below.

As an example, for the schema {"properties": {"foo": {"title": "Foo", "description": "a list of strings", "type": "array", "items": {"type": "string"}}}, "required": ["foo"]}
the object {"foo": ["bar", "baz"]} is a well-formatted instance of the schema. The object {"properties": {"foo": ["bar", "baz"]}} is not well-formatted.

Here is the output schema:
```
{"properties": {"id": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": null, "description": "Id of the expression", "title": "Id"}, "is_correct": {"description": "Is the expression used correctly", "title": "Is Correct", "type": "boolean"}, "comment": {"description": "Comment about the usage of the expression", "title": "Comment", "type": "string"}}, "required": ["is_correct", "comment"]}
```"""


class VeniceAssistantTests(TestCase):
    def setUp(self):
        os.environ["VENICE_MODEL"] = "test_model"
        os.environ["VENICE_API_KEY"] = "test_api_key"

        # silent pydantic error from langchain code
        # PydanticDeprecatedSince211: Accessing this attribute on the instance is deprecated,
        # and will be removed in Pydantic V3. Instead, you should access this attribute
        # from the model class. Deprecated in Pydantic V2.11 to be removed in V3.0.
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        venice_client_patcher = patch(
            "services.venice_chat_model.VeniceClient",
        )
        mock_venice_client = venice_client_patcher.start()
        self.mock_do_chat_completion = (
            mock_venice_client.return_value.do_chat_completion
        )
        self.addCleanup(venice_client_patcher.stop)

        self.subject = VeniceAssistant()

        self.text = "Hi, let's talk about attic. Are you wheel with it?"

    def tearDown(self):
        del os.environ["VENICE_MODEL"]
        del os.environ["VENICE_API_KEY"]

    @staticmethod
    def _get_mock_model_response(content: str) -> dict:
        return {
            "choices": [
                {
                    "message": {
                        "content": content,
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15,
            },
        }

    def test_complete_dialogue(self):
        dialogue = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi! How can I help you?"},
        ]
        self.mock_do_chat_completion.return_value = (
            self._get_mock_model_response("I am here to assist you.")
        )

        actual = self.subject.complete_dialogue(dialogue)
        self.assertEqual("I am here to assist you.", actual)

        expected_messages = [
            {"role": "system", "content": character},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi! How can I help you?"},
        ]

        self.mock_do_chat_completion.assert_called_once_with(
            messages=expected_messages
        )

    def test_get_general_judgement(self):
        self.mock_do_chat_completion.return_value = (
            self._get_mock_model_response(general_judgement_response)
        )

        actual = self.subject.get_general_judgement(self.text)

        expected_as_dict = {
            "problems": [
                {
                    "explanation": "The word 'wheel' is incorrectly used instead of "
                    "'familiar' or 'well'. The correct phrase should "
                    "be 'Are you familiar with it?' or 'Are you well "
                    "with it?' but in this context, 'familiar' is "
                    "more suitable.",
                    "problem": "Are you wheel with it?",
                    "solution": "Are you familiar with it?",
                },
                {
                    "explanation": "The sentence is a simple statement and lacks a "
                    "question or a clear direction for the "
                    "conversation. It would be more engaging to ask "
                    "a question or provide more context.",
                    "problem": "Hi, let's talk about attic.",
                    "solution": "Hi, let's discuss the attic. What would you like "
                    "to know about it?",
                },
                {
                    "explanation": "The sentence structure is simple and lacks "
                    "variety. The text could benefit from more "
                    "complex sentence structures and a clearer "
                    "connection between the two sentences.",
                    "problem": "Hi, let's talk about attic. Are you wheel with it?",
                    "solution": "Hi, I'd like to discuss the attic. Are you "
                    "familiar with its components and functions?",
                },
            ]
        }
        self.assertEqual(expected_as_dict, actual.model_dump())

        expected_messages = [
            {
                "role": "user",
                "content": general_judgement_template.format(
                    text_to_analyze=self.text,
                    response_format=general_judgement_response_format,
                ),
            },
        ]

        self.mock_do_chat_completion.assert_called_once_with(
            messages=expected_messages
        )

    def test_detect_phrases_usage(self):
        expressions = [
            {
                "id": "578d1e4d-2813-45d4-8886-977fc065c750",
                "expression": "attic",
            },
            {
                "id": "1867002c-6f8f-4ad3-afad-af3b66785d0e",
                "expression": "wheel",
            },
        ]
        self.mock_do_chat_completion.return_value = (
            self._get_mock_model_response(detect_phrases_usage_response)
        )

        actual = self.subject.detect_phrases_usage(self.text, expressions)

        expected_as_dict = {
            "expressions": [
                "578d1e4d-2813-45d4-8886-977fc065c750",
                "1867002c-6f8f-4ad3-afad-af3b66785d0e",
            ]
        }

        self.assertEqual(expected_as_dict, actual.model_dump())

        expected_messages = [
            {
                "role": "user",
                "content": expression_detection_template.format(
                    text=self.text,
                    expression_list=expressions,
                    response_format=phrases_detection_response_format,
                ),
            },
        ]

        self.mock_do_chat_completion.assert_called_once_with(
            messages=expected_messages
        )

    def test_get_expression_usage_judgement(self):
        expression = {
            "id": "1867002c-6f8f-4ad3-afad-af3b66785d0e",
            "expression": "wheel",
            "meaning": "a circular object that revolves on an axle and is fixed below a vehicle or other object to enable it to move easily over the ground",
        }

        self.mock_do_chat_completion.return_value = (
            self._get_mock_model_response(expression_usage_judgement_response)
        )

        actual = self.subject.get_expression_usage_judgement(
            self.text, expression
        )

        expected_as_dict = {
            "id": "1867002c-6f8f-4ad3-afad-af3b66785d0e",
            "is_correct": False,
            "comment": "The word 'wheel' is not used correctly in this context, it seems like the speaker meant to use the word 'well' or 'familiar'.",
        }
        self.assertEqual(expected_as_dict, actual.model_dump())

        expected_messages = [
            {
                "role": "user",
                "content": expression_usage_template.format(
                    text=self.text,
                    expression=expression["expression"],
                    meaning=expression["meaning"],
                    response_format=expression_usage_judgement_response_format,
                ),
            },
        ]

        self.mock_do_chat_completion.assert_called_once_with(
            messages=expected_messages
        )
