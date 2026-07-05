from __future__ import annotations

from .config import LLMConfig


class OpenAICompatibleClient:
    """Thin wrapper around an OpenAI-compatible chat completions endpoint.

    Retries for rate limits, timeouts, connection errors, and transient server
    errors are delegated to the OpenAI SDK (``max_retries`` with exponential
    backoff). JSON mode is attempted first; if the endpoint rejects
    ``response_format`` with a BadRequestError, the client falls back to plain
    completions and remembers that for the rest of the run. Other errors
    (authentication, exhausted retries) propagate to the caller so they can be
    reported per chunk/agent instead of being silently retried.
    """

    def __init__(self, config: LLMConfig):
        try:
            import openai
        except ImportError as exc:
            raise RuntimeError(
                "Install the OpenAI Python SDK first: pip install openai"
            ) from exc

        self.config = config
        self._openai = openai
        self._supports_json_mode = True
        self._client = openai.OpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout_seconds,
            max_retries=config.max_retries,
        )

    def complete_json(self, messages: list[dict[str, str]]) -> str:
        if self._supports_json_mode:
            try:
                return self._create(messages, json_mode=True)
            except self._openai.BadRequestError:
                # Endpoint rejected response_format; skip JSON mode from now on.
                self._supports_json_mode = False
        return self._create(messages, json_mode=False)

    def _create(self, messages: list[dict[str, str]], *, json_mode: bool) -> str:
        kwargs = {"response_format": {"type": "json_object"}} if json_mode else {}
        response = self._client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            **kwargs,
        )
        content = response.choices[0].message.content
        return content or '{"findings": []}'
