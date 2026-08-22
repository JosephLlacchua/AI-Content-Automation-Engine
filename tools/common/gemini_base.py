import os
from typing import Any, Callable, Optional

from dotenv import load_dotenv
from google.genai import Client, errors
from pydantic import PrivateAttr
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from tools.common.base_model import BaseModelTool
from tools.common.messenger import Messenger

load_dotenv()


class GeminiUsage(BaseModelTool):
    model: str
    prompt_tokens: Optional[int] = None
    thoughts_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


class GeminiBase(BaseModelTool):
    _client: Client = PrivateAttr()

    @property
    def client(self) -> Client:
        return self._client

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            import json
            from pathlib import Path
            config_path = Path("config.json")
            if config_path.exists():
                try:
                    data = json.loads(config_path.read_text())
                    api_key = data.get("gemini_api_key")
                except Exception:
                    pass
        
        if not api_key:
            raise RuntimeError("❌ GEMINI_API_KEY is not defined in the environment or config.json")
        self._client = Client(api_key=api_key)

    @retry(
        wait=wait_fixed(60),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type((errors.ServerError, errors.ClientError)),
        before_sleep=lambda retry_state: Messenger.info(
            f"⏳ Esperando cuota de Gemini... Reintentando en 60s "
            f"(Intento {retry_state.attempt_number}/5)"
        ),
        reraise=True,
    )
    def _execute_with_retry(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """
        Executes a Gemini API call with a 60s retry on ServerError or 429 RateLimit/Quota exhaustion.
        """
        return func(*args, **kwargs)

    def _extract_usage(self, response: Any, model_name: str) -> GeminiUsage:
        usage_meta = getattr(response, "usage_metadata", None)
        usage = GeminiUsage(model=model_name)

        if usage_meta:
            usage.prompt_tokens = getattr(usage_meta, "prompt_token_count", None)
            usage.thoughts_tokens = getattr(usage_meta, "thoughts_token_count", None)
            usage.output_tokens = getattr(usage_meta, "candidates_token_count", None)
            usage.total_tokens = getattr(usage_meta, "total_token_count", None)

        if usage.total_tokens is not None:
            Messenger.usage(
                model=usage.model,
                prompt=usage.prompt_tokens or 0,
                thoughts=usage.thoughts_tokens or 0,
                output=usage.output_tokens or 0,
                total=usage.total_tokens
            )
        return usage
