from unittest import TestCase
from unittest.mock import MagicMock, patch
from langchain_core.messages import BaseMessage
from services.venice_chat_model import ChatVeniceAI
from langchain_core.outputs import ChatResult

class ChatVeniceAITests(TestCase):
    @patch("services.venice_chat_model.VeniceClient")
    def test_init_venice_client(self, mock_venice_client):
        mock_api_key = "test_api_key"
        chat_model = ChatVeniceAI(
            model="test_model",
            api_key=mock_api_key,
            temperature=0.7,
        )

        client = chat_model._init_venice_client()

        mock_venice_client.assert_called_once_with(
            model="test_model",
            api_key=mock_api_key,
            temperature=0.7,
        )
        self.assertEqual(client, mock_venice_client.return_value)

    @patch("services.venice_chat_model.VeniceClient")
    def test_generate(self, mock_venice_client):
        mock_response = {
            "choices": [{"message": {"content": "response content"}}],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15,
            },
        }
        mock_venice_client.return_value.do_chat_completion.return_value = mock_response

        chat_model = ChatVeniceAI(
            model="test_model",
            api_key="test_api_key",
        )

        messages = [BaseMessage(type="human", content="Hello")]
        result = chat_model._generate(messages)

        mock_venice_client.return_value.do_chat_completion.assert_called_once_with(
            messages=[
                {"role": "user", "content": "Hello"}
            ]
        )
        self.assertIsInstance(result, ChatResult)
        self.assertEqual(result.generations[0].message.content, "response content")
        self.assertEqual(
            result.generations[0].message.usage_metadata,
            {
                "input_tokens": 10,
                "output_tokens": 5,
                "total_tokens": 15,
            },
        )

    def test_get_chat_messages(self):
        chat_model = ChatVeniceAI(
            model="test_model",
            api_key="test_api_key",
        )

        messages = [
            BaseMessage(type="system", content="System message"),
            BaseMessage(type="human", content="User message"),
            BaseMessage(type="ai", content="AI message"),
        ]
        result = chat_model._get_chat_messages(messages)

        expected = [
            {"role": "system", "content": "System message"},
            {"role": "user", "content": "User message"},
            {"role": "assistant", "content": "AI message"},
        ]
        self.assertEqual(result, expected)

    def test_llm_type(self):
        chat_model = ChatVeniceAI(
            model="test_model",
            api_key="test_api_key",
        )
        self.assertEqual(chat_model._llm_type, "venice")

    def test_identifying_params(self):
        chat_model = ChatVeniceAI(
            model="test_model",
            api_key="test_api_key",
        )
        self.assertEqual(
            chat_model._identifying_params,
            {"model_name": "test_model"},
        )