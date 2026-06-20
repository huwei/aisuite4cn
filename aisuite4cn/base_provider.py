import openai
from aisuite4cn.provider import Provider

OPENAI_PARAMS = [
    "messages",
    "model",
    "audio",
    "response_format",
    "frequency_penalty",
    "function_call",
    "functions",
    "logit_bias",
    "logprobs",
    "max_completion_tokens",
    "max_tokens",
    "metadata",
    "modalities",
    "n",
    "parallel_tool_calls",
    "prediction",
    "presence_penalty",
    "prompt_cache_key",
    "reasoning_effort",
    "safety_identifier",
    "seed",
    "service_tier",
    "stop",
    "store",
    "stream",
    "stream_options",
    "temperature",
    "tool_choice",
    "tools",
    "top_logprobs",
    "top_p",
    "user",
    "verbosity",
    "timeout",
    "extra_headers",
    "extra_query",
    "extra_body"
]

RESPONSES_PARAMS = [
    "input",
    "model",
    "instructions",
    "background",
    "context_management",
    "conversation",
    "include",
    "max_output_tokens",
    "max_tool_calls",
    "metadata",
    "moderation",
    "parallel_tool_calls",
    "previous_response_id",
    "prompt",
    "prompt_cache_key",
    "prompt_cache_retention",
    "reasoning",
    "safety_identifier",
    "service_tier",
    "store",
    "stream",
    "stream_options",
    "temperature",
    "text",
    "tool_choice",
    "tools",
    "top_logprobs",
    "top_p",
    "truncation",
    "user",
    "timeout",
    "extra_headers",
    "extra_query",
    "extra_body"
]


