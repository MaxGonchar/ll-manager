import http
from pprint import pprint

import requests


class VeniceClientError(Exception):
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class VeniceClient:
    def __init__(self, model: str, api_key: str, temperature: float = 0):
        self.base_url = "https://api.venice.ai/api/v1"
        self.model = model
        self.temperature = temperature
        self.api_key = api_key
    
    @property
    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def do_chat_completion(self, messages: list[dict], timeout: int = 60) -> dict:
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature
        }
        # pprint(payload)
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=timeout)
        except requests.exceptions.Timeout:
            raise VeniceClientError("Request timed out", http.HTTPStatus.REQUEST_TIMEOUT.value)

        if not response.ok:
            raise VeniceClientError(f"Venice API error: {response.text}", response.status_code)
        
        return response.json()
