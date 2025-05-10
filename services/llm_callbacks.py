import logging
from typing import Any
from uuid import UUID
from pathlib import Path

from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult


# TODO: don't log when testing
# TODO: Error in ModelCallbackHandler.on_llm_end callback: KeyError('metadata') during testing
class ModelCallbackHandler(BaseCallbackHandler):
    def __init__(self) -> None:
        super().__init__()
        self._init_logger()

    def _init_logger(self) -> None:
        """Initialize the logger."""
        self.logger = logging.getLogger(__name__)
        if not self.logger.hasHandlers():
            log_file_path = Path.cwd() / "logs/model_callback.log"
            log_file_path.parent.mkdir(parents=True, exist_ok=True)
            handler = logging.FileHandler(log_file_path)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

    def on_llm_start(
        self,
        serialized: dict[str, Any],
        prompts: list[str],
        run_id: UUID,
        **kwargs: Any,
    ) -> Any:
        """Run when LLM starts running."""
        self.logger.info(
            f"LLM started with run_id: {run_id}, run_type: {kwargs['metadata'].get('run_type', 'undefined')}, prompts: {prompts}"
        )

    def on_llm_end(
        self, response: LLMResult, run_id: UUID, **kwargs: Any
    ) -> Any:
        """Run when LLM ends running."""
        self.logger.info(
            f"LLM ended with run_id: {run_id}, run_type: {kwargs['metadata'].get('run_type', 'undefined')}, response: {response.generations}"
        )
