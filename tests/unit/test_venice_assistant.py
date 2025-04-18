from unittest import TestCase
from unittest.mock import Mock, patch
import os

from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from services.assistant import VeniceAssistant


# TODO: Implement tests for the Venice Assistant
class VeniceAssistantTests(TestCase):
    def setUp(self):
        os.environ["VENICE_MODEL"] = "test_model"
        os.environ["VENICE_API_KEY"] = "test_api_key"

        self.mock_venice_chat_model = Mock()

        chat_model_patcher = patch(
            "services.assistant.ChatVeniceAI",
            return_value=self.mock_venice_chat_model,
        )
        chat_model_patcher.start()
        self.addCleanup(chat_model_patcher.stop)

        self.subject = VeniceAssistant()
    
    def tearDown(self):
        del os.environ["VENICE_MODEL"]
        del os.environ["VENICE_API_KEY"]
    
    def _set_mock_chat_response(self, response: str):
        message = AIMessage(content=response, usage_metadata={
            "input_tokens": 6,
            "output_tokens": 4,
            "total_tokens": 10,
        })
        self.mock_venice_chat_model._generate.return_value = (
            ChatResult(generations=[ChatGeneration(message=message)])
        )

    # def test_complete_dialogue(self):
    #     dialogue = [
    #         {"role": "user", "content": "Hello"},
    #         {"role": "assistant", "content": "Hi! How can I help you?"},
    #     ]
    #     self._set_mock_chat_response("Hello, how can I assist you?")
    #     actual = self.subject.complete_dialogue(dialogue)
    #     self.assertEqual("", actual)

    # def test_get_general_judgement(self):
    #     pass

    # def test_detect_phrases_usage(self):
    #     pass

    # def test_get_expression_usage_judgement(self):
    #     pass
