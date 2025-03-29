from typing import Any, Dict, List, Optional

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import Field, SecretStr

from services.venice_client import VeniceClient


class ChatVeniceAI(BaseChatModel):

    model_name: str = Field(alias="model")
    temperature: float = 0
    max_tokens: Optional[int] = None
    timeout: Optional[int] = None
    stop: Optional[List[str]] = None
    max_retries: int = 2
    api_key: SecretStr

    def _init_venice_client(self) -> VeniceClient:
        return VeniceClient(
            model=self.model_name,
            api_key=self.api_key.get_secret_value(),
            temperature=self.temperature,
        )

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        
        client = self._init_venice_client()

        response = client.do_chat_completion(
            messages=self._get_chat_messages(messages),
        )

        message = AIMessage(
            content=response["choices"][0]["message"]["content"],
            usage_metadata={
                "input_tokens": response["usage"]["prompt_tokens"],
                "output_tokens": response["usage"]["completion_tokens"],
                "total_tokens": response["usage"]["total_tokens"],
            }
        )

        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])
    
    def _get_chat_messages(self, messages: List[BaseMessage]) -> List[Dict[str, Any]]:
        role_mapping = {
            "system": "system",
            "human": "user",
            "ai": "assistant",
        }
        return [{
            "role": role_mapping[message.type],
            "content": message.content,
        } for message in messages]