class BaseProvider(Provider):
    """Base class for all openai compatible providers."""

    def __init__(self, base_url, **config):
        self.base_url = base_url
        self.config = dict(config)
        self._client = None
        self._async_client = None

    @property
    def client(self):
        """Getter for the OpenAI client."""
        if not self._client:
            self._client = openai.OpenAI(base_url=self.base_url, **self.config)
        return self._client

    @client.setter
    def client(self, value):
        """Setter for the OpenAI client."""
        self._client = value

    @property
    def async_client(self):
        """Getter for the asynchronous OpenAI client.

        Lazily initializes the AsyncOpenAI client if not already created.
        """
        if not self._async_client:
            self._async_client = openai.AsyncOpenAI(
                base_url=self.base_url,
                **self.config
            )
        return self._async_client

    @async_client.setter
    def async_client(self, value):
        """Setter for the asynchronous OpenAI client.

        Allows replacing the default client with a custom one.

        Args:
            value: An instance of openai.AsyncOpenAI or compatible client
        """
        self._async_client = value

    # ---- Chat Completions API ----

    def _prepare_chat_completions_call(self, model, messages, **kwargs):
        return model, messages, kwargs

    def chat_completions_create(self, model, messages, **kwargs):
        """Create a chat completion using the OpenAI API."""
        model, messages, new_kwargs = self._prepare_chat_completions_call(model, messages, **kwargs)
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            **self._compatible_with_openai_kwargs(new_kwargs)
        )

    def chat_completions_parse(self, model, messages, **kwargs):
        model, messages, new_kwargs = self._prepare_chat_completions_call(model, messages, **kwargs)
        return self.client.chat.completions.parse(
            model=model,
            messages=messages,
            **self._compatible_with_openai_kwargs(new_kwargs)
        )

    def chat_completions_stream(self, model, messages, **kwargs):
        model, messages, new_kwargs = self._prepare_chat_completions_call(model, messages, **kwargs)
        return self.client.chat.completions.stream(
            model=model,
            messages=messages,
            **self._compatible_with_openai_kwargs(new_kwargs)
        )

    async def async_chat_completions_create(self, model, messages, **kwargs):
        """Create a chat completion using the OpenAI API."""
        model, messages, new_kwargs = self._prepare_chat_completions_call(model, messages, **kwargs)
        return await self.async_client.chat.completions.create(
            model=model,
            messages=messages,
            **self._compatible_with_openai_kwargs(new_kwargs)
        )

    async def async_chat_completions_parse(self, model, messages, **kwargs):

        model, messages, new_kwargs = self._prepare_chat_completions_call(model, messages, **kwargs)
        return await self.async_client.chat.completions.parse(
            model=model,
            messages=messages,
            **self._compatible_with_openai_kwargs(new_kwargs)
        )

    def async_chat_completions_stream(self, model, messages, **kwargs):
        model, messages, new_kwargs = self._prepare_chat_completions_call(model, messages, **kwargs)
        return self.async_client.chat.completions.stream(
            model=model,
            messages=messages,
            **self._compatible_with_openai_kwargs(new_kwargs)
        )

    # ---- Embeddings API ----

    def embeddings_create(self, model, input, **kwargs):
        return self.client.embeddings.create(
            model=model,
            input=input,
            **kwargs
        )

    async def async_embeddings_create(self, model, input, **kwargs):
        return await self.async_client.embeddings.create(
            model=model,
            input=input,
            **kwargs
        )

    # ---- Responses API ----

    def _prepare_responses_call(self, model, input, **kwargs):
        return model, input, kwargs

    def responses_create(self, model, input, **kwargs):
        """Create a response using the OpenAI Responses API."""
        model, input, new_kwargs = self._prepare_responses_call(model, input, **kwargs)
        return self.client.responses.create(
            model=model,
            input=input,
            **self._compatible_with_responses_kwargs(new_kwargs)
        )

    def responses_parse(self, model, input, **kwargs):
        model, input, new_kwargs = self._prepare_responses_call(model, input, **kwargs)
        return self.client.responses.parse(
            model=model,
            input=input,
            **self._compatible_with_responses_kwargs(new_kwargs)
        )

    def responses_stream(self, model, input, **kwargs):
        model, input, new_kwargs = self._prepare_responses_call(model, input, **kwargs)
        return self.client.responses.stream(
            model=model,
            input=input,
            **self._compatible_with_responses_kwargs(new_kwargs)
        )

    async def async_responses_create(self, model, input, **kwargs):
        """Create a response using the OpenAI Responses API (async)."""
        model, input, new_kwargs = self._prepare_responses_call(model, input, **kwargs)
        return await self.async_client.responses.create(
            model=model,
            input=input,
            **self._compatible_with_responses_kwargs(new_kwargs)
        )

    async def async_responses_parse(self, model, input, **kwargs):
        model, input, new_kwargs = self._prepare_responses_call(model, input, **kwargs)
        return await self.async_client.responses.parse(
            model=model,
            input=input,
            **self._compatible_with_responses_kwargs(new_kwargs)
        )

    def async_responses_stream(self, model, input, **kwargs):
        model, input, new_kwargs = self._prepare_responses_call(model, input, **kwargs)
        return self.async_client.responses.stream(
            model=model,
            input=input,
            **self._compatible_with_responses_kwargs(new_kwargs)
        )

    # ---- Kwarg compatibility helpers ----

    @staticmethod
    def _compatible_with_openai_kwargs(kwargs: dict = None) -> dict:
        """Filter kwargs to only include OpenAI Chat Completions API compatible parameters.

        Non-standard params are moved into extra_body.
        """
        if not kwargs:
            return {}
        new_kwargs = dict(kwargs)
        new_extra_body = dict(kwargs.get("extra_body", {}))
        for k, v in kwargs.items():
            if k not in OPENAI_PARAMS:
                new_extra_body[k] = new_kwargs.pop(k)
        if new_extra_body:
            new_kwargs["extra_body"] = new_extra_body
        return new_kwargs

    @staticmethod
    def _compatible_with_responses_kwargs(kwargs: dict = None) -> dict:
        """Filter kwargs to only include OpenAI Responses API compatible parameters.

        Non-standard params are moved into extra_body.
        """
        if not kwargs:
            return {}
        new_kwargs = dict(kwargs)
        new_extra_body = dict(kwargs.get("extra_body", {}))
        for k, v in kwargs.items():
            if k not in RESPONSES_PARAMS:
                new_extra_body[k] = new_kwargs.pop(k)
        if new_extra_body:
            new_kwargs["extra_body"] = new_extra_body
        return new_kwargs
