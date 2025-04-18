from unittest import TestCase
from unittest.mock import patch, MagicMock

import requests
from services.venice_client import VeniceClient, VeniceClientError
import http


class VeniceClientTests(TestCase):
    def setUp(self):
        self.client = VeniceClient(
            model="test-model",
            api_key="test-api-key",
            temperature=0.7,
        )
        self.messages = [{"role": "user", "content": "Hello"}]

        self.patcher = patch("services.venice_client.requests.post")
        self.mock_post = self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def test_do_chat_completion_success(self):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"response": "Test response"}
        self.mock_post.return_value = mock_response

        result = self.client.do_chat_completion(self.messages)

        self.mock_post.assert_called_once_with(
            f"{self.client.base_url}/chat/completions",
            headers=self.client.headers,
            json={
                "model": self.client.model,
                "messages": self.messages,
                "temperature": self.client.temperature,
            },
            timeout=60,
        )
        self.assertEqual(result, {"response": "Test response"})

    def test_do_chat_completion_requests_timeout(self):
        self.mock_post.side_effect = requests.exceptions.Timeout

        with self.assertRaises(VeniceClientError) as context:
            self.client.do_chat_completion(self.messages)

        self.assertEqual(
            context.exception.message, "Request timed out"
        )
        self.assertEqual(
            context.exception.status_code, http.HTTPStatus.REQUEST_TIMEOUT.value
        )

    def test_do_chat_completion_http_error(self):
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.text = "Error message"
        mock_response.status_code = http.HTTPStatus.INTERNAL_SERVER_ERROR.value
        self.mock_post.return_value = mock_response

        with self.assertRaises(VeniceClientError) as context:
            self.client.do_chat_completion(self.messages)

        self.assertEqual(
            context.exception.message, "Venice API error: Error message"
        )
        self.assertEqual(
            context.exception.status_code, http.HTTPStatus.INTERNAL_SERVER_ERROR.value
        )
